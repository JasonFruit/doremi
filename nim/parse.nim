import drmcommon, lex, strutils

type Keys = enum kMajor, kMinor

type ParseError* = object of Exception

type
 TimeSignature* = object
    top, bottom: int

proc `$`(ts: TimeSignature): string =
  return $ts.top & "/" & $ts.bottom

type 
  VoiceObject* = ref object of RootObj
    
type
  Note* = ref object of VoiceObject
    syllable*: string
    duration*: int
    modifiers*: seq[string]

type
  TimeSignatureChange* = ref object of VoiceObject
    newTime*: TimeSignature

type 
  BarLine* = ref object of VoiceObject
    representation*: string
    
type
  Voice* = ref object of RootObj
    content*: seq[VoiceObject]
    name*, lyrics*: string
    octave*: int
    time*: TimeSignature

type
  Tune* = object
    title*, subtitle*, composer*: string
    key*: Keys
    time*: TimeSignature
    partial*: int
    voices*: seq[Voice]
    
type Keyword = string

type 
  Form = ref object of RootObj

type
  InvalidForm = ref object of Form

type
  DefinitionForm = ref object of Form
    keyword: string
    
type
  IntDefinitionForm = ref object of DefinitionForm
    value: int

type
  TimeSignatureDefinitionForm = ref object of DefinitionForm
    top, bottom: int

type
  StringDefinitionForm = ref object of DefinitionForm
    value: string

type
  KeywordDefinitionForm = ref object of DefinitionForm
    value: Keyword

type
  ParseResult = object
    form: Form
    consumedTokens: int

# a token has content, start, and length

proc parseAssignment(tokens: seq[Token],
                     start: int): ParseResult =
  var form: Form

  if start + 2 >= tokens.high:
    return ParseResult(form: InvalidForm(),
                       consumedTokens: 0)
    
  elif assigners.contains(tokens[start + 1].content):

    if Digits.contains(tokens[start + 2].content[0]) or tokens[start + 2].content[0] == '-':
      if tokens[start + 2].content.contains('/'):
        var top, bottom: int
        top = parseInt(tokens[start + 2].content.split("/")[0])
        bottom = parseInt(tokens[start + 2].content.split("/")[1])
        form = TimeSignatureDefinitionForm(keyword: tokens[start].content,
                                           top: top,
                                           bottom: bottom)
      else:
        form = IntDefinitionForm(keyword: tokens[start].content,
                                 value: parseInt(tokens[start + 2].content))
    elif tokens[start + 2].content[0] == '"':
      form = StringDefinitionForm(keyword: tokens[start].content,
                                  value: strip(tokens[start + 2].content, true, true, {'"'}))
    else:
      form = KeywordDefinitionForm(keyword: tokens[start].content,
                                 value: tokens[start + 2].content)

    return ParseResult(form: form, consumedTokens: 3)

  else:

    return ParseResult(form: InvalidForm(), consumedTokens: 0)
    
proc parseVoice(tokens: seq[Token], start: var int): Voice =

  result = Voice(content: newSeq[VoiceObject](0),
                 name: "",
                 lyrics: "",
                 octave: 0,
                 time: TimeSignature(top: 4, bottom: 4))

  var note = Note(duration: 4,
                  modifiers: newSeq[string](0))

  while start <= tokens.high:
    
    var pr = parseAssignment(tokens, start)

    if pr.consumedTokens > 0:
      
      var kw = pr.form.DefinitionForm.keyword

      if kw == "name":
        result.name = pr.form.KeywordDefinitionForm.value
      elif kw == "lyrics":
        result.lyrics = pr.form.KeywordDefinitionForm.value
      elif kw == "octave":
        result.octave = pr.form.IntDefinitionForm.value
      elif kw == "time":
        result.time.top = pr.form.TimeSignatureDefinitionForm.top
        result.time.bottom = pr.form.TimeSignatureDefinitionForm.bottom
      else:
        raise newException(ParseError, "Invalid voice attribute '" & kw & "' at position " & $start & ".")

      start += pr.consumedTokens

    elif tokens[start].content == "[":

      start += 1

      while tokens[start].content != "]":

        if syllables.contains(tokens[start].content):
          note.syllable = tokens[start].content
          result.content.add(note)
          start += 1
          note = Note(duration: note.duration,
                      modifiers: newSeq[string](0))

        elif octaveChanges.contains(tokens[start].content):
          note.modifiers.add(tokens[start].content)
          start += 1

        elif durations.contains(tokens[start].content):
          note.duration = parseInt(tokens[start].content)
          start += 1

        elif otherModifiers.contains(tokens[start].content):
          note.modifiers.add(tokens[start].content)
          start += 1

        elif barlines.contains(tokens[start].content):
          result.content.add(Barline(representation: tokens[start].content))
          start += 1

        else:
          raise newException(ParseError,
                             "Invalid modifier '" & tokens[start].content & "' at position " & $tokens[start].start & ".")

      return

proc parse*(tokens: seq[Token]): Tune =
  var tune: Tune

  var start = tokens.low

  # parse up to the keyword "voices"
  while start <= tokens.high:

    # if we are at the standalone keyword "voices", add it and start
    # parsing voices
    if tokens[start].content == "voices":
      start += 1
      break

    # try parsing an assignment
    var pr: ParseResult = parseAssignment(tokens, start)

    # if successful, alter the tune according to the parsed definition
    if pr.consumedTokens > 0:
      case pr.form.DefinitionForm.keyword:
        of "title":
          tune.title = pr.form.StringDefinitionForm.value
        of "subtitle":
          tune.subtitle = pr.form.StringDefinitionForm.value
        of "composer":
          tune.composer = pr.form.StringDefinitionForm.value
        of "key":
          if pr.form.KeywordDefinitionForm.value == "major":
            tune.key = kMajor
          else:
            tune.key = kMinor
        of "time":
          tune.time.top = pr.form.TimeSignatureDefinitionForm.top
          tune.time.bottom = pr.form.TimeSignatureDefinitionForm.bottom
        of "partial":
          tune.partial = pr.form.IntDefinitionForm.value
        else:
          raise newException(
            ParseError,
            "Invalid tune attribute '" & pr.form.DefinitionForm.keyword & "' at position " & $tokens[start].start & "."
          )

      start = start + pr.consumedTokens

    else:
      raise newException(ParseError, "Invalid form at position " & $tokens[start].start & ".")

  tune.voices = newSeq[Voice](0)

  # continue parsing voices
  while start <= tokens.high:
    tune.voices.add(parseVoice(tokens, start))
    start += 1

  return tune
  

proc showParsed*(fn: string) =
  var tokens: seq[Token] = tokenize(readFile(fn))
  var tune = parse(tokens)

  echo tune.title
  echo tune.subtitle
  echo tune.composer
  echo tune.time
  echo tune.key
  echo len(tune.voices)

  for note in tune.voices[2].content:
    if note of Note:
      write stdout, note.Note.syllable & ", 1/" & $note.Note.duration & ": "
      for s in note.Note.modifiers:
        write stdout, s
        write stdout, " "
      write stdout, "\n"
    else:
      echo note.BarLine.representation
