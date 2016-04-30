from __future__ import print_function

import math

import gtk
from doremi.doremi_parser import DoremiParser, Note
from barlines import DurationCounter, durations

# the scale degree number for each syllable in major and minor
pitch_level = {"major": {"do": 0,
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
                         "ti": 6},
               "minor": {}}

# build minor based on the major values
for pitch in pitch_level["major"].keys():
    level =  pitch_level["major"][pitch]
    if level < 5:
        minor_level = level + 2
    else:
        minor_level = level - 5
    pitch_level["minor"][pitch] = minor_level

class DoremiCanvas(gtk.DrawingArea):
    """A GTK control to display a Doremi voice"""
    def __init__(self, tune, voice, octave_offset = 0):
        gtk.DrawingArea.__init__(self)
        self.dc = DurationCounter(tune.time, str(tune.partial))
        self.tune = tune
        self.voice = [v
                      for v in tune
                      if v.name == voice][0]
        self.set_size_request(200, 200)
        self.show_all()
        self.default_gc = None
        self.y_offset = 40
        self.vspace = 7
        self.stem_length = self.vspace * 3
        self.octave_offset = octave_offset

        self.min_dur = 24

        for note in self.voice:
            try:
                dur = durations[note.duration]
                if dur < self.min_dur:
                    self.min_dur = dur
            except AttributeError:
                pass # ignore non-notes

        self.sxt_space = math.ceil(15. / self.min_dur) + 1
        
    def get_gc(self):
        """Get a basic graphic context"""
        if not self.default_gc:
            drawable = self.window
            self.default_gc = drawable.new_gc(foreground=None,
                                              background=None,
                                              font=None, 
                                              function=-1,
                                              fill=-1,
                                              tile=None,
                                              stipple=None,
                                              clip_mask=None,
                                              subwindow_mode=-1,
                                              ts_x_origin=-1,
                                              ts_y_origin=-1,
                                              clip_x_origin=-1,
                                              clip_y_origin=-1,
                                              graphics_exposures=-1,
                                              line_width=-1,
                                              line_style=-1,
                                              cap_style=-1,
                                              join_style=-1)
        return self.default_gc
        
    def draw_staff(self):
        """Draw five lines across the control, leaving room top and bottom for
additional notes"""
        drawable = self.window
        gc = self.get_gc()
        
        lnum = 0
        while lnum < 5:
            y = lnum * (2 * self.vspace) + self.y_offset
            end_x = drawable.get_size()[0] - 5
            drawable.draw_line(gc, 5, y, end_x, y)
            self.bottom_line = y
            lnum += 1

    def draw_ledger_lines(self, x, num):
        drawable = self.window
        gc = self.get_gc()
        
        if num < 0:
            r = range(num, 0)
        else:
            r = range(1, num + 1)

        for i in r:
            y = self.bottom_line + (2 * i * self.vspace)
            drawable.draw_line(gc,
                               x - self.vspace - 2, y,
                               x + self.vspace + 2, y)

    def draw_note(self, note, duration, octave, key, x):
        """Draw a note of a given scale degree, duration, etc."""
        drawable = self.window
        gc = self.get_gc()

        try:
            dur_num = int(duration)
        except ValueError:
            dur_num = float("%s5" % duration)

        note_num = pitch_level[key][note]

        octave += self.octave_offset

        # is the notehead filled?  is it dotted? does it have a stem? which way?
        filled = (math.floor(dur_num) > 2)
        dotted = type(dur_num) != int
        has_stem = (math.floor(dur_num) > 1)
        
        if note_num + (7 * octave) > 3:
            stem_dir = 1
        else:
            stem_dir = -1

        # determine the center of the notehead
        x = int(x)
        y = int(self.bottom_line - self.vspace * note_num - (octave * 7 * self.vspace))

        #draw the appropriately-shaped notehead, with stem if needed
        if note.startswith("d"):
            drawable.draw_polygon(gc, filled, [(x + self.vspace, y + self.vspace),
                                                       (x - self.vspace, y + self.vspace),
                                                       (x, y - self.vspace)])
            if has_stem:
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   y + self.vspace * stem_dir + self.stem_length * stem_dir)
            
        elif note.startswith("r"):
            drawable.draw_arc(gc,
                              filled,
                              x - self.vspace,
                              y - self.vspace,
                              self.vspace * 2,
                              self.vspace * 2,
                              145 * 64,
                              250 * 64)
            drawable.draw_polygon(gc, filled, [(x - self.vspace + 1, y - self.vspace + 3),
                                               (x + self.vspace - 1, y - self.vspace + 3),
                                               (x, y + self.vspace)])

            if has_stem:
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir - 3 * stem_dir,
                                   x,
                                   y + self.vspace * stem_dir + self.stem_length * stem_dir - 3 * stem_dir)

            
        elif note.startswith("m"):
            drawable.draw_polygon(gc, filled, [(x - self.vspace, y),
                                               (x, y - self.vspace),
                                               (x + self.vspace, y),
                                               (x, y + self.vspace)])
            if has_stem:
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   y + self.vspace * stem_dir + self.stem_length * stem_dir)
            
        elif note.startswith("f"):
            drawable.draw_polygon(gc, filled, [(x - self.vspace, y - self.vspace),
                                               (x - self.vspace, y + self.vspace),
                                               (x + self.vspace, y + self.vspace)])
            if has_stem:
                if stem_dir == -1:
                    drawable.draw_line(gc,
                                       x + self.vspace,
                                       y + self.vspace,
                                       x + self.vspace,
                                       y + self.vspace - self.stem_length - 14)
                else:
                    drawable.draw_line(gc,
                                       x - self.vspace,
                                       y + self.vspace,
                                       x - self.vspace,
                                       y + self.vspace + self.stem_length)
                    
        elif note.startswith("s"):
            drawable.draw_arc(gc,
                              filled,
                              x - self.vspace,
                              y - self.vspace,
                              self.vspace * 2,
                              self.vspace * 2,
                              0,
                              360 * 64)
            if has_stem:
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   y + self.vspace * stem_dir + self.stem_length * stem_dir)
            
        elif note.startswith("l"):
            drawable.draw_rectangle(gc,
                                    filled,
                                    x - self.vspace,
                                    y - self.vspace + 1,
                                    self.vspace * 2,
                                    self.vspace * 2 - 2)

            if has_stem:
                drawable.draw_line(gc,
                                   x - self.vspace * stem_dir,
                                   y + self.vspace * stem_dir - stem_dir,
                                   x - self.vspace * stem_dir,
                                   y + self.vspace * stem_dir + self.stem_length * stem_dir)                                   
            
        elif note.startswith("t"):
            drawable.draw_arc(gc,
                              filled,
                              x - self.vspace,
                              y - self.vspace,
                              self.vspace * 2,
                              self.vspace * 2,
                              25 * 64,
                              130 * 64)
            drawable.draw_polygon(gc, filled, [(x - self.vspace, y - self.vspace + 4),
                                               (x + self.vspace, y - self.vspace + 4),
                                               (x, y + self.vspace)])

            if has_stem:
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   y + self.vspace * stem_dir + self.stem_length * stem_dir)

        # draw a dot, above and to the right for do, mi, fa, sol, and la
        if dotted:
            if note[0] in "dmfsl":
                drawable.draw_arc(gc, True,
                                  x + self.vspace + 1, y - self.vspace,
                                  5, 5,
                                  0, 360 * 64)
            elif note[0] in "rt": # or below for re and ti
                drawable.draw_arc(gc, True,
                                  x + self.vspace + 1, y + self.vspace,
                                  5, 5,
                                  0, 360 * 64)

        ledger_lines = 0 - int(math.floor((note_num + (octave * 7)) / 2))
        self.draw_ledger_lines(x, ledger_lines)

        self.dc.count(str(duration))

        space_after = self.sxt_space * (16 / dur_num)
        
        if self.dc.at_barline():
            self.draw_barline(x + space_after / 2)

        return x + space_after

    def draw_barline(self, x):
        gc = self.get_gc()
        drawable = self.window
        drawable.draw_line(gc,
                           int(x), self.y_offset,
                           int(x), self.bottom_line)
        
    def draw(self):
        self.draw_staff()
        x = 15
        for note in self.voice:
            if type(note) == Note:
                x = self.draw_note(note.pitch,
                                   note.duration,
                                   note.octave,
                                   self.tune.key.split(" ")[1],
                                   x)
                
            else:
                pass #handle non-notes here
            
    def on_btn_press(self, btn, *args):
        self.draw()

if __name__ == "__main__":
    win = gtk.Window()
    win.set_title("Test Window")
    win.connect("destroy", gtk.main_quit)

    vbx = gtk.VBox()
    win.add(vbx)

    dp = DoremiParser("tunes/goble.drm")
    tune = dp.convert()
    
    dc = DoremiCanvas(tune, tune[0].name)

    vbx.pack_start(dc, True)

    btn = gtk.Button("Apply Whatever")
    btn.connect("clicked", dc.on_btn_press)
    vbx.pack_end(btn, False)

    win.show_all()
    win.maximize()
    gtk.main()
