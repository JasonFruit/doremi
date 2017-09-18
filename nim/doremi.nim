import os, lex, parse, drmcommon, drmxml, xmltree

var tokens: seq[Token] = tokenize(readFile(paramStr(1)))
var tune = parse(tokens)

echo xmlHeader & musicXmlDoctype
echo xml(tune, paramStr(2))
