import Image

from .constants import *

CAN_CONTINUE, DEAD_END, OUT_OF_RANGE = range(3)

class Maze:
    def __init__(self, filename, step, auto_walk):
        self.im = Image.open(filename)
        self.pix = self.im.load()

        self.started = False
        self.solved = False
        self.auto_walk = auto_walk
        self.step = step
        self.init_pos = None
        self.end_pos = None
        self.road_length = None
        self.wall_length = None

    def start_at(self, pos):
        #pos = (547, 394)
        if self.init_pos is not None:
            raise AttributeError, "Initial position is already set."
        self.init_pos = pos
        self.markPosition(self.init_pos, 3)

    def end_at(self, pos):
        #pos = (13, 22)
        if self.end_pos is not None:
            raise AttributeError, "End position is already set."
        self.end_pos = pos
        self.markPosition(self.end_pos, 3)

    def eval_road_length(self, pos):
        dir_len = self.get_road_wall_length(pos)
        
        self.road_length = 1+min(dir_len[BOTTOM][0]+dir_len[TOP][0], dir_len[RIGHT][0]+dir_len[LEFT][0])
        self.wall_length = int(sum(dir_len[d][1] for d in dir_len)/len(dir_len))

    # EVALUATION
    def get_next_pos(self, pos, d):
        return (pos[0]+d[0]*self.step, pos[1]+d[1]*self.step)
    
    def nearest_color(self, col, col1, *cols_args):
        cols = [col1]+list(cols_args)
        diff = []
        for c in cols:
            d = map(lambda p: abs(col[p]-c[p]), range(3))
            diff.append((c, d))
        def do_cmp(cd1, cd2):
            c1, d1 = cd1
            c2, d2 = cd2
            d = map(lambda p: d1[p]-d2[p], range(3))
            if d.count(0) == 3:
                return 0
            nearest_to1 = map(lambda p: d1[p]<d2[p], range(3))
            return -1 if nearest_to1.count(True)>=2 else 1
        diff.sort(cmp=do_cmp, reverse=False)
        # TODO working but am not sure how :P
        return diff[0][0]

    def evaluate_pos(self, pos):
        #print 'eval %s' % (pos,)
        self.markPosition(pos, 1)
        try:
            nearest = self.nearest_color(self.pix[pos], BLACK, WHITE)#, BLUE, GREEN, RED)
        except IndexError:
            x, y = pos
            ix, iy = self.im.size
            closest_pos = max(0, min(ix-1, x)), max(0, min(iy-1, y))
            self.markPosition(closest_pos, 3)
            return OUT_OF_RANGE
        else:
            if nearest is WHITE:
                return CAN_CONTINUE
            else:
                return DEAD_END

    def center_pos(self, pos):
        #print 'in', pos
        x, y = pos
        dir_len = self.get_road_wall_length((x, y))
        #print dict([(dir_names[d], dir_len[d]) for d in dir_len])
        dirs = [d for d in (TOP, BOTTOM, LEFT, RIGHT) if dir_len[d][0]<self.road_length]

        if TOP in dirs and BOTTOM in dirs:
            dirs.remove(BOTTOM)
        if LEFT in dirs and RIGHT in dirs:
            dirs.remove(RIGHT)

        for d in dirs:
            #print dir_names[d]
            wall_offset = (self.wall_length-dir_len[d][1])
            center_offset = (dir_len[d][0]-wall_offset)
            distance_to_center = (self.road_length/2)-center_offset
            if d[1] == 0:
                #print 'x -=', d[0]*distance_to_center,'-',(d[0] if d[0]>0 else 0)
                x -= d[0]*distance_to_center-(d[0] if d[0]>0 else 0)
            elif d[0] == 0:
                #print 'y -=', d[1]*distance_to_center,'-',(d[1] if d[1]>0 else 0)
                y -= d[1]*distance_to_center-(d[1] if d[1]>0 else 0)
        return (x, y)

    def get_dir_length(self, pos, d):
        """ Counts in pixels the distance from pos to the nearest
            wall in given direction (at [self.step] pixels precision).
            Note that it does not count the pos pixel itself.
        """
        length = 0
        nxt = pos
        while True:
            nxt = self.get_next_pos(nxt, d)
            if self.evaluate_pos(nxt) in (DEAD_END, OUT_OF_RANGE):
                break
            else:
                length += self.step
        return length

    def get_all_dir_length(self, pos):
        """ Returns a dict containing the dir_length from pos in each direction.
        """
        dirs = {RIGHT: 0, LEFT: 0, TOP: 0, BOTTOM: 0}
        for d in dirs.keys():
            dirs[d] = self.get_dir_length(pos, d)
        return dirs

    def get_road_wall_length(self, pos):
        dir_len = {RIGHT: [0, 0], LEFT: [0, 0], TOP: [0, 0], BOTTOM: [0, 0]}
        for d in dir_len.keys():
            got_to_wall = False
            nxt = pos
            while True:
                nxt = self.get_next_pos(nxt, d)
                ev = self.evaluate_pos(nxt)
                if got_to_wall:
                    if ev == DEAD_END:
                        dir_len[d][1] += 1
                    else:
                        break
                elif ev == DEAD_END:
                    got_to_wall = True
                    dir_len[d][1] += 1
                elif ev == CAN_CONTINUE:
                    dir_len[d][0] += self.step
                elif ev == OUT_OF_RANGE:
                    break
        return dir_len

    def pos_is_close_to_end(self, pos):
        ex, ey = self.end_pos
        rlen = (self.road_length/2.0)**2
        return (pos[0]-ex)**2+(pos[1]-ey)**2<rlen

    # MAIN BRAIN
    def eval_possible_dirs(self, pos):
        dir_len = self.get_all_dir_length(pos)
        self.markPosition(pos, 2)
        dirs = [d for d in (TOP, BOTTOM, LEFT, RIGHT) if dir_len[d]>self.road_length]
        return dirs

    def go_in(self, last_pt, incoming_dir):
        key_pos = []        
        nxt = last_pt.pos
        while True:
            nxt = map(lambda i: nxt[i]+incoming_dir[i]*(self.road_length+self.wall_length), (0,1))
            dirs = self.eval_possible_dirs(nxt)
            print nxt, '->', [dir_names[d] for d in dirs], 'from', dir_names[incoming_dir]

            # TODO TODO TODO keep assertions as is cause they should be verified
            # maybe not the second all the time cause the wall_length for ex may vary from some place to another
            # cause if at first or in the end there is no border wall_length = 0 and some places where there
            # is extra noise on the pic the road length might be smaller by 1 or 2 px
            # but the first shoud definitely be verified unless the key_pos goes over a wall ??

            #assert len(dirs)>=1, 'While going in direction %s from pos %s to %s possible dirs is empty.' % \
            #       (dir_names[incoming_dir], last_pt.pos, nxt)

            #center = self.center_pos(nxt)
            #self.markPosition(center, 3)
            #assert tuple(nxt) == tuple(center), 'Next is not like its center position'

            if self.pos_is_close_to_end(nxt):
                pt = TurningPoint(nxt, incoming_dir, last_pt)
                raise EndReached(pt)
            elif len(dirs) <= 1:
                break
            elif incoming_dir not in dirs:
                pt = TurningPoint(nxt, incoming_dir, last_pt)
                key_pos.insert(0, pt)
                break
            elif len(dirs)>2:
                pt = TurningPoint(nxt, incoming_dir, last_pt)
                key_pos.insert(0, pt)
        return key_pos

    def process(self, pt):
        print 'process %s' % (pt,)
        dirs = self.eval_possible_dirs(pt.pos)
        print '%d possible dirs.' % (len(dirs),)
        disallowed_dir = invertdir(pt.incoming_dir) if pt.incoming_dir is not None else None
        try:
            dirs.remove(disallowed_dir)
        except ValueError:
            pass
        key_pos = []
        for d in dirs:
            dir_key_pos = self.go_in(pt, d)
            key_pos.extend(dir_key_pos)
        print '** Done processing %s. %d key positions found.' % (pt, len(key_pos))
        return key_pos

    def start(self):
        if self.solved: return
        self.init_pos = self.center_pos(self.init_pos)
        self.end_pos = self.center_pos(self.end_pos)

        self.markPosition(self.init_pos, 2)
        #print self.init_pos
        self.markPosition(self.end_pos, 2)
        #print self.end_pos

        pt = TurningPoint(self.init_pos, None, None)
        self.pos_queue = [pt]
        self.processed_queue = []
        self.started = True

        print 'start ()'

    def next_step(self):
        if self.solved: return
        print 'next () -> %d in queue. %d processed.' % \
              (len(self.pos_queue), len(self.processed_queue))
        try:
            pt = self.pos_queue.pop(0)
        except IndexError:
            raise
        self.onChangeKeyPositions(pt)
        assert (pt not in self.processed_queue), 'Point in queue already processed'
        try:
            key_pos = self.process(pt)
        except EndReached as end:
            self.started = False
            self.solved = True
            return end.last_pt
        else:
            self.processed_queue.append(pt)
            key_pos = [pt for pt in key_pos if pt not in self.pos_queue and pt not in self.processed_queue]
            for pt in key_pos:
                self.pos_queue.insert(0, pt)
            return

    def markPosition(self, pos, tp):
        pass

    def onChangeKeyPositions(self, last_pt):
        pass

class TurningPoint:
    def __init__(self, pos, incoming_dir=None, from_pt=None):
        self.pos = pos
        self.from_pt = from_pt
        self.incoming_dir = incoming_dir

    def __eq__(self, pt):
        return self.pos == pt.pos

    def __ne__(self, pt):
        return self.pos != pt.pos

    def __repr__(self):
        return '<TPoint pos=%s from_pos=%s dir=%s>' % (self.pos, self.from_pt.pos if self.from_pt is not None else None, \
                                    None if self.incoming_dir is None else dir_names[self.incoming_dir])

class EndReached(Exception):
    def __init__(self, last_pt):
        self.last_pt = last_pt

    def __str__(self):
        return repr(self.last_pt)
