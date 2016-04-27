import codecs

from doremi_parser import DoremiParser
from lyric_parser import Lyric, LyricParser

import argparse

# set up argument parser and use it
p = argparse.ArgumentParser()
p.add_argument("infile",
               help="the Doremi file to process")
p.add_argument("outfile",
               help="the Lilypond output file")
p.add_argument("--key", "-k",
               help='the key for the output file (e.g. "A major", "c minor", "gis minor")')

p.add_argument("--shapes", "-s",
               help='use shape notes (i.e. "round" (default), "aikin", "sacredharp", "southernharmony", "funk", "walker")')

p.add_argument("--octaves", "-o", help="transpose up OCTAVES octaves")

p.add_argument("--lyricfile",
               "-l",
               help="the file containing the lyrics")

args = p.parse_args()

if args.octaves:
    octave_offset = int(args.octaves)
else:
    octave_offset = 0

# try to load the lyric file; if none is specified, use an empty
# Lyric
lyric = Lyric()

if args.lyricfile:
    try:
        text = codecs.open(args.lyricfile, "r", "utf-8").read()
        lyric = LyricParser(text).convert()
    except FileNotFoundError:
        raise Exception("Unable to open lyric file '%s'." % args.lyricfile)

# correct a common misspelling
if args.shapes and args.shapes.lower() == "aiken":
    args.shapes = "aikin"

# parse the Doremi file
lc = DoremiParser(args.infile)

# convert it to the internal representation
tune = lc.convert()

if not args.key:
    args.key = tune.key

# convert it to lilypond and write to the output file
ly = tune.to_lilypond(args.key.lower(),
                      octave_offset=octave_offset,
                      shapes=args.shapes,
                      lyric=lyric)

outfile = codecs.open(args.outfile, "w", "utf-8")
outfile.write(ly)
