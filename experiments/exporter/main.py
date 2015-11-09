import sys

from panda3d.core import loadPrcFileData
from app import App

def main():
    width = 640
    height = 640

    loadPrcFileData('', 'window-title Animate')
    loadPrcFileData('', 'win-size %d %d' % (width, height))
    loadPrcFileData('', 'audio-library-name null') # suppress warning
    loadPrcFileData('', 'model-path %s' % '.')

    model_path = sys.argv[1]
    animation_path = sys.argv[2] if len(sys.argv) > 2 else None

    app = App(width, height, model_path, animation_path)
    app.run()

if __name__ == '__main__':
    main()
