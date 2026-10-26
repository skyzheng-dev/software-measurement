# Joern (PDG extraction)

Joern is installed outside the repo at `~/tools/joern/joern-cli` (needs Java 21).

```bash
tools/joern/export_pdg.sh <source_dir> data/derived/<name>          # Python
tools/joern/export_pdg.sh <source_dir> data/derived/<name> javasrc  # Java
```

This writes `cpg.bin` and `pdg/*.dot` (one PDG per method). Edges are labeled
`DDG: <var>` (data dependence) or `CDG:` (control dependence). Files for external
calls such as `print` or `execute` are empty stubs and should be skipped.

Interactive shell: `~/tools/joern/joern-cli/joern`, then `importCpg("data/derived/<name>/cpg.bin")`
and `cpg.method.name("register_user").dotPdg.l`.
