from panda3d.core import loadPrcFileData
from app import App

def main():
    model_path = 'models'
    width = 640
    height = 640

    loadPrcFileData('', 'window-title Animate')
    loadPrcFileData('', 'win-size %d %d' % (width, height))
    loadPrcFileData('', 'audio-library-name null') # suppress warning
    loadPrcFileData('', 'model-path %s' % model_path)

    app = App(width, height)
    app.run()

if __name__ == '__main__':
    main()
