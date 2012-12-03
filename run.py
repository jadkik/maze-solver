import laby
import os, glob
print 'Available mazes:'
fnames = glob.glob('maze/*.bmp')
for i, fname in enumerate(fnames):
    print '%d- %s' % (i, fname)
i = input('Maze filename (0-%d):' % (len(fnames)-1,))
laby.main(fnames[i])
