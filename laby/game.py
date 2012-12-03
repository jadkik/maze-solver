import pygame
from pygame.locals import *

from .maze import Maze, CAN_CONTINUE, DEAD_END, OUT_OF_RANGE
from .constants import *

import thread, sys

class Game:
    def __init__(self, filename):
        self.__filename = filename

        self.display = pygame.display.set_mode((200, 200), 0, 32)

        self.__screen = pygame.image.load(filename).convert()
        size = self.__screen.get_size()
        self.screen = self.__screen.copy()
        self.display = pygame.display.set_mode([min(size[i], 700) for i in (0,1)], 0, 32) # FULLSCREEN
        self.x, self. y = 0, 0

        print 'Size is: %sx%s' % (size[0], size[1])

        self.__step = 1
        self.__road_start = None
        self.maze = None

        self.__in_thread = False
        
        self.clock = pygame.time.Clock()

    def create_maze(self, step):
        self.maze = Maze(self.__filename, step, True)
        self.maze.onChangeKeyPositions = self.updateScreen
        self.maze.markPosition = self.markPosition
        return True

    def set_init_pos(self, pos):
        if not self.maze:
            print 'No maze. Cannot set Init Position'
            return
        pos = [pos[0]-self.x, pos[1]-self.y]
        try:
            self.maze.start_at(pos)
        except AttributeError, e:
            print e
            return
        else:
            print 'Maze starts at position %s' % (pos,)

    def set_end_pos(self, pos):
        if not self.maze:
            print 'No maze. Cannot set End Position'
            return
        pos = [pos[0]-self.x, pos[1]-self.y]
        try:
            self.maze.end_at(pos)
        except AttributeError, e:
            print e
            return
        else:
            print 'Maze ends at position %s' % (pos,)

    def set_road_length(self, pos):
        if not self.maze:
            print 'No maze. Cannot set End Position'
            return
        pos = [pos[0]-self.x, pos[1]-self.y]
        self.maze.eval_road_length(pos)
        print 'Road length is', self.maze.road_length
        print 'Wall length is', self.maze.wall_length
        #self.maze.road_length /= 2
        #self.maze.wall_length /= 2

    # DISPLAY
    def clearScreen(self):
        self.screen.blit(self.__screen, (0, 0))

    def markPosition(self, pos, tp):
        if tp == 1:
            self.screen.fill(GREEN, (pos, (1, 1)))
        elif tp == 2:
            self.screen.fill(RED, (pos, (2, 2)))
        elif tp == 3:
            self.screen.fill(BLUE, (pos, (2, 2)))
        pygame.display.update()

    def updateScreen(self, last_pt):
        self._old_screen = self.__screen.copy() #self.screen.copy()
        self.screen.blit(self._old_screen, (0, 0))
        self.screen.fill((255, 0, 255), (last_pt.pos, (4, 4)))
        for pt in self.maze.processed_queue:
            self.screen.fill(BLUE, (pt.pos, (3, 3)))
        for pt in self.maze.pos_queue:
            self.screen.fill(GREEN, (pt.pos, (4, 4)))

    def testImage(self):
        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill(RED)
        overlay.set_alpha(40)
        self.screen.blit(overlay, (0, 0))
        pos_iterator = ((x, y) for x in xrange(self.maze.im.size[0]) for y in xrange(self.maze.im.size[1]))
        for pos in pos_iterator:
            ev = self.maze.evaluate_pos(pos)
            if ev == CAN_CONTINUE:
                self.screen.fill(WHITE, (pos, (1, 1)))
            elif ev in (DEAD_END, OUT_OF_RANGE):
                self.screen.fill(BLACK, (pos, (1, 1)))

    def loop(self):
        while True:
            for event in pygame.event.get():
                if event.type == KEYDOWN:
                    if event.key == K_RETURN:
                        self.create_maze(self.__step)
                    elif event.key == K_PAGEUP:
                        self.__step += 1
                    elif event.key == K_PAGEDOWN:
                        self.__step -= 1
                    elif event.key == K_c:
                        self.clearScreen()
                    elif event.key == K_t:
                        #self.testImage()
                        thread.start_new_thread(self.testImage, ())
                    elif event.key == K_SPACE:
                        if not self.maze.started:
                            self.maze.start()
                            # TODO TODO TODO test this shit cause it is not working normally on 400px-shit-stuff-maze
                            #self.maze.wall_length /= 2
                            #self.maze.road_length /= 2
                        else:
                            self.next_step()
                    elif event.key == K_ESCAPE:
                        sys.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    if event.button == 1:
                        self.set_init_pos(event.pos)
                    elif event.button == 2:
                        self.set_road_length(event.pos)
                    elif event.button == 3:
                        self.set_end_pos(event.pos)
            keys = pygame.key.get_pressed()
            if keys[K_UP]:
                self.y += 15
            if keys[K_DOWN]:
                self.y -= 15
            if keys[K_RIGHT]:
                self.x -= 15
            if keys[K_LEFT]:
                self.x += 15
            time_passed = self.clock.tick(20)
            if self.maze is not None and self.maze.started and self.maze.auto_walk:
                self.next_step()
            self.display.fill(WHITE)
            self.display.blit(self.screen, (self.x, self.y))
            pygame.display.update()

    def next_step(self):
        if not self.__in_thread:
            thread.start_new_thread(self._next_step, ())

    def _next_step(self):
        self.__in_thread = True
        pt = self.maze.next_step()
        if pt is not None:
            pos_list = [pt.pos]
            while pt.from_pt is not None:
                pt = pt.from_pt
                pos_list.insert(0, pt.pos)
            pygame.draw.lines(self.screen, (255, 0, 0), False, pos_list, 2)
        self.__in_thread = False
