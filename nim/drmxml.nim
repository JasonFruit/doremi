import drmcommon, parse, xmltree, strtabs

var noteheadType*: Noteheads = nhDefault

proc setNoteheads*(typ: Noteheads) =
  noteheadType = typ

const musicXmlDoctype*: string = """<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 3.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">"""


# returns a node specifying the appropriate notehead for the syllable
proc noteheadNode(syllable: string): XmlNode =
  case noteheadType:
    of nhAikin, nhDefault:
      return <>notehead(newText(aikenNotehead(syllable)))
    of nhSacredHarp:
      return <>notehead(newText(sacredHarpNotehead(syllable)))
    of nhRound:
      # other program logic should prevent getting here
      return newComment("No notehead type needed.")

# track if the previous note was slurred/tied or not, so you know
# whether to end a slur/tie on the current note
var lastNoteSlurred = false
var lastNoteTied = false

# internal notes of a triplet are not marked, so keep track
var inTriplet = false

# represent a note as MusicXML in a given key and octave
proc xml*(note: Note, key: string, octave: int): XmlNode =
  var addNotations = false

  result = <>note()

  # if the note is a rest, skip all the pitch and octave stuff
  if note.syllable == "r":
    var rest = <>rest()
    result.add(rest)
  
  else: # if it's a pitched note

    var fp: FixedPitch = syllableToPitch(note.syllable, key)
    var pitch = <>pitch()

    # add a node for the base note name
    pitch.add(<>step(newText(fp.name)))

    # add the alteration -2..2 = doubleflat..doublesharp
    if fp.alteration != 0:
      pitch.add(<>alter(newText($fp.alteration)))

    # since doremi reads octaves from do, and musicxml always starts
    # them from c, some notes are offset an octave: correct for it
    var actualOctave: int = octave + keyOctaveOffset(key, note.syllable)

    pitch.add(<>octave(newText($actualOctave)))

    # the pitch node is now ready
    result.add(pitch)

  # the duration if not a triplet (whole-notes are 96 units in length)
  var dur = (96 / note.duration).int

  # handle triplets
  if note.triplet == tptStart:
    inTriplet = true
  elif note.triplet == tptStop:
    inTriplet = false
    
  if inTriplet:
    dur = (2 * dur / 3).int

  result.add(<>duration(newText($dur)))

  # add a tie to the note, but don't alter lastNoteTied yet; we also
  # have to add the tie to <notations>(!)
  if note.modifiers.contains("tie"):
    if lastNoteTied:
      result.add(<>tie(type="stop"))
    result.add(<>tie(type="start"))
  elif lastNoteTied:
    result.add(<>tie(type="stop"))

  result.add(<>type(newText(durationToNoteType(note.duration))))

  if inTriplet:
    var tpt = newElement("time-modification")
    var actual = newElement("actual-notes")
    actual.add(newText("3"))
    var normal = newElement("normal-notes")
    normal.add(newText("2"))
    tpt.add(actual)
    tpt.add(normal)
    result.add(tpt)

  # if not using round noteheads, set up a notehead node
  if noteheadType != nhRound:
    result.add(noteheadNode(note.syllable))

  var notations: XmlNode = <>notations()

  if note.modifiers.contains("slur") and not lastNoteSlurred:
    var slur: XmlNode
    slur = <>slur(type="start")
    notations.add(slur)
    addNotations = true
    lastNoteSlurred = true
  elif lastNoteSlurred:
    var slur: XmlNode
    slur = <>slur(type="stop")
    notations.add(slur)
    addNotations = true
    lastNoteSlurred = false

  if note.modifiers.contains("fermata"):
    notations.add(<>fermata())
    addNotations = true

  # duplicate the logic for adding the tie to the note, except this
  # time change lastNoteTied to its new value
  if note.modifiers.contains("tie"):
    if lastNoteTied:
      notations.add(<>tied(type="stop"))
    lastNoteTied = true
    notations.add(<>tied(type="start"))
    addNotations = true
  elif lastNoteTied:
    lastNoteTied = false
    notations.add(<>tied(type="stop"))
    addNotations = true

  if addNotations:
    result.add(notations)

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

proc barlineNode(barline: Barline, location: string): XmlNode =
  result = <>barline(location=location)
  var barlineStyle = newElement("bar-style")
  
  case barline.representation:
    of "||":
      barlineStyle.add(newText("light-light"))
    of "|.":
      barlineStyle.add(newText("light-heavy"))
    of ":|":
      barlineStyle.add(newText("light-heavy"))
      barlineStyle.add(<>repeat(direction="forward"))
    of "|:":
      barlineStyle.add(newText("heavy-light"))
      barlineStyle.add(<>repeat(direction="backward"))
    else:
      raise newException(ParseError, "Invalid barline type: '" & barline.representation)

  result.add(barlineStyle)

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
      if obj.Note.triplet == tptStart or (inTriplet and not (obj.Note.triplet == tptStop)):
        measureLen = measureLen + (0.67 / obj.Note.duration.float64)
      else:
        measureLen = measureLen + (1.0 / obj.Note.duration.float64)
        
    elif obj of Barline:
      var m: XmlNode
      var bn: XmlNode
      if measureLen == 0.0:
        var res = result.findAll("measure")
        m = res[res.high]
        bn = barlineNode(obj.Barline, "right")
      else:
        m = measure
        bn = barlineNode(obj.Barline, "middle")
      m.add(bn)
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
  var subtitle = newElement("work-number")
  subtitle.add(newText(tune.subtitle))
  work.add(subtitle)
  var title = newElement("work-title")
  title.add(newText(tune.title))
  work.add(title)
  result.add(work)

  var identification = <>identification()
  identification.add(<>creator(type="composer", newText(tune.composer)))

  result.add(identification)

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

