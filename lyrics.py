"""A rough parser for Doremi lyric files"""

from re import compile

class Lyric(object):
    def __init__(self, text):
        self.title = ""
        self.author = ""
        self.meter = ""
        self.verses = []

        if text != "":
            title_rgx = compile(r'title:\s*"([^"]*)"')
            author_rgx = compile(r'author:\s*"([^"]*)"')
            meter_rgx = compile(r'meter:\s*"([^"]*)"')
            verse_rgx = compile(r'\{\s*([^\}]*)\s*\}')
            word_div_rgx = compile(r"\s+")

            self.title = title_rgx.findall(text)[0]
            self.author = author_rgx.findall(text)[0]
            try:
                self.meter = meter_rgx.findall(text)[0]
            except (IndexError, ValueError):
                pass # it's already empty
            self.verses = verse_rgx.findall(text)
            self.verses = [" ".join(word_div_rgx.split(verse))
                           for verse in self.verses]

    def to_lilypond(self):
        return "\n".join([r"""\new Lyrics \lyricsto "one"
        { \set stanza = #"%s. "
        %s
        }""" % (i + 1, self.verses[i])
                          for i in range(len(self.verses))])

if __name__ == "__main__":
    import codecs
    infile = codecs.open("/home/jason/docs/pearl/prayer-comes-first.txt", "r", "utf-8")
    text = infile.read()
    lyric = Lyric(text)
    for verse in lyric.verses:
        print(verse)
