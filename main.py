"""Python implementation of 3D actuated arm experiments, driven by Theano.

Usage:
  main.py [--width=<width>] [--height=<height>]
  main.py [--model-path=<model_path>]
  main.py [--save=<save_path>] [--load=<load_path>] [--save-interval=<save_interval>]
  main.py (-h | --help)

Options:
  -h --help                        Show this screen.
  --width=<width>                  Save path for weights [default: 640].
  --height=<height>                Load path for weights [default: 640].
  --model-path=<model_path>        Path for 3D models [default: models].
  --save-interval=<save_interval>  Interval to save weights (in seconds) [default: 5].
  --save=<save_path>               Save path for weights.
  --load=<load_path>               Load path for weights.
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
        '--model-path': str,
        '--width': Use(int),
        '--height': Use(int),
        '--save-interval': Use(int),
        '--save': Or(None, str),
        '--load': Or(None, os.path.exists),
    })

    try:
        args = schema.validate(args)
    except SchemaError as e:
        exit(e)

    model_path = os.path.abspath(sys.path[0]) + "/" + args['--model-path']

    loadPrcFileData('', 'window-title Arm')
    loadPrcFileData('', 'win-size %d %d' % (args['--width'], args['--height']))
    loadPrcFileData('', 'audio-library-name null') # suppress warning for missing audio device
    loadPrcFileData('', 'model-path %s' % model_path)

    app = App(args)
    app.run()

if __name__ == '__main__':
    main()
