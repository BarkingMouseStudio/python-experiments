import math

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletSphericalConstraint, BulletHingeConstraint, BulletConeTwistConstraint
from panda3d.core import Vec3, Point3, TransformState

def get_joint_pairs(root, joints_config):
    for key_parent in joints_config:
        joint_config_parent = joints_config[key_parent]
        parent = root.find(key_parent)

        if 'joints' in joint_config_parent:
            for key_child in joint_config_parent['joints']:
                joint_config_child = joint_config_parent['joints'][key_child]
                other = root.find(key_child)
                yield (joint_config_child, parent, other)

def create_colliders(root, exposed_joints, joints_config):
    for node, parent in exposed_joints:
        node_name = node.get_name()

        joint_config = joints_config[node_name] if node_name in joints_config else None
        mass = joint_config['mass'] if joint_config is not None and 'mass' in joint_config else 1

        joint_pos = node.getPos(parent) if parent is not None else node.getPos()
        joint_midpoint = joint_pos / 2.0
        joint_length = joint_pos.length()
        joint_width = joint_length / 2.0 if joint_length > 0 else mass

        dims = math.sqrt(mass)
        box_scale = Vec3(dims, joint_width, dims)

        box_rb = BulletRigidBodyNode(node_name)
        box_rb.setMass(mass)
        box_rb.addShape(BulletBoxShape(box_scale))
        box_rb.setLinearDamping(0.2)
        box_rb.setAngularDamping(0.9)
        box_rb.setFriction(0.2)

        box_np = root.attachNewNode(box_rb)

        # align rigidbody with relative position node
        if parent is not None:
            box_np.setPos(parent, joint_midpoint)
            box_np.lookAt(parent, node.getPos(parent))
        else:
            box_np.setPos(joint_midpoint)
            box_np.lookAt(node)

        yield box_np

def create_constraints(root, joint_pairs):
    for joint_config, parent, child in joint_pairs:
        rb_parent = parent.node()
        rb_child = child.node()

        extents_parent = rb_parent.get_shape(0).getHalfExtentsWithMargin()
        extents_child = rb_child.get_shape(0).getHalfExtentsWithMargin()

        offset_parent = (0, 1, 0)
        if 'offset_parent' in joint_config:
            offset_parent = joint_config['offset_parent']
        offset_parent_x, offset_parent_y, offset_parent_z = offset_parent
        offset_parent = Point3(offset_parent_x * extents_parent.getX(), \
                               offset_parent_y * extents_parent.getY(), \
                               offset_parent_z * extents_parent.getZ())

        offset_child = (0, -1, 0)
        if 'offset_child' in joint_config:
            offset_child = joint_config['offset_child']
        offset_child_x, offset_child_y, offset_child_z = offset_child
        offset_child = Point3(offset_child_x * extents_child.getX(), \
                              offset_child_y * extents_child.getY(), \
                              offset_child_z * extents_child.getZ())

        if joint_config['type'] == 'hinge':
            axis_parent = Vec3(*joint_config['axis_parent'])
            axis_child = Vec3(*joint_config['axis_child'])

            constraint = BulletHingeConstraint(rb_parent, rb_child, offset_parent, offset_child, \
                axis_parent, axis_child)

            low, high = joint_config['limit']
            constraint.setLimit(low, high)
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
