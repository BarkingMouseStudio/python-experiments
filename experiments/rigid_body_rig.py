import random

from panda3d.core import NodePath, Vec3
from pandac.PandaModules import CharacterJoint

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletSphericalConstraint
from pandac.PandaModules import CharacterJoint

from .utils.physics_utils import create_constraints, create_colliders
from .config import joints_config, excluded_joints, center_joints

class RigidBodyRig:

    def __init__(self, control_rig):
        self.root = NodePath('root')

        self.colliders = create_colliders(self.root, control_rig.exposed_joints, joints_config)
        self.constraints = create_constraints(self.get_joint_pairs())

    def attachCubes(self, loader):
        for collider in self.colliders:
            scale = collider.node().get_shape(0).getHalfExtentsWithMargin()
            model = loader.loadModel('cube.egg')
            model.reparentTo(collider)
            model.setScale(scale)

    def apply_virtual_forces(self, gravity):
        for joint_name, mass in center_joints.iteritems():
            rb = self.root.find(joint_name).node()
            rb.applyCentralForce(-gravity * mass)

    def babble(self, torque_min, torque_max):
        for child in self.root.getChildren():
            T_local = Vec3(0, 0, random.random() * 10000.0)
            T_world = child.getQuat(self.root).xform(T_local)
            child.node().applyTorque(T_world)

    def matchPose(self, pose_rig):
        for node, parent in pose_rig.exposed_joints:
            if parent is None:
                continue

            box_np = self.root.find(node.get_name())
            box_rb = box_np.node()

            box_np.reparentTo(parent)
            box_np.setPos(node.get_pos(parent) / 2.0)
            box_np.lookAt(node)

            box_np.reparentTo(self.root)

    def reparentTo(self, other):
        self.root.reparentTo(other)

    def setCollideMask(self, mask):
        for child in self.root.getChildren():
            child.setCollideMask(mask)

    def attachRigidBodies(self, world):
        for collider in self.colliders:
            world.attachRigidBody(collider.node())

    def attachConstraints(self, world):
        for constraint in self.constraints:
            world.attachConstraint(constraint, linked_collision=True)

    def get_joint_pairs(self):
        for key_parent in joints_config:
            joint_config_parent = joints_config[key_parent]
            parent = self.root.find(key_parent)
            rb_parent = parent.node()

            if 'joints' in joint_config_parent:
                for key_child in joint_config_parent['joints']:
                    joint_config_child = joint_config_parent['joints'][key_child]
                    other = self.root.find(key_child)
                    rb_child = other.node()
                    yield (joint_config_child, rb_parent, rb_child)
