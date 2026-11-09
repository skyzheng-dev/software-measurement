// Export per-function facts from a Joern CPG built over one-function-per-file sources.
// For every top-level function (fullName "<id>.py:<module>.<name>") it writes:
//   <outDir>/pdg/<id>.dot      the function's PDG (DDG + CDG edges), named by file id
//   <outDir>/facts.jsonl       one JSON line: id, name, params, calls (name + code), returns, nested defs
// Usage: joern --script tools/joern/function_facts.sc --param cpgFile=<cpg.bin> --param outDir=<dir>
// Called by scripts/07_extract_joern.py.

import java.nio.file.{Files, Paths}

@main def exec(cpgFile: String, outDir: String) = {
  importCpg(cpgFile)
  val pdgDir = Paths.get(outDir, "pdg")
  Files.createDirectories(pdgDir)
  val TopLevel = """^(.+)\.py:<module>\.([^.]+)$""".r
  val writer = Files.newBufferedWriter(Paths.get(outDir, "facts.jsonl"))
  var n = 0
  cpg.method.isExternal(false).l.foreach { m =>
    m.fullName match {
      case TopLevel(id, name) =>
        Files.writeString(pdgDir.resolve(s"$id.dot"), m.dotPdg.headOption.getOrElse(""))
        val calls = m.call.l.map(c => ujson.Obj("name" -> c.name, "code" -> c.code.take(200)))
        val nested = cpg.method.fullName(java.util.regex.Pattern.quote(m.fullName) + "\\..*").size
        val row = ujson.Obj(
          "id" -> id,
          "name" -> name,
          "params" -> ujson.Arr.from(m.parameter.l.sortBy(_.index).map(p => ujson.Str(p.name))),
          "returns" -> m.ast.isReturn.size,
          "nested_defs" -> nested,
          "calls" -> ujson.Arr.from(calls)
        )
        writer.write(ujson.write(row))
        writer.newLine()
        n += 1
      case _ =>
    }
  }
  writer.close()
  println(s"wrote facts for $n functions to $outDir")
}
