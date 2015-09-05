# -*- coding: utf-8 -*-

class TimeStamp(object):

    def __init__(self, frog, frog_ai, hydrophytes, flies):
        self.frog_state = frog.get_state()
        if frog_ai is not None:
            self.frog_ai_state = frog_ai.get_state()
        self.hydrophytes_state = [hp.get_state() for hp in hydrophytes]
        self.flies = [fl.get_state() for fl in flies]

    def make_it_reality(self, frog, frog_ai, hydrophytes, flies, frogsbar):
        frog.set_state(self.frog_state)
        if frog_ai is not None:
            frog_ai.set_state(self.frog_ai_state)
        for i, hp in enumerate(hydrophytes):
            hp.set_state(self.hydrophytes_state[i])
        for i, fl in enumerate(flies):
            fl.set_state(self.flies[i])
        fp = frog.get_position_p()
        frogsbar.set_corner((fp[0] - 25, fp[1] - 40))


class TimeMachine(object):

    def __init__(self, capacity):
        self.timestamps = [None] * capacity
        self.curr_point = None
        self.genesis = None
        self.capacity = capacity

    def set_genesis(self, timestamp):
        self.curr_point = 0
        self.genesis = 0
        self.timestamps[0] = timestamp

    def _get_next_point(self):
        return (self.curr_point + 1) % self.capacity

    def _get_previous_point(self):
        return (self.curr_point - 1) % self.capacity

    def add_timestamp(self, timestamp):
        next_point = self._get_next_point()
        if next_point == self.genesis:
            self.genesis = (self.genesis + 1) % self.capacity
        self.timestamps[next_point] = timestamp
        self.curr_point = next_point

    def get_previous_timestamp(self): # returns None iff couldn't get previous
        assert self.curr_point != self.genesis

        prev_point = self._get_previous_point()
        if prev_point == self.genesis:
            return None
        assert self.timestamps[prev_point] is not None
        self.curr_point = prev_point
        return self.timestamps[prev_point]

    def stop_travelling(self):
        self.genesis = self.curr_point