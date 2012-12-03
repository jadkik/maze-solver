RED, GREEN, BLUE = (255, 0, 0), (0, 255, 0), (0, 0, 255)
BLACK, WHITE = (0, 0, 0), (255, 255, 255)

def makedir(d):
    return (d[0], d[1])
def invertdir(d):
    return (-d[0], -d[1])

RIGHT, LEFT, TOP, BOTTOM = map(makedir, [(1, 0), (-1, 0), (0, -1), (0, 1)])
dir_names = {RIGHT: 'R', LEFT: 'L', TOP: 'T', BOTTOM: 'B'}
