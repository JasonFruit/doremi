"""A simple music-representation language suitable for hymn tunes,
part-songs, and other brief, vocal-style works.

"""

# TODO: figure out how to make fermatas in bass staves upside-down in
# the template

import codecs
import copy

from parsimonious import Grammar, NodeVisitor

from doremi.lilypond import *
from doremi.lyric_parser import Lyric, LyricParser

class RepeatMarker(object):
    def __init__(self, text):
        self.text = text
    def to_lilypond(self, *args, **kwargs):
        if self.text == "|:":
            return r"\repeat volta 2 {"
        elif self.text == ":|":
            return r"}"
        elif self.text == "!":
            return r"} \alternative { {"
        elif self.text == "1!":
            return r"} {"
        elif self.text == "2!":
            return r"} }"
        elif self.text == "|.":
            return r'\bar "|."'
        elif self.text == "||":
            return r'\bar "||"'

class Note(object):
    """Represents a note (or rest) in a musical work, including scale
degree, duration, octave, and other information"""
    def __init__(self,          # initialize with empty properties
                 pitch=None,    # because they are built on-the-fly
                 duration=None,
                 octave=None,
                 modifiers=list()):
        self.pitch = pitch
        self.duration = duration
        self.octave = octave
        self.modifiers = modifiers
    def to_lilypond(self, key, octave_offset = 0):
        """
        Convert to an equivalent Lilypond representation
        """

        # short-circuit if this is a rest
        if self.pitch == "r":
            return "%s%s" % (self.pitch, self.duration)
        
        pitch = syllable_to_note(self.pitch, key)
        octave = self.octave + octave_offset + 1

        # convert internal octave representation to Lilypond, which
        # uses c->b
        offset = key_octave_offset[key.lower()]

        local_pitch_level = copy.copy(pitch_level)

        # adjust the local copy of the pitch-level order to go from
        # la->sol if key is minor
        if "minor" in key.lower():
            for k in local_pitch_level.keys():
                local_pitch_level[k] = local_pitch_level[k] + 2
                if local_pitch_level[k] > 6:
                    local_pitch_level[k] -= 7
        
        if local_pitch_level[self.pitch] - offset < 0:
            octave -= 1
        elif local_pitch_level[self.pitch] - offset > 6:
            octave += 1

        if octave < 0:
            octave = "," * abs(octave)
        else:
            octave = "'" * octave

        # start or end slurs (or beams) as indicated by modifiers
        slur = ""
        if "slur" in self.modifiers:
            if self.duration in ["8", "8.", "16"]:
                slur = "["
            else:
                slur = "("
        elif "end slur" in self.modifiers:
            if self.duration in ["8", "8.", "16"]:
                slur = "]"
            else:
                slur = ")"

        # ties only ever connect two notes, so need not be explicitly
        # terminated
        tie = ""
        if "tie" in self.modifiers:
            tie = "~"

        # add a fermata
        if "fermata" in self.modifiers:
            fermata = r"\fermata"
        else:
            fermata = ""

        # assemble and return the Lilypond string
        return "%s%s%s%s%s%s" % (pitch,
                                 octave,
                                 self.duration,
                                 tie,
                                 slur,
                                 fermata)
            
class Voice(list):
    """Represents a named part in a vocal-style composition"""
    def __init__(self,
                 name="",
                 octave=""):
        list.__init__(self)
        self.name = name
        self.octave = octave # the starting octave for the part
    def last_note(self):
        index = -1
        try:
            while type(self[index]) != Note:
                index -= 1
            return self[index]
        except IndexError:
            raise IndexError("No previous notes")
    def to_lilypond(self,
                    time,
                    key,
                    octave_offset=0,
                    shapes=None,
                    template="default"):
        """A representation of the voice as a Lilypond string"""

        # association of doremi shape args and Lilypond shape commands
        shape_dic = {"round": ("", ""),
                     "aikin": (r"\aikenHeads", "Minor"),
                     "sacredharp": (r"\sacredHarpHeads", "Minor"),
                     "southernharmony": (r"\southernHarmonyHeads", "Minor"),
                     "funk": (r"\funkHeads", "Minor"),
                     "walker": (r"\walkerHeads", "Minor")}

        # build the lilypond shape command
        if shapes == None:
            lshapes = ""
        else:
            lparts = shape_dic[shapes.lower()]
            lshapes = lparts[0]

            # there's a different command for minor
            if "minor" in key:
                lshapes += lparts[1]

        tmpl = codecs.open("templates/%s-voice.tmpl" % template,
                           "r",
                           "utf-8").read()
        
        return tmpl % {"name": self.name,
                       "key": key.replace(" ", " \\"), # a minor -> a \minor
                       "time": time,
                       "shapes": lshapes,
                       "notes": " ".join(
                           [note.to_lilypond(
                               key,
                               octave_offset=octave_offset)
                            for note in self])}


