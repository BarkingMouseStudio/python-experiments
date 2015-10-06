from pandac.PandaModules import *

loadPrcFileData('', 'interpolate-frames #t')

import direct.directbase.DirectStart
from direct.directtools.DirectGrid import DirectGrid

from direct.actor.Actor import Actor
import random

root = NodePath('root')
root.reparent_to(render)
root.set_scale(0.1)
root.set_pos(0, 0, 9)

grid = DirectGrid(parent=render)
grid.set_scale(0.5)

actor = Actor('models/walking.egg', {
    'walk': 'models/walking-animation.egg'
})
actor.reparentTo(root)
actor.setBin('background', 1)

def walkJointHierarchy(actor, part, parentNode = None, indent = ''):
    if isinstance(part, CharacterJoint):
        node = actor.exposeJoint(None, 'modelRoot', part.getName())

        if parentNode and parentNode.getName() != 'root':
            lines = LineSegs()
            lines.setThickness(3.0)
            lines.setColor(random.random() * 0.5, random.random() * 0.75, 1)
            lines.moveTo(0, 0, 0)
            lines.drawTo(node.getPos(parentNode))

            lnode = parentNode.attachNewNode(lines.create())
            lnode.setBin('fixed', 40)
            lnode.setDepthWrite(False)
            lnode.setDepthTest(False)

        parentNode = node

    for child in part.getChildren():
        walkJointHierarchy(actor, child, parentNode, indent + '  ')

walkJointHierarchy(actor, actor.getPartBundle('modelRoot'), None)

actor.loop('walk')
base.cam.setY(-50)

base.run()
