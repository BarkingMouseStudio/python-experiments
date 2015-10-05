from pandac.PandaModules import *

loadPrcFileData("", "interpolate-frames #t")

import direct.directbase.DirectStart
from direct.actor.Actor import Actor
from random import random

actor = Actor("models/walk.egg", {
    "walk": "models/walk-animation.egg"
})
actor.reparentTo(render)
actor.setBin('background', 1)

def walkJointHierarchy(actor, part, parentNode = None, indent = ""):
    if isinstance(part, CharacterJoint):
        node = actor.exposeJoint(None, 'modelRoot', part.getName())

        if parentNode and parentNode.getName() != "root":
            lines = LineSegs()
            lines.setThickness(3.0)
            lines.setColor(random(), random(), 1)
            lines.moveTo(0, 0, 0)
            lines.drawTo(node.getPos(parentNode))

            lnode = parentNode.attachNewNode(lines.create())
            lnode.setBin("fixed", 40)
            lnode.setDepthWrite(False)
            lnode.setDepthTest(False)

        parentNode = node

    for child in part.getChildren():
        walkJointHierarchy(actor, child, parentNode, indent + "  ")

walkJointHierarchy(actor, actor.getPartBundle('modelRoot'), None)

actor.loop("walk")
base.cam.setY(-50)

base.run()
