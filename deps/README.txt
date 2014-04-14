## THIS FILE ASSUMES:
### - You use Python 2.7
### - If Windows, you have 64-bit Windows and 32-bit Python
### - If Mac, you have an up-to-date installation
### - If Linux, you have a modern 64-bit distro (which means 64-bit python)
# If that is not true, go into each folder and pay attention to exactly what is going on.

1. go into avbin/install this/ and:
 Windows: copy avbin.dll to C:\Windows\SysWOW64
 Mac/Linux: run appropriate setup

2. go into pyglet-9781eb46dca2/, and from a shell run 'python setup.py install'
you may need to sudo to root to do that
you MUST use our copy of pyglet, not one you already have! [1]

3. now you need either PIL or Pillow. [2]
 on Windows: install PIL/PIL-1.1.7.win32-py2.7.exe (for 64bit do Pillow & deps)
 on Mac do: 'sudo easy_install pip' and then 'sudo pip install Pillow'
 on Linux, apparently you probably already have Pillow installed anyway!

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

[1] ...for ours is patched to use the PIL image loader as #1 priority, which takes
 map load times from 30 seconds to 0.2 seconds. (this is because Windows loaders load
images upside down, and pyglet's conversion code to fix this is pathologically slow)

[2] the issue is that Pillow is better but doesn't tend to ship a bunch of useful stuff
 that you're going to need to, you know, actually load images.
(for example, we need zlib to load PNGs.)
for release we can sort this out & ship a good static Pillow fairly easily.
