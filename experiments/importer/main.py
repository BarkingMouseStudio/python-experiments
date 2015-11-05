import sys

from .fbx2egg import fbx2egg, fbx2egg_animation

def main():
    fbx2egg(sys.argv[1], sys.argv[2])
    fbx2egg_animation(sys.argv[1], sys.argv[3])

if __name__ == '__main__':
    main()
