from panda3d.core import VBase4, Vec3, TransformState, LineSegs

class Muscle:

    def __init__(self, max_force):
        self.max_force = max_force

    def drawLineSeg(self, loader, parent, start, end):
        lines = LineSegs()
        lines.setThickness(5.0)
        lines.setColor(VBase4(1, 0.5, 0.5, 1.0))
        lines.moveTo(start)
        lines.drawTo(end)

        np = parent.attachNewNode(lines.create())
        np.setDepthWrite(True)
        np.setDepthTest(True)

    def drawTestCube(self, loader, parent, pos):
        cube = loader.loadModel('cube')
        cube.reparentTo(parent)
        cube.setPos(pos)
        cube.setScale(Vec3(0.1, 0.1, 0.1))
        cube.setColor(VBase4(1, 0.5, 0.5, 1.0))

    def setupDebug(self, loader):
        self.drawTestCube(loader, self.a, self.a_pos)
        self.drawTestCube(loader, self.b, self.b_pos)
        self.drawTestCube(loader, self.a, self.joint_pos)

    def setA(self, a, a_pos):
        self.a = a
        self.a_pos = a_pos

    def setB(self, b, b_pos):
        self.b = b
        self.b_pos = b_pos

    def setJointCenter(self, joint_pos):
        self.joint_pos = joint_pos

    def getAttachmentA(self):
        return self.a.getTransform().compose(TransformState.makePos(self.a_pos)).getPos()

    def getAttachmentB(self):
        return self.b.getTransform().compose(TransformState.makePos(self.b_pos)).getPos()

    def getJointCenter(self):
        return self.a.getTransform().compose(TransformState.makePos(self.joint_pos)).getPos()

    def getMomentArm(self):
        d = self.getAttachmentB() - self.getAttachmentA()
        v = self.getAttachmentA() - self.getJointCenter()
        r = v.cross(d)
        return r

    def apply(self, activation):
        F = activation * self.max_force
        r = self.getMomentArm()

        self.applyTorque(self.a, +F, r)
        self.applyTorque(self.b, -F, r)

    def applyTorque(self, np, F, r):
        T = r * F
        np.node().applyTorque(T)
