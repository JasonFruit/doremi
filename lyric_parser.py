import codecs
from parsimonious import Grammar, NodeVisitor

class Verse(object):
    def __init__(self):
        self.words = []
    def __repr__(self):
        return " ".join(self.words)
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
    def __init__(self):
        self.name = ""
        self.verses = [Verse()]
    def __repr__(self):
        return """  name: %s
  %s""" % (self.name, "\n  ".join([repr(v) for v in self.verses]))
    def to_lilypond(self):
        return "\n".join([r"""\new Lyrics \lyricsto "exportedvoice_%s"
        { 
        %s
        }""" % (self.name,
                self.verses[i].to_lilypond())
                          for i in range(len(self.verses))])

class Lyric(object):
    def __init__(self):
        self.title = ""
        self.author = ""
        self.meter = ""
        self.voices = [LyricVoice()]
    def __repr__(self):
        return """title: %s
author: %s
meter: %s
voices: 
%s""" % (self.title, self.author, self.meter, "\n".join([repr(v)
                                                         for v in self.voices]))
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
    def __init__(self, text):
        NodeVisitor.__init__(self)

        self.lyric = Lyric()
        self.lyric.voices.append(LyricVoice())
        
        self.grammar = Grammar(open("lyric-grammar", "r").read())
        self.syntax = self.grammar.parse(text)
        
    def convert(self):
        self.visit(self.syntax)

        self.lyric.voices = [voice for voice in self.lyric.voices
                             if voice.name != ""]
        
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
        self.lyric.voices.append(LyricVoice())
        
    def visit_voice(self, node, vc):
        self.lyric.voices[-1].name = get_node_val(node, "name")

    def visit_verse(self, node, vc):
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
