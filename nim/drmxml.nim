import drmcommon, parse, xmltree, strtabs

var noteheadType*: Noteheads = nhDefault

proc setNoteheads*(typ: Noteheads) =
  noteheadType = typ

const musicXmlDoctype*: string = """<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">"""


proc noteheadNode(syllable: string): XmlNode =
  # if not using round noteheads, set up a notehead node
  case noteheadType:
    of nhAikin, nhDefault:
      return <>notehead(newText(aikenNotehead(syllable)))
    of nhSacredHarp:
      return <>notehead(newText(sacredHarpNotehead(syllable)))
    of nhRound:
      return newComment("No notehead type needed.")

var lastNoteSlurred = false

proc xml*(note: Note, key: string, octave: int): XmlNode =
  result = <>note()

  if note.syllable == "r":
    var rest = <>rest()
    result.add(rest)
  
  else:
    var fp: FixedPitch = syllableToPitch(note.syllable, key)
    var pitch = <>pitch()

    pitch.add(<>step(newText(fp.name)))

    if fp.alteration != 0:
      pitch.add(<>alter(newText($fp.alteration)))

    var actualOctave: int = octave + keyOctaveOffset(key, note.syllable)

    pitch.add(<>octave(newText($actualOctave)))

    result.add(pitch)

  result.add(<>duration(newText($(96 / note.duration).int)))
  
  result.add(<>type(newText(durationToNoteType(note.duration))))

  # if not using round noteheads, set up a notehead node
  if noteheadType != nhRound:
    result.add(noteheadNode(note.syllable))

  if note.modifiers.contains("slur") and not lastNoteSlurred:
    var notations: XmlNode = <>notations()
    var slur: XmlNode
    slur = <>slur(type="start")
    notations.add(slur)
    result.add(notations)
    lastNoteSlurred = true

  elif lastNoteSlurred:
    var notations: XmlNode = <>notations()
    var slur: XmlNode
    slur = <>slur(type="stop")
    notations.add(slur)
    result.add(notations)
    lastNoteSlurred = false


proc clefNode(clef: Clefs): XmlNode =
  result = <>clef()
  
  case clef:
    of clfTreble:
      result.add(<>sign(newText("G")))
      result.add(<>line(newText("2")))
    of clfBass:
      result.add(<>sign(newText("F")))
      result.add(<>line(newText("4")))
    of clfAlto:
      result.add(<>sign(newText("C")))
      result.add(<>line(newText("3")))
    of clfTenor:
      result.add(<>sign(newText("C")))
      result.add(<>line(newText("4")))
    of clfOctaveTreble:
      result.add(<>sign(newText("G")))
      result.add(<>line(newText("2")))
      var oct = newElement("clef-octave-change")
      oct.add(newText("-1"))
      result.add(oct)

proc xml*(voice: Voice, key: string, octave, partial: int): XmlNode =
  result = <>part(id=voice.name)

  var attribs = <>attributes()

  attribs.add(<>divisions(newText("24")))

  var keyElem = <>key()
  keyElem.add(<>fifths(newText($keyToFifths(key))))

  attribs.add(keyElem)

  var time = <>time()
  time.add(<>beats(newText($voice.time.top)))

  var beatType = newElement("beat-type")
  beatType.add(newText($voice.time.bottom))
  time.add(beatType)

  attribs.add(time)

  attribs.add(clefNode(voice.clef))

  var measureNum = 1
  var measure = <>measure(number = $measureNum)
  measure.add(attribs)

  var measureLen = (1.0 / partial.float64)
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

  if not result.findAll("measure").contains(measure):
    result.add(measure)

proc xml*(tune: Tune, key: string): XmlNode =
  result = newElement("score-partwise")
  result.attrs = newStringTable("version", "3.0", modeCaseSensitive)

  var work = <>work()
  var title = newElement("work-title")
  title.add(newText(tune.title))
  work.add(title)
  result.add(work)

  var identification = <>identification()
  identification.add(<>creator(type="composer", newText(tune.composer)))

  var parts = newElement("part-list")
  result.add(parts)

  for voice in tune.voices:

    var part = newElement("score-part")
    part.attrs = newStringTable("id", voice.name, modeCaseSensitive)
    parts.add(part)

    var name = newElement("part-name")
    name.add(newText(voice.name))

    part.add(name)

    result.add(voice.xml(key, voice.octave + 3, tune.partial))

