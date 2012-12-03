maze-solver
===========

Maze Solver based on image input.

There are a bunch of images from around the web in the maze/ directory.
When you run the solver, you'll get to choose from one of those. Some will work immediately, some will take some time.
And some will fail really bad...

How to use
==========

  1. Run runExec.py
  2. Choose an image file. Start with one of the simple ones.
  3. Press Enter to create a new "Maze" object.
  4. Left click on the start position on the picture.
  5. Right clcik on the end position on the picture.
  6. Middle click on some "road", so that it detects how wide the road is.
  7. Hit space and let it run!
  8. Enjoy.

The code is kind of a mess, or maybe a total mess. But it's half working ;) So all is good, but slow.

If you were to remove the UI part and the printing to standard output part, it might get a lot faster.
And the UI's pretty much separated from the logic part...