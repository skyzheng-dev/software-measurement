"""Step 7: per-function structural features from Joern program dependence graphs (PDGs).

Needs the one-function-per-file sources written by step 6 (data/derived/functions/<dataset>/).
For each dataset (COSMIC, MicroM):
  1. builds a Joern CPG over the folder (tools/joern/export_pdg.sh's joern-parse step);
  2. runs tools/joern/function_facts.sc, which writes data/derived/joern/<dataset>/pdg/<id>.dot
     (kept for later graph models) and facts.jsonl (params, returns, nested defs, calls);
  3. turns those into numeric features (prefix `jn_`) in data/derived/features/joern_<dataset>.csv.

Feature groups:
  - PDG shape: nodes, data-dependence (DDG) edges, control-dependence (CDG) edges, distinct
    variables carried by DDG edges, DDG edges leaving parameters (how much input is used).
  - Interface: parameters (without self/cls), return statements, yields, nested defs.
  - Calls: number of (non-operator) calls and distinct callees.
  - Heuristic call categories: calls whose name contains a read-, write-, exit- or entry-like
    word (lists below), plus SQL verbs in string literals. These are keyword heuristics meant to
    approximate COSMIC data-movement candidates, not an implementation of the COSMIC rules.

Run: uv run python scripts/07_extract_joern.py
"""

import ast
import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
IN = ROOT / "data" / "derived" / "repaired"
FUNCS = ROOT / "data" / "derived" / "functions"
JOERN_OUT = ROOT / "data" / "derived" / "joern"
OUT = ROOT / "data" / "derived" / "features"
FACTS_SCRIPT = ROOT / "tools" / "joern" / "function_facts.sc"

JOERN_CLI = Path(os.environ.get("JOERN_CLI", Path.home() / "tools" / "joern" / "joern-cli"))
JAVA_HOME = os.environ.get("JAVA_HOME", "/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home")

DATASETS = ["cosmic", "microm"]

# Callee-name words for the heuristic categories. A call counts toward a category when one of the
# words in its name (split on _ and camelCase, lowercased) is in the set.
READ_WORDS = {
    "get", "read", "readline", "readlines", "fetch", "fetchone", "fetchall", "fetchmany", "query",
    "select", "load", "loads", "find", "search", "filter", "lookup", "retrieve", "download",
    "recv", "receive", "scan", "exists", "count", "open", "list", "glob", "listdir", "walk",
}
WRITE_WORDS = {
    "write", "writelines", "save", "insert", "update", "delete", "remove", "commit", "put",
    "store", "upload", "dump", "dumps", "flush", "create", "set", "add", "mkdir", "makedirs",
    "unlink", "rmtree", "rename", "move", "copy", "persist", "upsert", "destroy", "drop",
}
EXIT_WORDS = {
    "print", "log", "info", "debug", "warning", "warn", "error", "exception", "critical",
    "send", "sendall", "emit", "render", "respond", "response", "jsonify", "display", "show",
    "echo", "notify", "publish", "reply", "redirect", "abort", "plot", "savefig", "post",
}
ENTRY_WORDS = {"input", "raw_input", "parse_args", "argv", "getenv", "environ", "prompt", "listen", "accept"}
SQL_RE = {verb: re.compile(rf"\b{verb}\b", re.IGNORECASE) for verb in ["select", "insert", "update", "delete"]}

DOT_NODE = re.compile(r'^"(\d+)" \[label = <([^,>]+),', re.MULTILINE)
DOT_EDGE = re.compile(r'^\s*"(\d+)" -> "(\d+)"\s+\[ label = "(DDG|CDG): ?(.*)"\]', re.MULTILINE)


def words(name):
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    return {w for w in name.lower().split("_") if w}


