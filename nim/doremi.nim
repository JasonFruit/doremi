import os, lex, parse, drmcommon, drmxml, xmltree

var tokens: seq[Token] = tokenize(readFile(paramStr(1)))
var tune = parse(tokens)

setNoteheads(nhSacredHarp)

echo """<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">"""

echo xml(tune, paramStr(2))
