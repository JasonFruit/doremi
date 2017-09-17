import drmcommon, parse, xmltree, strtabs

var noteheadType*: Noteheads = nhDefault

proc setNoteheads*(typ: Noteheads) =
  noteheadType = typ

proc xml*(note: Note, key: string, octave: int): XmlNode =
  var fp: FixedPitch = syllableToPitch(note.syllable, key)

  var pitch = <>pitch()

  pitch.add(<>step(newText(fp.name)))

  if fp.alteration != 0:
    pitch.add(<>alter(newText($fp.alteration)))

  var actualOctave: int = octave + keyOctaveOffset(key, note.syllable)
  
  pitch.add(<>octave(newText($actualOctave)))

  result = <>note()

  result.add(pitch)
  result.add(<>duration(newText($(96 / note.duration).int)))
  
  result.add(<>type(newText(durationToNoteType(note.duration))))

  # if not using round noteheads, set up a notehead node
  if noteheadType == nhAikin:
    result.add(<>notehead(newText(rootSyllable(note.syllable))))
  elif noteheadType == nhSacredHarp:
    result.add(<>notehead(newText(sacredHarpNotehead(note.syllable))))

proc xml*(voice: Voice, key: string, octave: int): XmlNode =
  result = <>part(id=voice.name)

  var attribs = <>attributes()
  var time = <>time()
  time.add(<>beats(newText($voice.time.top)))

  var beatType = newElement("beat-type")
  beatType.add(newText($voice.time.bottom))
  time.add(beatType)

  attribs.add(time)

  var clef = <>clef()

  if voice.clef == clfTreble:
    clef.add(<>sign(newText("G")))
    clef.add(<>line(newText("2")))
  elif voice.clef == clfBass:
    clef.add(<>sign(newText("F")))
    clef.add(<>line(newText("4")))
  elif voice.clef == clfAlto:
    clef.add(<>sign(newText("C")))
    clef.add(<>line(newText("3")))
  elif voice.clef == clfTenor:
    clef.add(<>sign(newText("C")))
    clef.add(<>line(newText("4")))
  elif voice.clef == clfOctaveTreble:
    clef.add(<>sign(newText("G")))
    clef.add(<>line(newText("2")))
    var oct = newElement("clef-octave-change")
    oct.add(newText("-1"))
    clef.add(oct)

  attribs.add(clef)

  var keyElem = <>key()
  keyElem.add(<>fifths(newText($keyToFifths(key))))

  attribs.add(keyElem)

  attribs.add(<>divisions(newText("24")))

  var measureNum = 1
  var measure = <>measure(number = $measureNum)
  measure.add(attribs)

  var measureLen = 0.0
  var curOctave = octave

  for obj in voice.content:
    if obj of Note:
      if obj.Note.modifiers.contains("-"):
        curOctave -= 1
      elif obj.Note.modifiers.contains("+"):
        curOctave += 1
      measure.add(obj.Note.xml(key, curOctave))
      measureLen = measureLen + (1.0 / obj.Note.duration.float64)
    if measureLen >= 0.97:
      measureLen = 0.0
      result.add(measure)
      measureNum += 1
      measure = <>measure(number = $measureNum)

proc xml*(tune: Tune, key: string): XmlNode =
  result = newElement("score-partwise")
  result.attrs = newStringTable("version", "3.0", modeCaseSensitive)

  var parts = newElement("part-list")
  result.add(parts)

  for voice in tune.voices:

    var part = newElement("score-part")
    part.attrs = newStringTable("id", voice.name, modeCaseSensitive)
    parts.add(part)

    var name = newElement("part-name")
    name.add(newText(voice.name))

    part.add(name)

    result.add(voice.xml(key, voice.octave + 3))
