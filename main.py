import os
import sys
from panda3d.core import loadPrcFileData

model_path = os.path.abspath(sys.path[0]) + "/models"

width = 600
height = 600

loadPrcFileData('', 'window-title Arm')
loadPrcFileData('', 'win-size %d %d' % (width, height))
loadPrcFileData('', 'audio-library-name null')
loadPrcFileData('', 'model-path %s' % model_path)
loadPrcFileData('', 'show-frame-rate-meter #t')

from app import App

def main():
    app = App(width, height)
    print app.render.ls()
    app.run()

if __name__ == '__main__':
    main()
