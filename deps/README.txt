## THIS FILE ASSUMES:
### - You use Python 2.7
### - If Windows, you have 64-bit Windows and 32-bit Python
### - If Mac, you have an up-to-date installation
### - If Linux, you have a modern 64-bit distro (which means 64-bit python)
# If that is not true, go into each folder and pay attention to exactly what is going on.

go into avbin/install this/ and:
 Windows: copy avbin.dll to C:\Windows\SysWOW64
 Mac/Linux: run appropriate setup

go into pyglet-9781eb46dca2/, and from a shell run 'python setup.py install'
you may need to sudo to root to do that
you MUST use our copy of pyglet, not one you already have! [1]

now you need either PIL or Pillow. [2]
 on Windows: install PIL/PIL-1.1.7.win32-py2.7.exe (for 64bit do Pillow & deps)
 on Mac do: 'pip install Pillow'
 on Linux, apparently you probably already have Pillow installed anyway!


[1] ...for ours is patched to use the PIL image loader as #1 priority, which takes
 map load times from 30 seconds to 0.2 seconds. (this is because Windows loaders load
images upside down, and pyglet's conversion code to fix this is pathologically slow)

[2] the issue is that Pillow is better but doesn't tend to ship a bunch of useful stuff
 that you're going to need to, you know, actually load images.
(for example, we need zlib to load PNGs.)
for release we can sort this out & ship a good static Pillow fairly easily.