class Tune(list):
    """Represents a vocal-style tune, e.g. a hymn-tune or partsong"""
    def __init__(self,
                 title="",
                 scripture="",
                 composer="",
                 key="",
                 time=None,
                 partial=None):
        self.title = title
        self.scripture = scripture
        self.composer = composer
        self.key = key
        self.time = time
        self.partial = partial
        
    def to_lilypond(self,
                    key,
                    octave_offset=0,
                    shapes=None,
                    lyric=None,
                    template="default"):
        """Return a Lilypond version of the tune"""

        key = key_to_lilypond(key)

        # represent the partial beginning measure a la Lilypond if
        # necessary
        if self.partial:
            partial = r"\partial %s" % self.partial
        else:
            partial = ""

        # TODO: make this allow other templates
        ly = codecs.open("templates/%s.tmpl" % template, "r", "utf-8").read()

        tmpl_data = {"voices": "\n".join(
            [voice.to_lilypond(self.time,
                               key,
                               octave_offset=octave_offset,
                               shapes=shapes,
                               template=template)
             for voice in self]),
                     "author": lyric.author,
                     "lyrictitle": lyric.title,
                     "meter": lyric.meter,
                     "title": self.title,
                     "scripture": self.scripture,
                     "composer": self.composer,
                     "partial": partial}

        for voice in self:
            tmpl_data["%s_lyrics" % voice.name] = ""
            
        for lvoice in lyric.voices:
            tmpl_data["%s_lyrics" % lvoice.name] = lvoice.to_lilypond()
                    
        return ly % tmpl_data
                            

def get_node_val(node, val_type):
    """Return the value as a string of a child node of the specified type,
or raise ValueError if none exists"""
    for child in node.children:
        if child.expr_name == val_type:
            return child.text.strip('"')
    raise ValueError("No value of specified type.")

def get_string_val(node):
    """Return the value of a string child node, if exists; otherwise,
raise a ValueError"""
    try:
        return get_node_val(node, "string")
    except:
        raise ValueError("No string value.")
        
class DoremiParser(NodeVisitor):
    def __init__(self, tune_fn):
        NodeVisitor.__init__(self)
        # start with an empty tune, voice, note, and list of modifiers
        self.tune = Tune()
        self.voice = Voice()
        self.note = Note()
        self.note_modifiers = []

        # at the outset, we are not in a voice's content
        self.in_content = False

        # set up the actual parser
        grammar = Grammar(open("doremi-grammar", "r").read())

        # read and parse the tune
        tune_text = codecs.open(tune_fn, "r", "utf-8").read()
        self.syntax = grammar.parse(tune_text)
        
    def convert(self):
        """Convert the parse tree to the internal music representation"""
        self.visit(self.syntax)
        return self.tune

    # title, composer, key, and partial value can only occur at the
    # tune level, so they always are added to the tune
    def visit_title(self, node, vc):
        self.tune.title = get_string_val(node)
    def visit_scripture(self, node, vc):
        self.tune.scripture = get_string_val(node)
    def visit_composer(self, node, vc):
        self.tune.composer = get_string_val(node)
    def visit_key(self, node, vc):
        text = " ".join([child.text for child in node.children
                         if child.expr_name == "name"])
        self.tune.key = text
    def visit_partial(self, node, vc):
        self.tune.partial = int(get_node_val(node, "number"))

    def visit_time(self, node, vc):
        time = get_node_val(node, "fraction")

        # if it occurs inside a voice's note array
        if self.in_content:
           self.note_modifiers.append(time)
        else: # otherwise, it's at the tune level
            self.tune.time = time

    # octave and voice-name only occur at the voice level
    def visit_octave(self, node, vc):
        self.voice.octave = int(get_node_val(node, "number"))
    def visit_voice_name(self, node, vc):
        self.voice.name = node.children[-1].text

    # modifiers only occur in a collection of notes, and are stored at
    # the note level
    def visit_note_modifier(self, node, vc):
        self.note_modifiers.append(node.text)
        
    def visit_voice(self, node, vc):
        # a voice is only visited when fully parsed, so the voice is
        # already fully constructed; add it to the tune and start a
        # new one
        self.tune.append(self.voice)
        self.voice = Voice()
        
    def visit_note(self, node, vc):
        # a note is only visited after its modifiers have been
        # visited, so we finalize it and add it to the voice here

        # if there's no duration explicit, it's the same as the
        # previous note in the same voice
        if not self.note.duration:
            self.note.duration = self.voice.last_note().duration
            
        self.note.modifiers = self.note_modifiers
        self.note.pitch = node.text

        # if there's a previous note, start from its octave; if not,
        # start from the voice's octave
        try:
            self.note.octave = self.voice.last_note().octave
        except IndexError:
            self.note.octave = self.voice.octave

        # alter the octave according to octave modifiers
        for mod in self.note.modifiers:
            if mod == "-":
                self.note.octave -= 1
            elif mod == "+":
                self.note.octave += 1

        # if a slur started on the previous note and is not continued
        # by this one, explicitly end it
        try:
            if "slur" in self.voice.last_note().modifiers:
                if not "slur" in self.note.modifiers: 
                    self.note.modifiers.append("end slur")
        except IndexError:
            pass

        # add the note to the voice and start a new one with no
        # modifiers
        self.voice.append(self.note)
        self.note = Note()
        self.note_modifiers = []

    def visit_repeat(self, node, vc):
        self.voice.append(RepeatMarker(node.text))
        
    def visit_number(self, node, vc):
        # all numbers except note durations are handled at a higher level
        if self.in_content:
            self.note.duration = node.text
            
    def generic_visit(self, node, vc):
        # set whether we're in the note-content of a voice based on
        # open- and close-brackets
        if node.text == "[":
            self.in_content = True
        elif node.text == "]":
            self.in_content = False
