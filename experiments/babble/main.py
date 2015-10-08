"""Generate training data for target matching.

Usage:
  main.py [--width=<width>] [--height=<height>] [--headless] <save_path>
  main.py (-h | --help)

Options:
  -h --help                 Show this text.
  --headless                Run in headless mode.
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
        '--headless': bool,
        '--width': Use(int),
        '--height': Use(int),
        '<save_path>': str,
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

    if args['--headless']:
        loadPrcFileData('', 'window-type none')

    app = App(args)
    app.run()

if __name__ == '__main__':
    main()
