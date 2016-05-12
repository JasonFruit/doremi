from __future__ import print_function

import math

import gtk
import pango
from doremi.doremi_parser import DoremiParser, Note, RepeatMarker
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
    def __init__(self, tune, voice, octave_offset = None, scale_factor=7):
        gtk.DrawingArea.__init__(self)

        partial = tune.partial

        if not partial:
            partial = 0
            
        partial = str(partial)
        
        self.dc = DurationCounter(tune.time, partial)
        self.tune = tune
        self.voice = [v
                      for v in tune
                      if v.name == voice][0]
        self.set_size_request(200, 200)
        self.show_all()
        self.default_gc = None
        self.y_offset = 40
        self.vspace = scale_factor
        self.base_spacing = self.vspace * 2 + self.vspace / 7.0
        self.stem_length = self.vspace * 3
        if octave_offset:
            self.octave_offset = octave_offset
        else:
            self.octave_offset = 0 - self.voice.octave

        # determine the shortest note (min_dur) in the tune

        # start assuming a really long minimum duration
        self.min_dur = 24

        for v in tune:
            for note in v:
                try:
                    dur = durations[note.duration]
                    if dur < self.min_dur:
                        self.min_dur = dur
                except AttributeError:
                    pass # ignore non-notes

        self.sxt_space = math.ceil(self.base_spacing / self.min_dur) + 1

        self.slur_start = None
        self.tie_start = None
        
    def flags(self, duration):
        sixteenths = durations[duration]
        if sixteenths == 1:
            return 2
        elif sixteenths < 4:
            return 1
        return 0

    def draw_flags(self, flags, x, stem_end, stem_dir):
        drawable = self.window
        gc = self.thick_gc()

        y_offset = 0
        
        for i in range(flags):
            drawable.draw_line(gc,
                               x,
                               stem_end - y_offset,
                               x + self.vspace,
                               stem_end - 2 * self.vspace * stem_dir - y_offset)
            y_offset += self.vspace

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

    def thick_gc(self):
        """Get a thick-line graphic context"""
        drawable = self.window
        return drawable.new_gc(foreground=None,
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
                               line_width=3,
                               line_style=-1,
                               cap_style=-1,
                               join_style=-1)

    def xthick_gc(self):
        """Get a thick-line graphic context"""
        drawable = self.window
        return drawable.new_gc(foreground=None,
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
                               line_width=6,
                               line_style=-1,
                               cap_style=-1,
                               join_style=-1)

    def draw_slur(self, direction, start, end):
        drawable = self.window
        gc = self.get_gc()

        x1, y1 = start
        x2, y2 = end

        width = x2 - x1

        if direction > 0:
            y = min([y1, y2]) * direction - self.vspace * 3 * direction
            drawable.draw_arc(gc, False,
                              x1, y + 3 * direction,
                              width, self.vspace,
                              0, 180 * 64)
        else:
            y = max([y1, y2]) * direction + self.vspace * 2 * direction
            drawable.draw_arc(gc, False,
                              x1, y * direction + 3 * direction,
                              width, self.vspace,
                              180 * 64, 180 * 64)      

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

    def draw_clef(self):
        drawable = self.window
        gc = self.xthick_gc()
        
        drawable.draw_line(gc,
                           7, self.y_offset + 2 * self.vspace,
                           7, self.y_offset + 6 * self.vspace)
        drawable.draw_line(gc,
                           int(self.base_spacing), self.y_offset + 2 * self.vspace,
                           int(self.base_spacing), self.y_offset + 6 * self.vspace)

    def draw_time(self, time):
        drawable = self.window
        gc = self.xthick_gc()
        num = pango.Layout(self.get_pango_context())
        num.set_text(time.split("/")[0])
        denom = pango.Layout(self.get_pango_context())
        denom.set_text(time.split("/")[1])
        
        drawable.draw_layout(gc, 30, self.y_offset + 5, num)
        drawable.draw_layout(gc, 30, self.y_offset + 5 + self.vspace * 4, denom)

    def draw_ledger_lines(self, x, num):
        drawable = self.window
        gc = self.get_gc()
        
        if num < 0:
            r = range(num - 4, 0)
            
        else:
            r = range(0, num + 1)

        for i in r:
            y = self.bottom_line + (2 * i * self.vspace)
            drawable.draw_line(gc,
                               x - self.vspace - 2, y,
                               x + self.vspace + 2, y)

    def draw_rest(self, duration, x):
        drawable = self.window
        gc = self.get_gc()
        tgc = self.thick_gc()
        xtgc = self.xthick_gc()

        x = int(x)
        
        if duration.startswith("4"):
            drawable.draw_line(gc,
                               x - self.vspace, self.y_offset + self.vspace,
                               x, self.y_offset + self.vspace * 2)
            drawable.draw_line(xtgc,
                               x, self.y_offset + self.vspace * 2,
                               x - self.vspace, self.y_offset + self.vspace * 3)
            drawable.draw_line(gc,
                               x - self.vspace, self.y_offset + self.vspace * 3,
                               x, self.y_offset + self.vspace * 4)
            drawable.draw_line(xtgc,
                               x, self.y_offset + self.vspace * 4,
                               x - self.vspace, self.y_offset + int(self.vspace * 4.5))
            drawable.draw_line(tgc,
                               x - self.vspace, self.y_offset + int(self.vspace * 4.5),
                               x - self.vspace, self.y_offset + self.vspace * 5)
            drawable.draw_line(gc,
                               x - self.vspace, self.y_offset + self.vspace * 5,
                               x - int(self.vspace / 2), self.y_offset + self.vspace * 6)

            if "." in duration:
                drawable.draw_arc(gc, True,
                                  x + self.vspace + 3, self.y_offset + int(self.vspace * 5.5),
                                  5, 5,
                                  0, 360 * 64)

        elif duration.startswith("2"):
            drawable.draw_line(xtgc,
                               x-10, self.y_offset + self.vspace * 4 - 3,
                               x + 10, self.y_offset + self.vspace * 4 - 3)
            if "." in duration:
                drawable.draw_arc(gc, True,
                                  x + 13, self.y_offset + self.vspace * 4 - 2,
                                  5, 5,
                                  0, 360 * 64)

        elif duration == "1":
            drawable.draw_line(xtgc,
                               x - 10, self.y_offset + self.vspace * 3 - 3,
                               x + 10, self.y_offset + self.vspace * 3 - 3)
            

        self.dc.count(str(duration))

        try:
            dur_num = int(duration)
        except ValueError:
            dur_num = float(duration) / 1.5

        space_after = self.sxt_space * (16 / dur_num)
        
        return x + space_after
            

    def draw_note(self, note_obj, key, x):
        """Draw a note of a given scale degree, duration, etc."""

        note, duration, octave = note_obj.pitch, note_obj.duration, note_obj.octave
        
        if note == "r":
            return self.draw_rest(duration, x)
        
        drawable = self.window
        gc = self.get_gc()

        try:
            dur_num = int(duration)
        except ValueError:
            dur_num = float(duration) / 1.5

        note_num = pitch_level[key][note]

        octave += self.octave_offset

        # is the notehead filled?  is it dotted? does it have a stem? which way?
        filled = (math.floor(dur_num) > 2)
        dotted = type(dur_num) != int
        has_stem = dur_num > 1
        
        if note_num + (7 * octave) > 3:
            stem_dir = 1
        else:
            stem_dir = -1

        # determine the center of the notehead
        x = int(x)
        y = int(self.bottom_line - self.vspace * note_num - (octave * 7 * self.vspace))

        if "slur" in note_obj.modifiers:
            if not self.slur_start:
                self.slur_start = (x, y)

        if "end slur" in note_obj.modifiers:
            self.draw_slur(stem_dir, self.slur_start, (x, y))
            self.slur_start = None

        if self.tie_start:
            self.draw_slur(stem_dir, self.tie_start, (x, y))
            self.tie_start = None

        if "tie" in note_obj.modifiers:
            self.tie_start = (x, y)
        
            

        #draw the appropriately-shaped notehead, with stem if needed
        if note.startswith("d"):
            drawable.draw_polygon(gc, filled, [(x + self.vspace, y + self.vspace),
                                                       (x - self.vspace, y + self.vspace),
                                                       (x, y - self.vspace)])
            if has_stem:
                stem_end = y + self.vspace * stem_dir + self.stem_length * stem_dir
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   stem_end)

                self.draw_flags(self.flags(duration), x, stem_end, stem_dir)
                    
            
        elif note.startswith("r"):
            drawable.draw_arc(gc,
                              filled,
                              x - self.vspace,
                              y - self.vspace,
                              self.vspace * 2,
                              self.vspace * 2,
                              145 * 64,
                              250 * 64)
            if filled:
                drawable.draw_polygon(gc, filled, [(x - self.vspace + 1, y - self.vspace + 3),
                                                   (x + self.vspace - 1, y - self.vspace + 3),
                                                   (x, y + self.vspace)])
            else:
                drawable.draw_line(gc, x - self.vspace + 1, y - self.vspace + 3,
                                   x + self.vspace - 1, y - self.vspace + 3)

            if has_stem:
                if stem_dir > 0:
                    y_offset = 6
                else:
                    y_offset = 3
                    
                stem_start = y + y_offset * stem_dir
                stem_end = stem_start + self.stem_length * stem_dir
                
                drawable.draw_line(gc,
                                   x,
                                   stem_start,
                                   x,
                                   stem_end)

                self.draw_flags(self.flags(duration), x, stem_end, stem_dir)
            
        elif note.startswith("m"):
            drawable.draw_polygon(gc, filled, [(x - self.vspace, y),
                                               (x, y - self.vspace),
                                               (x + self.vspace, y),
                                               (x, y + self.vspace)])
            if has_stem:
                stem_end = y + self.vspace * stem_dir + self.stem_length * stem_dir
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   stem_end)

                self.draw_flags(self.flags(duration), x, stem_end, stem_dir)
            
        elif note.startswith("f"):
            drawable.draw_polygon(gc, filled, [(x - self.vspace, y - self.vspace),
                                               (x - self.vspace, y + self.vspace),
                                               (x + self.vspace, y + self.vspace)])
            if has_stem:
                if stem_dir == -1:
                    stem_end = y + self.vspace - self.stem_length - 14
                    stem_x = x + self.vspace
                    drawable.draw_line(gc,
                                       stem_x,
                                       y + self.vspace,
                                       x + self.vspace,
                                       stem_end)
                else:
                    stem_end = y + self.vspace + self.stem_length
                    stem_x = x - self.vspace
                    drawable.draw_line(gc,
                                       stem_x,
                                       y + self.vspace,
                                       x - self.vspace,
                                       stem_end)
                self.draw_flags(self.flags(duration), stem_x, stem_end, stem_dir)
                    
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
                stem_end = y + self.vspace * stem_dir + self.stem_length * stem_dir
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   stem_end)
                self.draw_flags(self.flags(duration), x, stem_end, stem_dir)
            
        elif note.startswith("l"):
            drawable.draw_rectangle(gc,
                                    filled,
                                    x - self.vspace,
                                    y - self.vspace + 1,
                                    self.vspace * 2,
                                    self.vspace * 2 - 2)

            if has_stem:
                stem_x = x - self.vspace * stem_dir
                stem_end = y + self.vspace * stem_dir + self.stem_length * stem_dir
                
                drawable.draw_line(gc,
                                   stem_x,
                                   y + self.vspace * stem_dir - stem_dir,
                                   stem_x,
                                   stem_end)
                self.draw_flags(self.flags(duration), stem_x, stem_end, stem_dir)
            
        elif note.startswith("t"):
            drawable.draw_arc(gc,
                              filled,
                              x - self.vspace,
                              y - self.vspace,
                              self.vspace * 2,
                              self.vspace * 2,
                              25 * 64,
                              130 * 64)
            if filled:
                drawable.draw_polygon(gc, filled, [(x - self.vspace, y - self.vspace + 4),
                                                   (x + self.vspace, y - self.vspace + 4),
                                                   (x, y + self.vspace)])
            else:
                drawable.draw_line(gc, x - self.vspace, y - self.vspace + 4,
                                       x, y + self.vspace)
                drawable.draw_line(gc, x + self.vspace, y - self.vspace + 4,
                                       x, y + self.vspace)

            if has_stem:
                stem_end = y + self.vspace * stem_dir + self.stem_length * stem_dir
                drawable.draw_line(gc,
                                   x,
                                   y + self.vspace * stem_dir,
                                   x,
                                   stem_end)
                self.draw_flags(self.flags(duration), x, stem_end, stem_dir)

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

        # if the note falls outside the staff, it needs ledger lines
        if y > self.bottom_line:
            ledger_lines = (y - self.bottom_line) / (self.vspace * 2)
        elif y < self.y_offset:
            ledger_lines = 0 - int(math.ceil((self.y_offset - y) / (self.vspace * 2)))
        else:
            ledger_lines = 0
            
        self.draw_ledger_lines(x, ledger_lines)

        # track the note's duration
        self.dc.count(str(duration))

        space_after = self.sxt_space * (16 / dur_num)
        
        return x + space_after

    def draw_barline(self, x, style=""):
        gc = self.get_gc()
        tgc = self.thick_gc()
        xtgc = self.xthick_gc()
        drawable = self.window

        drawable.draw_line(gc,
                           int(x), self.y_offset,
                           int(x), self.bottom_line)

        if style == "|.":
            drawable.draw_line(tgc,
                               int(x) + 4, self.y_offset,
                               int(x) + 4, self.bottom_line)

        if style == "||":
            drawable.draw_line(gc,
                               int(x) + 4, self.y_offset,
                               int(x) + 4, self.bottom_line)

        return x + self.sxt_space * 2

    def set_width(self):
        width = sum([int(self.sxt_space) * durations[note.duration]
                     for note in self.voice
                     if "duration" in dir(note)])
        
        self.set_size_request(width + 300, 155)
        
    def draw(self):
        self.set_width()
        
        self.draw_staff()
        self.draw_clef()
        self.draw_time(self.tune.time)
        x = 50
        
        for note in self.voice:
            if type(note) == RepeatMarker:
                x = self.draw_barline(x, note.text)
            elif self.dc.at_barline():
                x = self.draw_barline(x)
            if type(note) == Note:
                x = self.draw_note(note,
                                   self.tune.key.split(" ")[1],
                                   x)
                
            else:
                pass #handle non-notes here

    def on_btn_press(self, btn, *args):
        self.draw()

if __name__ == "__main__":
    import sys
    win = gtk.Window()
    win.set_title("Test Window")
    win.connect("destroy", gtk.main_quit)
    
    vbx = gtk.VBox()
    win.add(vbx)

    dp = DoremiParser(sys.argv[1])
    tune = dp.convert()

    scroll = gtk.ScrolledWindow()
    scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
    voice_vbx = gtk.VBox()

    for voice in tune:
        dc = DoremiCanvas(tune, voice.name)
        voice_vbx.pack_start(dc, False)
        dc.connect("expose-event", dc.on_btn_press)
        
    scroll.add_with_viewport(voice_vbx)
    vbx.pack_start(scroll, True, True, 0)

    btn = gtk.Button("Apply Whatever")
    btn.connect("clicked", dc.on_btn_press)
    vbx.pack_end(btn, False)
    win.show_all()
    win.maximize()
    gtk.main()
