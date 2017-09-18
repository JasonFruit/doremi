import tables, unicode

type Noteheads* = enum nhAikin, nhSacredHarp, nhRound, nhDefault
type Clefs* = enum clfTreble, clfAlto, clfTenor, clfBass, clfOctaveTreble

type
 Token* = object
   content*: string
   start*, length*: int

type
  InvalidSyllableError* = object of Exception

type 
  InvalidKeyError* = object of Exception

type
  FixedPitch* = object
    name*: string
    alteration*: int

proc `$`(pitch: FixedPitch): string =
  result = pitch.name

  if pitch.alteration < 0:
    for i in pitch.alteration..(-1):
     result = result & "b"
  elif pitch.alteration > 0:
    for i in 1..pitch.alteration:
      result = result & "#"

proc initFixedPitch(name: string, alteration: int): FixedPitch =
  result.name = name
  result.alteration = alteration

type
  KeysTable* = Table[string, Table[string, FixedPitch]]

proc newToken*(start: int = 0): Token =
  result.content = ""
  result.start = start

const shortSyllables*: seq[string] = @["d", "r", "m", "f", "s", "l", "t"]

proc longSyllable*(short: string): string =
  case short:
    of "d":
      result = "do"
    of "r":
      result = "re"
    of "m":
      result = "mi"
    of "f":
      result = "fa"
    of "s":
      result = "sol"
    of "l":
      result = "la"
    of "t":
      result = "ti"
    else:
      raise newException(InvalidSyllableError, "Invalid syllable: '" & short & "'.")

const syllables*: seq[string] = @["do", "di", "ra", "re", "ri", "me", 
                                 "mi", "fa", "fi", "se", "sol", "si",
                                 "le", "la", "li", "te", "ti", "r"]

var keys*: KeysTable = initTable[string, Table[string, FixedPitch]]()

proc addKey(name: string, notes: seq[FixedPitch]) =
  keys[name] = initTable[string, FixedPitch]()
  for i in notes.low..notes.high:
    keys[name][syllables[i]] = notes[i]

addKey("c",
       @[initFixedPitch("C", 0),
         initFixedPitch("C", 1),
         initFixedPitch("D", -1),
         initFixedPitch("D", 0),
         initFixedPitch("D", 1),
         initFixedPitch("E", -1),
         initFixedPitch("E", 0),
         initFixedPitch("F", 0),
         initFixedPitch("F", 1),
         initFixedPitch("G", -1),
         initFixedPitch("G", 0),
         initFixedPitch("G", 1),
         initFixedPitch("A", -1),
         initFixedPitch("A", 0),
         initFixedPitch("A", 1),
         initFixedPitch("B", -1),
         initFixedPitch("B", 0)])

addKey("d",
       @[initFixedPitch("D", 0),
         initFixedPitch("D", 1),
         initFixedPitch("E", -1),
         initFixedPitch("E", 0),
         initFixedPitch("E", 1),
         initFixedPitch("F", 0),
         initFixedPitch("F", 1),
         initFixedPitch("G", 0),
         initFixedPitch("G", 1),
         initFixedPitch("A", -1),
         initFixedPitch("A", 0),
         initFixedPitch("A", 1),
         initFixedPitch("B", -1),
         initFixedPitch("B", 0),
         initFixedPitch("B", 1),
         initFixedPitch("C", 0),
         initFixedPitch("C", 1)])

addKey("des",
       @[initFixedPitch("D", -1),
         initFixedPitch("D", 0),
         initFixedPitch("E", -2),
         initFixedPitch("E", -1),
         initFixedPitch("E", 0),
         initFixedPitch("F", -1),
         initFixedPitch("F", 0),
         initFixedPitch("G", -1),
         initFixedPitch("G", 0),
         initFixedPitch("A", -2),
         initFixedPitch("A", -1),
         initFixedPitch("A", 0),
         initFixedPitch("B", -2),
         initFixedPitch("B", -1),
         initFixedPitch("B", 0),
         initFixedPitch("C", -1),
         initFixedPitch("C", 0)])

addKey("es",
       @[initFixedPitch("E", -1),
         initFixedPitch("E", 0),
         initFixedPitch("F", -1),
         initFixedPitch("F", 0),
         initFixedPitch("F", 1),
         initFixedPitch("G", -1),
         initFixedPitch("G", 0),
         initFixedPitch("A", -1),
         initFixedPitch("A", 0),
         initFixedPitch("B", -2),
         initFixedPitch("B", -1),
         initFixedPitch("B", 0),
         initFixedPitch("C", -1),
         initFixedPitch("C", 0),
         initFixedPitch("C", 1),
         initFixedPitch("D", -1),
         initFixedPitch("D", 0)])

