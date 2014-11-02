should add controls to change auto-walk value
+ add controls to save image / hide processed pos / hide key pos / hide mark positions / save solution / save cleaned image ...
no more hard coded thingy except for the auto-walk value
+ fullscreen thingy

ok so now i made some testing changes, the start point and road length are predefined (hard-coded) for fast testing


controls:
enter to start - this now also sets default road length and start pos
up/down arrows - changes the step now also hard coded for better testing
space - next step makes the next step on a new thread which makes possible the raw_input() pause without bugging the whole thing.