#!/usr/bin/env python

from distutils.core import setup

setup(name="ghost-simulator",
      version="0.1",
      packages=['gslib'],
      scripts=['ghost-simulator.py'],
      data_files=[
                  ('gs-chars', ['characters/' + fname for fname in [
                      'bio.txt', 'first_names_f.txt',
                      'first_names_m.txt', 'second_names.txt',
                      'fears_description.txt',
                      'ghostSheet.png']]),
                  ('gs-tiles', ['tiles/' + fname for fname in [
                      'martin.json', 'martin.png', 'field.png',
                      'info_sheet_border_tile.png', 'light.png']]),
                  ('gs-music', ['music/' + fname for fname in [
                      'transylvania.ogg']]),
                  ('gs-sound', ['sound/' + fname for fname in [
                      'scream.ogg']]),
                  ('gs-video', ['video/' + fname for fname in [
                      'default.mpg']])],
                  ('gs-data', ['skills.json', 'credits.txt']),
)
