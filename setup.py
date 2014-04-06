from distutils.core import setup

setup(name="ghost-simulator",
      version="0.1",
      packages=['gslib'],
      scripts=['ghost-simulator.py'],
      data_files=[('gs-chars', ['characters/' + fname for fname in [
          'bio.txt', 'fears.txt', 'first_names_f.txt',
          'first_names_m.txt', 'second_names.txt',
          'fears_description.txt',
          'ghostSheet.png']]),
                  ('gs-tiles', ['tiles/' + fname for fname in [
                      'martin.json', 'martin.png', 'field.png']]),
                  ('gs-music', ['music/' + fname for fname in [
                      'transylvania.ogg']]),
                  ('gs-movies', ['movies/' + fname for fname in [
                      'movie.mpg']])],
)
