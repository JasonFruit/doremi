"""Some data and functions useful for converting to Lilypond"""

pitch_level = {"do": 0,
               "di": 0,
               "ra": 1,
               "re": 1,
               "ri": 1,
               "me": 2,
               "mi": 2,
               "fa": 3,
               "fi": 3,
               "se": 4,
               "sol": 4,
               "si": 4,
               "le": 5,
               "la": 5,
               "li": 5,
               "te": 6,
               "ti": 6}

key_octave_offset = {'fis major': -3,
                     'gis minor': 3,
                     'c minor': 0,
                     'a minor': 2,
                     'eis minor': -2,
                     'fis minor': -3,
                     'bes major': 1,
                     'cis minor': 0,
                     'a major': 2,
                     'g major': 3,
                     'c major': 0,
                     'e minor': -2,
                     'des major': -1,
                     'cis major': 0,
                     'f minor': -3,
                     'aes major': 2,
                     'bes minor': 1,
                     'dis minor': -1,
                     'ges minor': 3,
                     'ces major': 0,
                     'ges major': 3,
                     'ais minor': 2,
                     'd major': -1,
                     'f major': -3,
                     'd minor': -1,
                     'es major': -2,
                     'e major': -2,
                     'b minor': 1,
                     'b major': 1}

keys = {"c major": {"do": "c",
                    "di": "cis",
                    "ra": "des",
                    "re": "d", 
                    "ri": "dis",
                    "me": "es",
                    "mi": "e",
                    "fa": "f",
                    "fi": "fis",
                    "se": "ges",
                    "sol": "g",
                    "si": "gis",
                    "le": "aes",
                    "la": "a",
                    "li": "ais",
                    "te": "bes",
                    "ti": "b"},
        "cis major": {"do": "cis",
                      "di": "cisis",
                      "ra": "d",
                      "re": "dis", 
                      "ri": "disis",
                      "me": "e",
                      "mi": "eis",
                      "fa": "fis",
                      "fi": "fisis",
                      "se": "g",
                      "sol": "gis",
                      "si": "gisis",
                      "le": "a",
                      "la": "ais",
                      "li": "aisis",
                      "te": "b",
                      "ti": "bis"},
        "des major": {"do": "des",
                      "di": "d",
                      "ra": "eses",
                      "re": "es", 
                      "ri": "e",
                      "me": "fes",
                      "mi": "f",
                      "fa": "ges",
                      "fi": "g",
                      "se": "aeses",
                      "sol": "aes",
                      "si": "a",
                      "le": "beses",
                      "la": "bes",
                      "li": "b",
                      "te": "ces",
                      "ti": "c"},
        "d major": {"do": "d",
                    "di": "dis",
                    "ra": "es",
                    "re": "e", 
                    "ri": "eis",
                    "me": "f",
                    "mi": "fis",
                    "fa": "g",
                    "fi": "gis",
                    "se": "aes",
                    "sol": "a",
                    "si": "ais",
                    "le": "bes",
                    "la": "b",
                    "li": "bis",
                    "te": "c",
                    "ti": "cis"},
        "es major": {"do": "es",
                     "di": "e",
                     "ra": "fes",
                     "re": "f", 
                     "ri": "fis",
                     "me": "ges",
                     "mi": "g",
                     "fa": "aes",
                     "fi": "a",
                     "se": "beses",
                     "sol": "bes",
                     "si": "b",
                     "le": "ces",
                     "la": "c",
                     "li": "cis",
                     "te": "des",
                     "ti": "d"},
        "e major": {"do": "e",
                    "di": "eis",
                    "ra": "f",
                    "re": "fis", 
                    "ri": "fisis",
                    "me": "g",
                    "mi": "gis",
                    "fa": "a",
                    "fi": "ais",
                    "se": "bes",
                    "sol": "b",
                    "si": "bis",
                    "le": "c",
                    "la": "cis",
                    "li": "cisis",
                    "te": "d",
                    "ti": "dis"},
        "f major": {"do": "f",
                    "di": "fis",
                    "ra": "ges",
                    "re": "g", 
                    "ri": "gis",
                    "me": "aes",
                    "mi": "a",
                    "fa": "bes",
                    "fi": "b",
                    "se": "ces",
                    "sol": "c",
                    "si": "cis",
                    "le": "des",
                    "la": "d",
                    "li": "dis",
                    "te": "es",
                    "ti": "e"},
        "fis major": {"do": "fis",
                      "di": "fisis",
                      "ra": "g",
                      "re": "gis", 
                      "ri": "gisis",
                      "me": "a",
                      "mi": "ais",
                      "fa": "b",
                      "fi": "bis",
                      "se": "c",
                      "sol": "cis",
                      "si": "cisis",
                      "le": "d",
                      "la": "dis",
                      "li": "disis",
                      "te": "e",
                      "ti": "eis"},
        "ges major": {"do": "ges",
                      "di": "g",
                      "ra": "aeses",
                      "re": "aes", 
                      "ri": "a",
                      "me": "beses",
                      "mi": "bes",
                      "fa": "ces",
                      "fi": "c",
                      "se": "deses",
                      "sol": "des",
                      "si": "d",
                      "le": "eses",
                      "la": "es",
                      "li": "e",
                      "te": "fes",
                      "ti": "f"},        
        "g major": {"do": "g",
                    "di": "gis",
                    "ra": "aes",
                    "re": "a", 
                    "ri": "ais",
                    "me": "bes",
                    "mi": "b",
                    "fa": "c",
                    "fi": "cis",
                    "se": "des",
                    "sol": "d",
                    "si": "dis",
                    "le": "es",
                    "la": "e",
                    "li": "eis",
                    "te": "f",
                    "ti": "fis"},
        "aes major": {"do": "aes",
                      "di": "a",
                      "ra": "beses",
                      "re": "bes", 
                      "ri": "b",
                      "me": "ces",
                      "mi": "c",
                      "fa": "des",
                      "fi": "d",
                      "se": "eses",
                      "sol": "es",
                      "si": "e",
                      "le": "fes",
                      "la": "f",
                      "li": "fis",
                      "te": "ges",
                      "ti": "g"},        
        "a major": {"do": "a",
                    "di": "ais",
                    "ra": "bes",
                    "re": "b", 
                    "ri": "bis",
                    "me": "c",
                    "mi": "cis",
                    "fa": "d",
                    "fi": "dis",
                    "se": "es",
                    "sol": "e",
                    "si": "eis",
                    "le": "f",
                    "la": "fis",
                    "li": "fisis",
                    "te": "g",
                    "ti": "gis"},
        "bes major": {"do": "bes",
                      "di": "b",
                      "ra": "ces",
                      "re": "c", 
                      "ri": "cis",
                      "me": "des",
                      "mi": "d",
                      "fa": "es",
                      "fi": "e",
                      "se": "fes",
                      "sol": "f",
                      "si": "fis",
                      "le": "ges",
                      "la": "g",
                      "li": "gis",
                      "te": "aes",
                      "ti": "a"},
        "b major": {"do": "b",
                    "di": "bis",
                    "ra": "c",
                    "re": "cis", 
                    "ri": "cisis",
                    "me": "d",
                    "mi": "dis",
                    "fa": "e",
                    "fi": "eis",
                    "se": "f",
                    "sol": "fis",
                    "si": "fisis",
                    "le": "g",
                    "la": "gis",
                    "li": "gisis",
                    "te": "a",
                    "ti": "ais"},
        "ces major": {"do": "ces",
                      "di": "c",
                      "ra": "deses",
                      "re": "des", 
                      "ri": "d",
                      "me": "eses",
                      "mi": "es",
                      "fa": "fes",
                      "fi": "f",
                      "se": "geses",
                      "sol": "ges",
                      "si": "g",
                      "le": "aeses",
                      "la": "aes",
                      "li": "a",
                      "te": "beses",
                      "ti": "bes"}}

keys["g minor"] = keys['bes major']
keys["cis minor"] = keys['e major']
keys["b minor"] = keys['d major']
keys["c minor"] = keys['es major']
keys["e minor"] = keys['g major']
keys["f minor"] = keys['aes major']
keys["ais minor"] = keys['cis major']
keys["bes minor"] = keys['des major']
keys["a minor"] = keys['c major']
keys["gis minor"] = keys['b major']
keys["d minor"] = keys['f major']
keys["fis minor"] = keys['a major']
keys["ais minor"] = keys['ces major']
keys["es minor"] = keys['ges major']
keys["dis minor"] = keys['fis major']

def syllable_to_note(syllable, key):
    return keys[key.lower()][syllable]

def key_to_lilypond(key):
    elems = key.split(" ")
    if len(elems[0]) == 2:
        chars = [c for c in elems[0]]
        if chars[1] == "b":
            chars[1] = "es"
        elif chars[1] == "#":
            chars[1] = "is"
        elems[0] = "".join(chars)
        if elems[0] == "ees":
            elems[0] = "es"
    return " ".join(elems)