addKey("e",
       @[initFixedPitch("E", 0),
         initFixedPitch("E", 1),
         initFixedPitch("F", 0),
         initFixedPitch("F", 1),
         initFixedPitch("F", 2),
         initFixedPitch("G", 0),
         initFixedPitch("G", 1),
         initFixedPitch("A", 0),
         initFixedPitch("A", 1),
         initFixedPitch("B", -1),
         initFixedPitch("B", 0),
         initFixedPitch("B", 1),
         initFixedPitch("C", 0),
         initFixedPitch("C", 1),
         initFixedPitch("C", 2),
         initFixedPitch("D", 0),
         initFixedPitch("D", 1)])

addKey("f",
       @[initFixedPitch("F", 0),
         initFixedPitch("F", 1),
         initFixedPitch("G", -1),
         initFixedPitch("G", 0),
         initFixedPitch("G", 1),
         initFixedPitch("A", -1),
         initFixedPitch("A", 0),
         initFixedPitch("B", -1),
         initFixedPitch("B", 0),
         initFixedPitch("C", -1),
         initFixedPitch("C", 0),
         initFixedPitch("C", 1),
         initFixedPitch("D", -1),
         initFixedPitch("D", 0),
         initFixedPitch("D", 1),
         initFixedPitch("E", -1),
         initFixedPitch("E", 0)])

addKey("fis",
       @[initFixedPitch("F", 1), #do
         initFixedPitch("F", 2), #di
         initFixedPitch("G", 0), #ra
         initFixedPitch("G", 1), #re
         initFixedPitch("G", 2), #ri
         initFixedPitch("A", 0), #me
         initFixedPitch("A", 1), #mi
         initFixedPitch("B", 0), #fa
         initFixedPitch("B", 1), #fi
         initFixedPitch("C", 0), #se
         initFixedPitch("C", 1), #sol
         initFixedPitch("C", 2), #si
         initFixedPitch("D", 0), #le
         initFixedPitch("D", 1), #la
         initFixedPitch("D", 2), #li
         initFixedPitch("E", 0), #te
         initFixedPitch("E", 1)]) #ti

addKey("ges",
       @[initFixedPitch("G", -1), #do
         initFixedPitch("G", 0), #di
         initFixedPitch("A", -2), #ra
         initFixedPitch("A", -1), #re
         initFixedPitch("A", 0), #ri
         initFixedPitch("B", -2), #me
         initFixedPitch("B", -1), #mi
         initFixedPitch("C", -1), #fa
         initFixedPitch("C", 0), #fi
         initFixedPitch("D", -2), #se
         initFixedPitch("D", -1), #sol
         initFixedPitch("D", 0), #si
         initFixedPitch("E", -2), #le
         initFixedPitch("E", -1), #la
         initFixedPitch("E", 0), #li
         initFixedPitch("F", -1), #te
         initFixedPitch("F", 0)]) #ti

addKey("g",
       @[initFixedPitch("G", 0), #do
         initFixedPitch("G", 1), #di
         initFixedPitch("A", -1), #ra
         initFixedPitch("A", 0), #re
         initFixedPitch("A", 1), #ri
         initFixedPitch("B", -1), #me
         initFixedPitch("B", 0), #mi
         initFixedPitch("C", 0), #fa
         initFixedPitch("C", 1), #fi
         initFixedPitch("D", -1), #se
         initFixedPitch("D", 0), #sol
         initFixedPitch("D", 1), #si
         initFixedPitch("E", -1), #le
         initFixedPitch("E", 0), #la
         initFixedPitch("E", 1), #li
         initFixedPitch("F", 0), #te
         initFixedPitch("F", 1)]) #ti

addKey("aes",
       @[initFixedPitch("A", -1), #do
         initFixedPitch("A", 0), #di
         initFixedPitch("B", -2), #ra
         initFixedPitch("B", -1), #re
         initFixedPitch("B", 0), #ri
         initFixedPitch("C", -1), #me
         initFixedPitch("C", 0), #mi
         initFixedPitch("D", -1), #fa
         initFixedPitch("D", 0), #fi
         initFixedPitch("E", -2), #se
         initFixedPitch("E", -1), #sol
         initFixedPitch("E", 0), #si
         initFixedPitch("F", -1), #le
         initFixedPitch("F", 0), #la
         initFixedPitch("F", 1), #li
         initFixedPitch("G", -1), #te
         initFixedPitch("G", 0)]) #ti

