"""Provides objects to parse and represent words for tunes notated in
the Doremi music-representation language"""

import codecs
from parsimonious import Grammar, NodeVisitor

class Verse(object):
    """Represents the words to a stanza of a lyric"""
    def __init__(self):
        self.words = []
    def __word_to_lilypond(self, word):
        try:
            w = int(word)
            return r'\set stanza = #"%s. "' % w
        except ValueError:
            return word
    def to_lilypond(self):
        return " ".join([self.__word_to_lilypond(word)
                         for word in self.words])

class LyricVoice(object):
    """Represents the association of a musical voice and the verses of
words that are sung to it"""
    def __init__(self):
        self.name = ""
        self.verses = [Verse()]
    def to_lilypond(self):
        return "\n".join([r"""\new Lyrics \lyricsto "exportedvoice_%s"
        { 
        %s
        }""" % (self.name,
                self.verses[i].to_lilypond())
                          for i in range(len(self.verses))])

class Lyric(object):
    """Represents words to be sung, with special provision for strophic
lyrics"""
    def __init__(self):
        self.title = ""
        self.author = ""
        self.meter = ""
        self.voices = [LyricVoice()]

    def to_lilypond(self):
        return "\n\n".join([voice.to_lilypond()
                            for voice in self.voices])

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
        
class LyricParser(NodeVisitor):
    """Parses .drmw lyric files for association with Doremi tunes"""
    def __init__(self, text):
        NodeVisitor.__init__(self)

        # start with a new empty lyric
        self.lyric = Lyric()
        # add an empty voice to it
        self.lyric.voices.append(LyricVoice())

        # build an abstract syntax tree
        self.grammar = Grammar(open("lyric-grammar", "r").read())
        self.syntax = self.grammar.parse(text)
        
    def convert(self):
        """Convert the syntax tree to our internal representation"""
        self.visit(self.syntax)

        # remove any extra empty voices
        self.lyric.voices = [voice for voice in self.lyric.voices
                             if voice.name != ""]

        # remove any extra empty verses
        for voice in self.lyric.voices:
            voice.verses = voice.verses[:-1]
            
        return self.lyric

    def visit_title(self, node, vc):
        self.lyric.title = get_string_val(node)

    def visit_author(self, node, vc):
        self.lyric.author = get_string_val(node)

    def visit_meter(self, node, vc):
        self.lyric.meter = get_string_val(node)

    def visit_voicespec(self, node, vc):
        # the current voice is complete, so start a new one
        self.lyric.voices.append(LyricVoice())
        
    def visit_voice(self, node, vc):
        self.lyric.voices[-1].name = get_node_val(node, "name")

    def visit_verse(self, node, vc):
        # the verse is complete, so start a new one
        self.lyric.voices[-1].verses.append(Verse())

    def visit_word(self, node, vc):
        self.lyric.voices[-1].verses[-1].words.append(node.text.strip())

    def generic_visit(self, node, vc):
        pass

if __name__ == "__main__":
    text = codecs.open("hymns/dear-redeemer.drmw", "r", "utf-8").read()
    parser = LyricParser(text)
    lyric = parser.convert()
    print(lyric.to_lilypond())
