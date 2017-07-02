import strutils, sequtils, parseutils

type
 Token* = object
   content: string
   start, length: int

proc newToken(start: int = 0): Token =
  result.content = ""
  result.start = start

const syllables: seq[string] = @["do", "di", "ra", "re", "ri", "me", 
                                 "mi", "fa", "fi", "se", "sol", "si",
                                 "le", "la", "li", "te", "ti"]

const tuneKeywords: seq[string] = @["title", "subtitle", "composer", "key",
                                    "time", "partial", "voices"]

const voiceKeywords: seq[string] = @["name", "octave", "lyrics", "time"]

const keyQualities: seq[string] = @["major", "minor"]

const tonics: seq[string] = @["c", "ces", "cis", "d", "des", "dis", 
                              "e", "es", "eis", "f", "fes", "fis",
                              "g", "ges", "gis", "a", "aes", "ais",
                              "b", "bes", "bis"]

const white: string = " \n\t\v"
const brackets: string = "[]{}"

const delimiters: string = white & brackets

const quote: char = '"'

proc isTuneKeyword(s: string): bool =
  return tuneKeywords.contains(s & ":")

proc isVoiceKeyword(s: string): bool =
  return voiceKeywords.contains(s & ":")

proc syllableDegree(syll: string): int =
  case syll:
    of "do", "di":
      result = 0
    of "ra", "re", "ri":
      result = 1
    of "me", "mi":
      result = 2
    of "fa", "fi":
      result = 3
    of "se", "sol", "si":
      result = 4
    of "le", "la", "li":
      result = 5
    of "te", "ti":
      result = 6
    else:
      result = -1

proc tokenize*(s: string): seq[Token] =
  var tokenStart: Natural = 0
  var cur: Token = newToken()
  var inString = false
  result = newSeq[Token](0)
  for pos in 0..high(s):
    if inString:
      cur.content = cur.content & $s[pos]

      if s[pos] == quote and s[pos-1] != '\\':
        cur.length = pos - cur.start
        result.add(cur)
        cur = newToken(pos + 1)
        inString = false

    elif delimiters.contains(s[pos]):
      if brackets.contains(s[pos]):
        if cur.content != "":
          cur.length = pos - cur.start
          result.add(cur)
          cur = newToken(pos)
        cur.content = $s[pos]
        cur.length = pos - cur.start
        result.add(cur)
        cur = newToken(pos + 1)
      else:
        if cur.content == "":
          cur.start = pos + 1
        else:
          cur.length = pos - cur.start
          result.add(cur)
          cur = newToken(pos + 1)
    else:
      if s[pos] == quote:
        inString = true
      cur.content = cur.content & $s[pos]

var code: string
var file: File

code = readFile("/home/jason/Code/doremi/tunes/old-hundred.drm")

var tokens: seq[Token] = tokenize(code)

for tkn in tokens: 
  echo tkn.content, ": ", tkn.start
