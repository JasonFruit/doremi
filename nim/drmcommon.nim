type
 Token* = object
   content*: string
   start*, length*: int

proc newToken*(start: int = 0): Token =
  result.content = ""
  result.start = start

const syllables*: seq[string] = @["do", "di", "ra", "re", "ri", "me", 
                                 "mi", "fa", "fi", "se", "sol", "si",
                                 "le", "la", "li", "te", "ti", "r"]

const tuneKeywords*: seq[string] = @["title", "subtitle", "composer", "key",
                                    "time", "partial", "voices"]

const voiceKeywords*: seq[string] = @["name", "octave", "lyrics", "time"]

const keyQualities*: seq[string] = @["major", "minor"]

const tonics*: seq[string] = @["c", "ces", "cis", "d", "des", "dis", 
                              "e", "es", "eis", "f", "fes", "fis",
                              "g", "ges", "gis", "a", "aes", "ais",
                              "b", "bes", "bis"]

const white*: string = " \n\t\v"
const brackets*: string = "[]{}"
const assigners*: string = "="
const octaveChanges*: string = "+-"
const otherModifiers*: seq[string] = @["slur", "tie", "fermata"]
const barlines*: seq[string] = @["||", "|.", ":|", "|:"]
const durations*: seq[string] = @["1", "2", "4", "8", "16", "32"]

const delimiters*: string = white & brackets & assigners

const quote*: char = '"'

proc isTuneKeyword*(s: string): bool =
  return tuneKeywords.contains(s & ":")

proc isVoiceKeyword*(s: string): bool =
  return voiceKeywords.contains(s & ":")

proc syllableDegree*(syll: string): int =
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
