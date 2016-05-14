from __future__ import print_function

durations = {"16": 1,
             "8": 2,
             "8.5": 3,
             "4": 4,
             "4.": 6,
             "2": 8,
             "2.": 12,
             "1": 16,
             "1.": 24,
             "0": 0}

def measure_duration(time_sig):
    num, denom = [int(part)
                  for part in time_sig.split("/")]
    return int(num * 16 / denom)

class DurationCounter(object):
    def __init__(self, time_sig, partial):
        self.time_sig = time_sig
        self.partial = partial
        self.measure_dur = measure_duration(time_sig)
        self.cur = self.measure_dur - durations[self.partial]
    def reset(self):
        self.cur = self.measure_dur - durations[self.partial]
    def at_barline(self):
        return (self.cur % self.measure_dur) == 0
    def count(self, dur):
        self.cur += durations[dur]
        return self.cur
