class Rig:

    # TODO: root motion
    def __init__(self, is_control=False):
        self.actor = Actor('walk.egg', { 'walk': 'walk-animation.egg' })

        self.exposed_joints = []
        walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), self.exposed_joints, None, lambda actor, part: actor.exposeJoint(None, 'modelRoot', part.get_name()))
        draw_joints(self.exposed_joints)

        if is_control:
            self.control_joints = []
            walk_joints(self.actor, self.actor.getPartBundle('modelRoot'), self.control_joints, None, lambda actor, part: actor.controlJoint(None, 'modelRoot', part.get_name()))

    def get_joint_pos(self):
        joint_pos = []
        for node, parent in self.joints:
            if parent is not None:
                pos = node.get_pos(parent)
            else:
                pos = node.get_pos(self.actor)
            joint_pos.append(pos)
        return np.array(joint_pos)

    def get_joint_hpr(self):
        joint_hpr = []
        for node, parent in self.joints:
            if parent is not None:
                pos = node.get_hpr(parent)
            else:
                pos = node.get_hpr(self.actor)
            joint_hpr.append(pos)
        return np.array(joint_hpr)

        linear_velocities = [joint_position - prev_joint_position for joint_position, prev_joint_position in zip(joint_positions, self.prev_joint_positions)]
        angular_velocities = [joint_rotation - prev_joint_rotation for joint_rotation, prev_joint_rotation in zip(joint_rotations, self.prev_joint_rotations)]
        next_joint_positions = [node.get_pos(parent) if parent is not None else node.get_pos(self.control_rig) for node, parent in self.joint_list]
        next_joint_rotations = [node.get_hpr(parent) if parent is not None else node.get_hpr(self.control_rig) for node, parent in self.joint_list]
