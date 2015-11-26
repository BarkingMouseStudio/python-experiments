"""Generate training data for target matching.

Usage:
  main.py [--width=<width>] [--height=<height>]
  main.py (-h | --help)

Options:
  -h --help                 Show this text.
  --width=<width>           Save path for weights [default: 640].
  --height=<height>         Load path for weights [default: 640].
"""

import os
import sys
from docopt import docopt
from schema import Schema, Or, Use, SchemaError
from panda3d.core import loadPrcFileData

from app import App

def main():
    args = docopt(__doc__)

    schema = Schema({
        '--help': bool,
        '--width': Use(int),
        '--height': Use(int),
    })

    try:
        args = schema.validate(args)
    except SchemaError as e:
        exit(e)

    model_path = 'models'

    loadPrcFileData('', 'window-title Babble')
    loadPrcFileData('', 'win-size %d %d' % (args['--width'], args['--height']))
    loadPrcFileData('', 'audio-library-name null') # suppress warning
    loadPrcFileData('', 'model-path %s' % model_path)
    loadPrcFileData('', 'bullet-filter-algorithm groups-mask')
    # loadPrcFileData('', 'framebuffer-multisample 1')
    # loadPrcFileData('', 'multisamples 1')

    app = App(args)
    app.run()

if __name__ == '__main__':
    main()
