import math

from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletSphericalConstraint
from panda3d.core import Vec3, Point3

def create_colliders(root, exposed_joints, joints_config):
    colliders = []

    for node, parent in exposed_joints:
        if parent is None:
            continue

        node_name = node.get_name()

        joint_config = joints_config[node_name] if node_name in joints_config else None
        mass = joint_config['mass']

        joint_pos = node.get_pos(parent)
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

        # align rigidbody with relative position node
        np = parent.attachNewNode(box_rb)
        np.setPos(joint_midpoint)
        np.lookAt(node)

        # reparent to root
        box_np = root.attachNewNode(box_rb)
        np.removeNode() # cleanup relative position node

        colliders.append(box_np)

    return colliders

def create_constraints(joint_pairs):
    constraints = []

    for joint_config, rb_parent, rb_child in joint_pairs:
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

        constraint = BulletSphericalConstraint(rb_parent, rb_child, offset_parent, offset_child)
        constraint.setDebugDrawSize(3.0)

        constraints.append(constraint)

    return constraints
