#!/usr/bin/env bash
# Build a Joern CPG from a source directory and export one PDG (.dot) per method.
# Usage: tools/joern/export_pdg.sh <source_dir> <out_dir> [language]
#   language defaults to pythonsrc (others: javasrc, c, csharpsrc, jssrc, ...)
set -euo pipefail

SRC="${1:?source dir required}"
OUT="${2:?output dir required}"
LANG="${3:-pythonsrc}"

export JAVA_HOME="${JAVA_HOME:-/opt/homebrew/opt/openjdk@21/libexec/openjdk.jdk/Contents/Home}"
JOERN_CLI="${JOERN_CLI:-$HOME/tools/joern/joern-cli}"

mkdir -p "$OUT"
"$JOERN_CLI/joern-parse" "$SRC" --language "$LANG" -o "$OUT/cpg.bin"
rm -rf "$OUT/pdg"  # joern-export refuses to write into an existing dir
"$JOERN_CLI/joern-export" "$OUT/cpg.bin" --repr pdg --out "$OUT/pdg"
echo "PDGs written to $OUT/pdg"
