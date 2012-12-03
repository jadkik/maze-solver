import traceback, sys

try:
    execfile('run.py')
except KeyboardInterrupt:
    sys.exit()
except Exception:
    traceback.print_exc()

print '[DONE EXECUTION]'
try:
    while True: pass
except KeyboardInterrupt:
    sys.exit()
