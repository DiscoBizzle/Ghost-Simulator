#!/usr/bin/env python

from __future__ import absolute_import, division, print_function

import pyglet

pyglet.options['debug_gl'] = False
#pyglet.options['vsync'] = False
pyglet.options['shadow_window'] = False

from gslib import game

import time

def main():
    # global lasttime
    # global lframes
    # global accumulator
    # lasttime = time.clock()
    # lframes = 0
    # accumulator = 0.0
    # def idle_fun():
    #     global lasttime
    #     global lframes
    #     global accumulator
    #     accumulator += time.clock() - lasttime
    #     lasttime = time.clock()
    #     for w in pyglet.app.windows:
    #         w.on_draw()
    #         w.flip()
    #     #print(str(time.clock() - lasttime) + "seconds passed")
    #     if accumulator > 1.0:
    #         # print(str(lframes) + " FPS")
    #         lframes = 0
    #         accumulator = 0.0
    #     pyglet.clock.tick(False)
    #     lframes += 1
    #
    #     return 0.01
    #
    # pyglet.app.event_loop.idle = idle_fun
    game.Game()
    pyglet.app.run()

if __name__ == '__main__':
    main()
