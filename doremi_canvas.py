from __future__ import print_function

import sys
import math

# TODO: make compatible with Python 3
# if sys.version_info[0] == 3:
#     import gi
#     gi.require_version('Gtk', '3.0')
#     from gi.repository import Gtk as gtk
#     from gi.repository import Gdk
# else:    
import gtk
import pango

# import the stuff to parse Doremi files
from doremi.doremi_parser import Note, RepeatMarker
from barlines import DurationCounter, durations

# the scale degree number for each syllable in major
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
               "minor": {}} # minor is about to be built

# build relative minor based on the major values
for pitch in pitch_level["major"].keys():
    level =  pitch_level["major"][pitch]
    if level < 5:
        minor_level = level + 2
    else:
        minor_level = level - 5
    pitch_level["minor"][pitch] = minor_level

    
class DoremiCanvas(gtk.DrawingArea):
    """A GTK control to display a Doremi voice"""
    def __init__(self,
                 tune,
                 voice,
                 octave_offset = None,
                 scale_factor=7):

        # the vertical offset between two scale degrees (half the
        # distance between staff lines)
        self.vspace = scale_factor

        gtk.DrawingArea.__init__(self)

        # when the control needs redrawing, handle it
        self.connect("expose-event", self.redraw_event_handler)

        partial = tune.partial

        if not partial:
            partial = 0

        # the partial value may or may not be a string; make sure it
        # is one
        partial = str(partial)

        # the duration counter trackes the position with respect to
        # barlines
        self.dc = DurationCounter(tune.time, partial)
        
        self.tune = tune

        # retrieve the correct voice from the tune by name
        self.voice = [v
                      for v in tune
                      if v.name == voice][0]

        self.y_offset = 40 # the distance from the top of the control
                           # to the top line of the staff

        # we have to set _some_ size to display correctly
        self.set_size_request(0, 150)
        self.show_all()

        # before the window is rendered, there is no graphics context
        self.default_gc = None
        
        self.base_spacing = self.vspace * 2 + self.vspace / 7.0
        self.stem_length = self.vspace * 3
        if octave_offset:
            self.octave_offset = octave_offset
        else:
            self.octave_offset = 0 - self.voice.octave

        # determine the shortest note (min_dur) in the tune

        # start assuming a really long minimum duration
        self.min_dur = 24

        # find the shortest note duration in the entire tune, not just
        # this voice
        for v in tune:
            for note in v:
                try:
                    dur = durations[note.duration]
                    if dur < self.min_dur:
                        self.min_dur = dur
                except AttributeError:
                    pass # ignore non-notes

        # set the sixteenth-note space to make the minimum duration a sensible minimum space
        self.sxt_space = math.ceil(self.base_spacing / self.min_dur) + 1

        # we are neither in a slur nor a tie
        self.slur_start = None
        self.tie_start = None
        
    def flags(self, duration):
        """How many flags does duration get?"""
        sixteenths = durations[duration]
        if sixteenths == 1:
            return 2
        elif sixteenths < 4:
            return 1
        return 0

    def draw_flags(self, flags, x, stem_end, stem_dir):
        """Draw a number of flags on a stem ending at stem_end and pointing in stem_dir"""
        
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

        # cache it as it seems to take time to construct and we use it
        # a lot (I may be wrong about its construction, but . . . )
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
        """Get an extra-thick-line graphic context"""
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

    def export(self, filename, type):
        """Export the voice as an image of type [jpeg, png, ?...] to the
        specified filename"""
        
        drawable = self.window
        colormap = drawable.get_colormap()
        
        pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, 0, 8, *drawable.get_size())
        pixbuf = pixbuf.get_from_drawable(drawable, colormap, 0,0,0,0, *drawable.get_size())
        
        pixbuf.save(filename, type)

    def draw_slur(self, direction, start, end):
        """Draw a slur facing away from the stems of a note, from (x,y) point
        start to end"""
        
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
        notes on ledger lines"""
        
        drawable = self.window
        gc = self.get_gc()

        # draw five lines
        for lnum in range(0, 5):
            y = lnum * (2 * self.vspace) + self.y_offset
            end_x = drawable.get_size()[0] - 5 # end the lines 5 units
                                               # from the right side
                                               # of the control
            drawable.draw_line(gc, 5, y, end_x, y)
            self.bottom_line = y # save the position of the bottom line

    def draw_clef(self):
        """Draw a clef like that used by Jesse Aikin in his Christian Minstrel
        to indicate notes that are pitched, but only relatively
        """
        
        drawable = self.window
        gc = self.xthick_gc()
        
        drawable.draw_line(gc,
                           7, self.y_offset + 2 * self.vspace,
                           7, self.y_offset + 6 * self.vspace)
        drawable.draw_line(gc,
                           int(self.base_spacing), self.y_offset + 2 * self.vspace,
                           int(self.base_spacing), self.y_offset + 6 * self.vspace)

    def draw_time(self, time):
        """Draw the time signature (yes, I know it's not really a fraction,
        but are there names for the top and bottom numbers?"""
        
        drawable = self.window
        gc = self.get_gc()
        
        num = pango.Layout(self.get_pango_context())
        num.set_text(time.split("/")[0])
        
        denom = pango.Layout(self.get_pango_context())
        denom.set_text(time.split("/")[1])
        
        drawable.draw_layout(gc, 30, self.y_offset + 5, num)
        drawable.draw_layout(gc, 30, self.y_offset + 5 + self.vspace * 4, denom)

    def draw_ledger_lines(self, x, num):
        """Draw num ledger lines at x position; if num is negative, draw them
        above the staff"""
        
        drawable = self.window
        gc = self.get_gc()
        
        if num < 0:
            r = range(num - 4, 0) # 4 to start them up above the staff
            
        else:
            r = range(0, num + 1) # 1 to start them below the staff

        # draw the lines spaced just like the staff
        for i in r:
            y = self.bottom_line + (2 * i * self.vspace)
            drawable.draw_line(gc,
                               x - self.vspace - 2, y,
                               x + self.vspace + 2, y)

    def draw_rest(self, duration, x):
        """Draw a rest of the given duration at the given x position,
        returning the next x-position"""
        
        drawable = self.window

        # we need all these thicknesses to draw rests
        gc = self.get_gc()
        tgc = self.thick_gc()
        xtgc = self.xthick_gc()

        x = int(x)

        # rests are complicated; their appearance varies without pattern based on their duration
        
        if duration.startswith("4"):

            # quarter rests are a complicated squiggle whose varying
            # thickness is apparently important to legibility
            
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

            # TODO: eliminate magic numbers that do not scale
            drawable.draw_line(xtgc,
                               x-10, self.y_offset + self.vspace * 4 - 3,
                               x + 10, self.y_offset + self.vspace * 4 - 3)
            if "." in duration:
                drawable.draw_arc(gc, True,
                                  x + 13, self.y_offset + self.vspace * 4 - 2,
                                  5, 5,
                                  0, 360 * 64)

        elif duration == "1":

            # TODO: eliminate magic numbers that do not scale
            drawable.draw_line(xtgc,
                               x - 10, self.y_offset + self.vspace * 3 - 3,
                               x + 10, self.y_offset + self.vspace * 3 - 3)
            
        else:
            #TODO: implement eighth and sixteenth rests
            raise Exception("Rests of duration %s not implemented." % duration)

        # track the duration of the rest
        self.dc.count(str(duration))

        # before we figure the spacing, we need to handle dots
        try:
            dur_num = int(duration)
        except ValueError:
            # converting a dotted duration such as "2." to an int will
            # fail, so convert it to a float and multiply by 3/2
            dur_num = float(duration) / 1.5

        space_after = self.sxt_space * (16 / dur_num)

        # return the next x position
        return x + space_after
            

    def draw_note(self, note_obj, key, x):
        """Draw a note of a given scale degree, duration, etc. returning the
        next x position"""

        # extract pitch, duration, and octave information from the
        # note object
        note, duration, octave = note_obj.pitch, note_obj.duration, note_obj.octave

        # if the note is a rest (Doremi notes and rests have the same
        # representation), return the result of drawing the rest
        if note == "r":
            return self.draw_rest(duration, x)

        drawable = self.window
        gc = self.get_gc()

        # convert the duration to a number of sixteenth notes
        try:
            dur_num = int(duration)
        except ValueError:
            # converting the dotted duration (e.g. "2.") to an int
            # will fail; instead we convert it to a float and multiply
            # by 3/2
            dur_num = float(duration) / 1.5

        # find out the scale degree for the pitch syllable in the key
        # (major or minor)
        note_num = pitch_level[key][note]

        # alter the octave according to the display octave offset
        octave += self.octave_offset

        # is the notehead filled?  is it dotted? does it have a stem? which way?
        filled = (math.floor(dur_num) > 2) # half-notes and lower are unfilled, dotted or not
        dotted = type(dur_num) != int
        has_stem = dur_num > 1

        # choose the stem direction based on the note's placement on
        # the staff (middle line and above point down)
        if note_num + (7 * octave) > 3:
            stem_dir = 1
        else:
            stem_dir = -1

        # determine the center of the notehead (both must be ints)
        x = int(x)
        y = int(self.bottom_line - self.vspace * note_num - (octave * 7 * self.vspace))

        # store the note's position if it starts a slur
        if "slur" in note_obj.modifiers:
            if not self.slur_start:
                self.slur_start = (x, y)

        # if the note ends a slur, draw it and clear the slur start
        if "end slur" in note_obj.modifiers:
            self.draw_slur(stem_dir, self.slur_start, (x, y))
            self.slur_start = None

        # ties only ever connect two notes, so if there's a starting
        # point, this note has to end it and clear the start point
        if self.tie_start:
            self.draw_slur(stem_dir, self.tie_start, (x, y))
            self.tie_start = None

        if "tie" in note_obj.modifiers:
            self.tie_start = (x, y)

        # draw the appropriately-shaped notehead, with stem if needed;
        # each scale degree has a different head shape
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

        # return the x position of the next note
        return x + space_after

    def draw_barline(self, x, style=""):
        """Draw a barline at the specified x position; if the style is blank,
        draw a regular barline; if "|.", draw a final barline; if "||", a thin
        double bar."""

        # TODO: implement repeat barlines
        
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
        """Set the width of the control to fit complete voice"""
        
        width = sum([int(self.sxt_space) * durations[note.duration]
                     for note in self.voice
                     if "duration" in dir(note)])
        
        self.set_size_request(width + 300, 155)
        
    def draw(self):
        """Draw the voice and horizontally resize the control accordingly"""
        
        self.set_width()
        
        self.draw_staff()
        
        self.draw_clef()
        self.draw_time(self.tune.time)

        # allow enough room for the clef and time signature
        x = self.vspace * 9
        
        for note in self.voice:
            if type(note) == RepeatMarker: # special barlines
                x = self.draw_barline(x, note.text)
            elif self.dc.at_barline(): # regular barlines
                x = self.draw_barline(x)
            if type(note) == Note: # notes and rests
                x = self.draw_note(note,
                                   self.tune.key.split(" ")[1],
                                   x)
                
            else:
                pass #TODO: handle other non-notes

    def redraw_event_handler(self, btn, *args):
        self.draw()

if __name__ == "__main__":
    import sys
    from doremi.doremi_parser import DoremiParser
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

    canvases = []
    
    for voice in tune:
        dc = DoremiCanvas(tune, voice.name)
        canvases.append(dc)
        voice_vbx.pack_start(dc, False)
        
    scroll.add_with_viewport(voice_vbx)
    vbx.pack_start(scroll, True, True, 0)

    def exportem(*args, **kwargs):
        for canvas in canvases:
            canvas.export("%s-%s.jpg" % (tune.title, canvas.voice.name), "jpeg")
            
    btn = gtk.Button("Apply Whatever")
    btn.connect("clicked", exportem)
    vbx.pack_end(btn, False)
    win.show_all()
    win.maximize()
    gtk.main()