addKey("a",
       @[initFixedPitch("A", 0), #do
         initFixedPitch("A", 1), #di
         initFixedPitch("B", -1), #ra
         initFixedPitch("B", 0), #re
         initFixedPitch("B", 1), #ri
         initFixedPitch("C", 0), #me
         initFixedPitch("C", 1), #mi
         initFixedPitch("D", 0), #fa
         initFixedPitch("D", 1), #fi
         initFixedPitch("E", -1), #se
         initFixedPitch("E", 0), #sol
         initFixedPitch("E", 1), #si
         initFixedPitch("F", 0), #le
         initFixedPitch("F", 1), #la
         initFixedPitch("F", 2), #li
         initFixedPitch("G", 0), #te
         initFixedPitch("G", 1)]) #ti

addKey("bes",
       @[initFixedPitch("B", -1), #do
         initFixedPitch("B", 0), #di
         initFixedPitch("C", -1), #ra
         initFixedPitch("C", 0), #re
         initFixedPitch("C", 1), #ri
         initFixedPitch("D", -1), #me
         initFixedPitch("D", 0), #mi
         initFixedPitch("E", -1), #fa
         initFixedPitch("E", 0), #fi
         initFixedPitch("F", -1), #se
         initFixedPitch("F", 0), #sol
         initFixedPitch("F", 1), #si
         initFixedPitch("G", -1), #le
         initFixedPitch("G", 0), #la
         initFixedPitch("G", 1), #li
         initFixedPitch("A", -1), #te
         initFixedPitch("A", 0)]) #ti

addKey("b",
       @[initFixedPitch("B", 0), #do
         initFixedPitch("B", 1), #di
         initFixedPitch("C", 0), #ra
         initFixedPitch("C", 1), #re
         initFixedPitch("C", 2), #ri
         initFixedPitch("D", 0), #me
         initFixedPitch("D", 1), #mi
         initFixedPitch("E", 0), #fa
         initFixedPitch("E", 1), #fi
         initFixedPitch("F", 0), #se
         initFixedPitch("F", 1), #sol
         initFixedPitch("F", 2), #si
         initFixedPitch("G", 0), #le
         initFixedPitch("G", 1), #la
         initFixedPitch("G", 2), #li
         initFixedPitch("A", 0), #te
         initFixedPitch("A", 1)]) #ti

proc writeScales() =
  for ki in @["c", "d", "des", "es", "e", "f", "fis", "ges", "g", "aes", "a", "bes", "b"]:
    echo ki & ":"
    var key = keys[ki]
    for dgr in @["do", "re", "mi", "fa", "sol", "la", "ti"]:
      write(stdout, key[dgr])
      write(stdout, " ")
    echo ""
    

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

proc rootSyllable*(syll: string): string =
  return longSyllable($syll[0])

proc aikenNotehead*(syll: string): string =
  result = rootSyllable(syll)
  if result == "sol":
    result = "so"

proc sacredHarpNotehead*(syll: string): string =
  case rootSyllable(syll):
    of "do", "fa":
      result = "fa"
    of "re", "sol":
      result = "so"
    of "mi", "la":
      result = "la"
    of "ti":
      result = "mi"

proc syllableToPitch*(syllable: string, key: string): FixedPitch =
  return keys[key][syllable]

proc durationToNoteType*(duration: int): string = 
  case duration:
    of -2:
      result = "maxima"
    of -1:
      result = "long"
    of 0:
      result = "breve"
    of 1:
      result = "whole"
    of 2:
      result = "half"
    of 4:
      result = "quarter"
    of 8:
      result = "eighth"
    of 16:
      result = "16th"
    of 32:
      result = "32nd"
    of 64:
      result = "64th"
    of 128:
      result = "128th"
    else:
      result = "mu"

proc keyOctaveOffset*(key, syllable: string): int =
  var pastC: string
  for note in "cdefgab":
    if note == key.toLower()[0]:
      return 0
    elif $note == keys[key][syllable].name.toLower():
      return 1

proc keyToFifths*(key: string): int =
  var keys = @["ges", "des", "aes", "es", "bes", "f", 
               "c", "g", "d", "a", "e", "b", "fis"]

  return keys.find(key.toLower()) - keys.find("c")
