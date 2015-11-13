from panda3d.core import LineSegs
from pandac.PandaModules import CharacterJoint

def get_parents(exposed_joints):
    child_parent = dict()
    for child, parent in exposed_joints:
        if parent is not None:
            child_parent[child.getName()] = parent.getName()

    parents = dict()
    for child, parent in child_parent.iteritems():
        parents[child] = child_parents = []
        while parent is not None:
            child_parents.append(parent)
            parent = child_parent[parent] if parent in child_parent else None
    return parents

def walk_joints(actor, part, part_parent=None):
    if isinstance(part, CharacterJoint):
        yield part, part_parent

    for part_child in part.getChildren():
        for child_part, child_part_parent in walk_joints(actor, part_child, part):
            yield child_part, child_part_parent

def map_joints(actor, part, fn, prev=None):
    if isinstance(part, CharacterJoint):
        curr = fn(actor, part)
        yield curr, prev
        prev = curr

    for part_child in part.getChildren():
        for next_curr, next_prev in map_joints(actor, part_child, fn, prev):
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
            np.setDepthWrite(True)
            np.setDepthTest(True)

def filter_joints(joint_gen, excluded_joints):
    joints = []
    for node, parent in joint_gen:
        if node.get_name() not in excluded_joints:
            joints.append((node, parent))
    return joints

def match_pose(pose_joints, control_joints, is_relative=False):
    for pose_joint_pair, control_joint_pair in zip(pose_joints, control_joints):
        pose_joint, pose_joint_parent = pose_joint_pair
        control_joint, control_joint_parent = control_joint_pair

        if pose_joint_parent is not None:
            if is_relative:
                pose_pos = pose_joint.getPos(pose_joint_parent)
                pose_hpr = pose_joint.getHpr(pose_joint_parent)
            else:
                pose_pos = pose_joint.getPos()
                pose_hpr = pose_joint.getHpr()
            control_joint.setPosHpr(pose_pos, pose_hpr)
        else:
            pose_pos = pose_joint.getPos()
            pose_hpr = pose_joint.getHpr()
            control_joint.setPosHpr(pose_pos, pose_hpr)
            continue

# def get_max_joint_angles(actor, joints, animation_name):
#     max_angles = [0 for joint in joints]
#
#     actor.pose(animation_name, 0)
#     actor.update(force=True)
#
#     frame_count = actor.getNumFrames(animation_name)
#
#     for frame in range(frame_count):
#         prev_quat = [node.get_quat(parent) if parent is not None else node.get_quat(actor) for node, parent in joints]
#
#         actor.pose(animation_name, frame)
#         actor.update(force=True)
#
#         curr_quat = [node.get_quat(parent) if parent is not None else node.get_quat(actor) for node, parent in joints]
#
#         diff_angles = [curr_quat.angle_deg(prev_quat) for curr_quat, prev_quat in zip(curr_quat, prev_quat)]
#         max_angles = [max(math.ceil(diff_angle), max_angle) for diff_angle, max_angle in zip(diff_angles, max_angles)]
#
#     return max_angles

def apply_control_joints(control_joint_list, exposed_joint_list):
    for control_joint_pair, exposed_joint_pair in zip(control_joint_list, exposed_joint_list):
        control_joint, control_joint_parent = control_joint_pair
        exposed_joint, exposed_joint_parent = exposed_joint_pair

        control_pos = control_joint.getPos()
        control_hpr = control_joint.getHpr()

        if exposed_joint_parent:
            exposed_joint.setPosHpr(exposed_joint_parent, control_pos, control_hpr)
        else:
            exposed_joint.setPosHpr(control_pos, control_hpr)
