from direct.actor.Actor import Actor

from panda3d.core import Quat, Vec3

from .utils.actor_utils import walk_joints, create_lines, match_pose, filter_joints
from .config import excluded_joints

class ControlJointRig:
    def __init__(self, model_name):
        self.actor = Actor(model_name)

        exposed_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.getName()))
        control_joint_gen = walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), \
            lambda actor, part: actor.controlJoint(None, 'modelRoot', part.getName()))

        self.exposed_joints = filter_joints(exposed_joint_gen, excluded_joints)
        self.control_joints = filter_joints(control_joint_gen, excluded_joints)

    def createLines(self, color):
        create_lines(self.exposed_joints, color)

    def setRoot(self, name):
        self.root = [node for node, parent in self.control_joints if node.getName() == name][0]

    def setPos(self, x, y, z):
        self.actor.setPos(x, y, z)

    def reparentTo(self, other):
        self.actor.reparentTo(other)

    def matchRoot(self, pose_rig):
        self.root.setPosHpr(pose_rig.root.getPos(self.actor), \
            pose_rig.root.getHpr(self.actor))

    def matchPose(self, pose_rig):
        match_pose(pose_rig.exposed_joints, self.control_joints, True)

    def matchPhysicalPose(self, render, loader, physical_rig):
        for collider_parent_pair, node_parent_pair in zip(physical_rig.collider_parents, self.control_joints):
            collider, collider_parent = collider_parent_pair
            node, node_parent = node_parent_pair

            if node_parent is not None:
                half_extents_parent = collider_parent.node().getShape(0).getHalfExtentsWithMargin()
                half_extents_child = collider.node().getShape(0).getHalfExtentsWithMargin()

                print '+=++=++=++=++=++=++=+'
                print node, node.getPos(), node.getHpr()

                # rotation_node = node.getQuat()
                # endpoint_node = node.getPos()
                # print rotation_node.xform(endpoint_node)

                rotation_parent = collider_parent.getQuat()
                midpoint_parent = collider_parent.getPos()
                endpoint_parent = midpoint_parent + rotation_parent.xform(Vec3(0, half_extents_parent.getY(), 0))

                rotation = collider.getQuat()
                midpoint = collider.getPos()
                endpoint = midpoint + rotation.xform(Vec3(0, half_extents_child.getY(), 0))

                model = loader.loadModel('cube.egg')

                if collider.getName() == 'RightArm':
                    model.setColor(1, 0, 0)

                if collider.getName() == 'RightForeArm':
                    model.setColor(0, 1, 0)

                if collider.getName() == 'RightHand':
                    model.setColor(0, 0, 1)

                model.reparentTo(render)
                model.setPos(midpoint)
                model.setQuat(rotation)

                # print (endpoint_parent - endpoint).length(), node.getPos().length()

                # rotation_parent.invertInPlace()
                # rotation.invertInPlace()
                print collider.getName(), collider_parent.getName()
                print node.getName(), node_parent.getName()

                # node.setPos(endpoint)
                # node.setHpr(collider.getHpr(collider_parent))
            # else:
            #     node.setPosHpr(collider.getPos(), collider.getHpr())

    def getJointPositions(self):
        return np.concatenate([node.getPos(parent) if parent is not None else node.getPos() for node, parent in self.exposed_joints])

    def getJointRotations(self):
        return np.concatenate([node.getHpr(parent) if parent is not None else node.getHpr() for node, parent in self.exposed_joints])