def run_joern(src, out):
    env = {**os.environ, "JAVA_HOME": JAVA_HOME}
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    cpg = out / "cpg.bin"
    subprocess.run([JOERN_CLI / "joern-parse", src, "--language", "pythonsrc", "-o", cpg],
                   env=env, check=True, capture_output=True)
    res = subprocess.run([JOERN_CLI / "joern", "--script", FACTS_SCRIPT,
                          "--param", f"cpgFile={cpg}", "--param", f"outDir={out}"],
                         env=env, check=True, capture_output=True, text=True)
    print("   ", [line for line in res.stdout.splitlines() if line.startswith("wrote")])


def pdg_features(dot):
    kinds = dict(DOT_NODE.findall(dot))
    edges = DOT_EDGE.findall(dot)
    ddg = [e for e in edges if e[2] == "DDG"]
    return {
        "jn_pdg_nodes": len(kinds),
        "jn_ddg_edges": len(ddg),
        "jn_cdg_edges": sum(e[2] == "CDG" for e in edges),
        "jn_ddg_vars": len({e[3] for e in ddg}),
        "jn_param_ddg_out": sum(kinds.get(e[0]) == "PARAM" for e in ddg),
    }


def fact_features(fact, source):
    calls = [c for c in fact["calls"] if not c["name"].startswith("<operator>")]
    call_words = [words(c["name"]) for c in calls]
    feats = {
        "jn_params": sum(p not in ("self", "cls") for p in fact["params"]),
        "jn_returns": fact["returns"],
        # Joern's Python frontend does not model yield as a call, so count it from the source.
        "jn_yields": sum(isinstance(n, (ast.Yield, ast.YieldFrom)) for n in ast.walk(ast.parse(source))),
        "jn_nested_defs": fact["nested_defs"],
        "jn_calls": len(calls),
        "jn_unique_callees": len({c["name"] for c in calls}),
    }
    for cat, vocab in [("read", READ_WORDS), ("write", WRITE_WORDS), ("exit", EXIT_WORDS), ("entry", ENTRY_WORDS)]:
        feats[f"jn_calls_{cat}"] = sum(bool(w & vocab) for w in call_words)
    literals = " ".join(string_literals(source))
    for verb, rx in SQL_RE.items():
        feats[f"jn_sql_{verb}"] = len(rx.findall(literals))
    return feats


def string_literals(source):
    """All string constants in the function except its docstring (prose would match SQL verbs)."""
    tree = ast.parse(source)
    func = tree.body[0]
    doc = ast.get_docstring(func, clean=False) if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)) else None
    skip = func.body[0].value if doc is not None else None
    return [n.value for n in ast.walk(tree)
            if isinstance(n, ast.Constant) and isinstance(n.value, str) and n is not skip]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for name in DATASETS:
        df = pd.read_csv(IN / f"code_{name}_repaired.csv")
        df = df[df["usable"]].set_index("id")
        src = FUNCS / name
        if not src.exists():
            raise SystemExit(f"{src} missing: run scripts/06_extract_understand.py first")
        out = JOERN_OUT / name
        print(f"{name}: {len(df)} usable functions")
        run_joern(src, out)
        rows = []
        for line in (out / "facts.jsonl").read_text().splitlines():
            fact = json.loads(line)
            if fact["id"] not in df.index or fact["name"] != df.at[fact["id"], "func_name"].split(".")[-1]:
                continue
            dot = (out / "pdg" / f"{fact['id']}.dot").read_text()
            rows.append({"id": fact["id"], **pdg_features(dot),
                         **fact_features(fact, df.at[fact["id"], "code_restored"])})
        feats = pd.DataFrame(rows).drop_duplicates("id")
        missing = sorted(set(df.index) - set(feats["id"]))
        print(f"    features for {len(feats)}/{len(df)} functions, {feats.shape[1] - 1} features")
        if missing:
            print(f"    missing ({len(missing)}): {missing[:10]}{' ...' if len(missing) > 10 else ''}")
        feats.to_csv(OUT / f"joern_{name}.csv", index=False)


if __name__ == "__main__":
    main()
