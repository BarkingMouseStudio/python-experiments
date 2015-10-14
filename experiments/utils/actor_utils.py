from panda3d.core import LineSegs
from pandac.PandaModules import CharacterJoint

def walk_joints(actor, part, fn, prev=None):
    if isinstance(part, CharacterJoint):
        curr = fn(actor, part)
        yield curr, prev
        prev = curr

    for part_child in part.get_children():
        for next_curr, next_prev in walk_joints(actor, part_child, fn, prev):
            yield next_curr, next_prev

def create_lines(joints, color, thickness=5.0):
    for node, parent in joints:
        if parent is not None:
            lines = LineSegs()
            lines.setThickness(thickness)
            lines.setColor(color)
            lines.moveTo(0, 0, 0)
            lines.drawTo(node.getPos(parent))

            np = parent.attachNewNode(lines.create())
            np.setDepthWrite(False)
            np.setDepthTest(False)

def get_max_joint_angles(actor, joints, animation_name):
    max_angles = [0 for joint in joints]

    actor.pose(animation_name, 0)
    actor.update(force=True)

    frame_count = actor.getNumFrames(animation_name)

    for frame in range(frame_count):
        prev_quat = [node.get_quat(parent) if parent is not None else node.get_quat(actor) for node, parent in joints]

        actor.pose(animation_name, frame)
        actor.update(force=True)

        curr_quat = [node.get_quat(parent) if parent is not None else node.get_quat(actor) for node, parent in joints]

        diff_angles = [curr_quat.angle_deg(prev_quat) for curr_quat, prev_quat in zip(curr_quat, prev_quat)]
        max_angles = [max(math.ceil(diff_angle), max_angle) for diff_angle, max_angle in zip(diff_angles, max_angles)]

    return max_angles

def match_pose(pose_joint_list, control_joint_list):
    for pose_joint_pair, control_joint_pair in zip(pose_joint_list, control_joint_list):
        pose_joint, pose_joint_parent = pose_joint_pair
        control_joint, control_joint_parent = control_joint_pair

        if pose_joint_parent is None:
            # get target pose position and orientation in local space
            pose_pos = pose_joint.get_pos()
            pose_hpr = pose_joint.get_hpr()

            # apply to control joint
            control_joint.set_pos_hpr(pose_pos, pose_hpr)
            continue

        # get target pose position and orientation in local space
        pose_pos = pose_joint.get_pos(pose_joint_parent)
        pose_hpr = pose_joint.get_hpr(pose_joint_parent)

        # apply to control joint
        control_joint.set_pos_hpr(pose_pos, pose_hpr)

def apply_control_joints(control_joint_list, exposed_joint_list):
    for control_joint_pair, exposed_joint_pair in zip(control_joint_list, exposed_joint_list):
        control_joint, control_joint_parent = control_joint_pair
        exposed_joint, exposed_joint_parent = exposed_joint_pair

        control_pos = control_joint.get_pos()
        control_hpr = control_joint.get_hpr()

        if exposed_joint_parent:
            exposed_joint.set_pos_hpr(exposed_joint_parent, control_pos, control_hpr)
        else:
            exposed_joint.set_pos_hpr(control_pos, control_hpr)

def measure_error(control_joint_list, exposed_joint_list):
    err = 0.0
    for control_joint_pair, exposed_joint_pair in zip(control_joint_list, exposed_joint_list):
        control_joint, control_joint_parent = control_joint_pair
        exposed_joint, exposed_joint_parent = exposed_joint_pair

        if control_joint_parent is None or exposed_joint_parent is None:
            continue

        # get target pose position and orientation in local space
        exposed_pos = exposed_joint.get_pos(exposed_joint_parent)
        exposed_quat = exposed_joint.get_quat(exposed_joint_parent)

        control_pos = control_joint.get_pos(control_joint_parent)
        control_quat = control_joint.get_quat(control_joint_parent)

        diff_pos = (exposed_pos - control_pos).length()
        diff_quat = exposed_quat.angle_deg(control_quat)
        err += diff_quat / 180.0

    return err
