## THIS FILE ASSUMES:
### - You use Python 2.7
### - If Windows, you have 64-bit Windows and 32-bit Python
### - If Mac, you have an up-to-date installation
### - If Linux, you have a modern 64-bit distro (which means 64-bit python)
# If that is not true, go into each folder and pay attention to exactly what is going on.

===== DO THESE THINGS =====

1. go into avbin/install this/ and:
 Windows: copy avbin.dll to C:\Windows\SysWOW64
 Mac/Linux: run appropriate setup

2. go into pyglet-9781eb46dca2/, and from a shell run 'python setup.py install'
you may need to sudo to root to do that
you MUST use our copy of pyglet, not one you already have! [1]

 
=== BONUS MATERIAL FOR 64-BIT PYTHON ON 64-BIT WINDOWS / ANY LINUX ===
(you probably have 32-bit python on 64-bit windows)

A. Only on Linux, you should go ahead and install openal-soft from your Linux distro
 as otherwise you'll probably end up using ALSA which lacks some features.
 Also, the reference OpenAL impl (NOT openal-soft) is buggy and crap and somehow
  manages to make sounds not play in stereo, so don't use that.
This is untested. Someone please get back to me on whether it works or not.

B. On 64-bit Windows with 64-bit Python, you're going to run into the bug:
 https://code.google.com/p/pyglet/issues/detail?id=664
...which hasn't been fixed yet.
Basically you're going to get intermittent crashes on load in the font code.
Rerun, go 32-bit, or somehow fix the problem.

[1] we took the liberty of hacking pyglet.media to not hang when videos end.
we have destroyed the functionality that allows you to queue files to be played
 one after the other, though... though this should be easy to re-implement from the
 outside. (just start a new file in a new Player once the existing one is used)
