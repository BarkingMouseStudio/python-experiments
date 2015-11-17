import math

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletSphericalConstraint, BulletHingeConstraint, BulletConeTwistConstraint
from panda3d.core import Vec3, Point3, Quat, TransformState, lookAt, RigidBodyCombiner

def get_joint_pairs(root, joints_config):
    for node_name, joint_config in joints_config.iteritems():
        node = root.find(node_name)

        if 'joints' not in joint_config:
            continue

        joints = joint_config['joints']

        for child_name, child_config in joints.iteritems():
            if child_config['type'] is None:
                continue

            child = root.find(child_name)
            yield (child_config, node, child)

def create_colliders(root, pose_rig, joints_config):
    for node, parent in pose_rig.exposed_joints:
        if node.getName() not in joints_config:
            continue

        joint_config = joints_config[node.getName()]
        if 'joints' not in joint_config:
            continue

        joints = joint_config['joints']
        if len(joints) == 0:
            continue

        mass = joint_config['mass'] if 'mass' in joint_config else 1

        box_rb = BulletRigidBodyNode(node.getName())
        box_rb.setMass(mass)
        box_rb.setLinearDamping(0.2)
        box_rb.setAngularDamping(0.9)
        box_rb.setFriction(1.0)
        box_rb.setAnisotropicFriction(1.0)
        box_rb.setRestitution(0.0)

        for joint in joints:
            child_node, child_parent = next((child_node, child_parent) for child_node, child_parent in pose_rig.exposed_joints if child_node.getName() == joint)

            pos = child_node.getPos(child_parent)
            width = pos.length() / 2.0
            scale = Vec3(3, width, 3)

            shape = BulletBoxShape(scale)

            quat = Quat()
            lookAt(quat, child_node.getPos(child_parent), Vec3.up())
            if len(joints) > 1:
                transform = TransformState.makePosHpr(child_node.getPos(child_parent) / 2.0, quat.getHpr())
            else:
                transform = TransformState.makeHpr(quat.getHpr())
                # transform = TransformState.makeIdentity()

            box_rb.addShape(shape, transform)

        box_np = root.attachNewNode(box_rb)

        if len(joints) > 1:
            pos = node.getPos(pose_rig.actor)
            hpr = node.getHpr(pose_rig.actor)
            box_np.setPosHpr(root, pos, hpr)
        else:
            box_np.setPos(child_parent, child_node.getPos(child_parent) / 2.0)
            box_np.lookAt(child_parent, child_node.getPos(child_parent))

        yield box_np

def create_constraints(root, joint_pairs):
    for joint_config, parent, child in joint_pairs:
        rb_parent = parent.node()
        rb_child = child.node()

        extents_parent = rb_parent.get_shape(0).getHalfExtentsWithMargin()
        extents_child = rb_child.get_shape(0).getHalfExtentsWithMargin()

        if 'offset_parent' in joint_config:
            offset_parent = joint_config['offset_parent']
        else:
            offset_parent = (0, 1, 0)
            offset_parent_x, offset_parent_y, offset_parent_z = offset_parent
            offset_parent = Point3(offset_parent_x * extents_parent.getX(), \
                                   offset_parent_y * extents_parent.getY(), \
                                   offset_parent_z * extents_parent.getZ())

        if 'offset_child' in joint_config:
            offset_child = joint_config['offset_child']
        else:
            offset_child = (0, -1, 0)
            offset_child_x, offset_child_y, offset_child_z = offset_child
            offset_child = Point3(offset_child_x * extents_child.getX(), \
                                  offset_child_y * extents_child.getY(), \
                                  offset_child_z * extents_child.getZ())

        if joint_config['type'] == 'hinge':
            axis_parent = Vec3(*joint_config['axis_parent'])
            axis_child = Vec3(*joint_config['axis_child'])

            constraint = BulletHingeConstraint(rb_parent, rb_child, offset_parent, offset_child, \
                axis_parent, axis_child)

            if 'limit' in joint_config:
                low, high = joint_config['limit']
                softness = 0.0
                bias = 0.0
                relaxation = 1.0
                constraint.setLimit(low, high, softness, bias, relaxation)
        elif joint_config['type'] == 'cone':
            frame_parent = TransformState.makePosHpr(offset_parent, Vec3(90, 0, 0))
            frame_child = TransformState.makePosHpr(offset_child, Vec3(90, 0, 0))

            constraint = BulletConeTwistConstraint(rb_parent, rb_child, frame_parent, frame_child)

            swing1, swing2, twist = joint_config['limit']
            constraint.setLimit(swing1, swing2, twist)
        elif joint_config['type'] == 'spherical':
            constraint = BulletSphericalConstraint(rb_parent, rb_child, offset_parent, offset_child)

        constraint.setDebugDrawSize(3.0)

        yield constraint
