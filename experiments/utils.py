from __future__ import division

import math
import numpy as np
import cPickle as pickle
import random
import sys

from panda3d.core import Vec3, Quat, PerspectiveLens, ClockObject, DirectionalLight
from pandac.PandaModules import CharacterJoint, LineSegs

from keras.models import model_from_json

def rotate_node(node, dh, dp, dr):
    dq = Quat()
    dq.set_hpr(Vec3(dh, dp, dr))
    q = node.get_quat()
    node.set_quat(q * dq)

def create_lens(aspect_ratio):
    lens = PerspectiveLens()
    lens.setFov(60)
    lens.setAspectRatio(aspect_ratio)
    return lens

def get_angle(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle

get_angle_vec = np.vectorize(get_angle)

def flatten_vectors(arr):
    return np.array([[v.get_x(), v.get_y(), v.get_z()] for v in arr]).flatten()

def draw_joints(joint_list, color):
    for node, parent in joint_list:
        if parent is None:
            continue

        lines = LineSegs()
        lines.set_thickness(3.0)
        lines.set_color(*color)
        lines.move_to(0, 0, 0)
        lines.draw_to(node.get_pos(parent))

        lines_np = parent.attach_new_node(lines.create())
        lines_np.set_bin('fixed', 40)
        lines_np.set_depth_write(False)
        lines_np.set_depth_test(False)

def walk_joints(actor, part, joint_list, parent, node_fn):
    if isinstance(part, CharacterJoint):
        node = node_fn(actor, part)
        joint_list.append((node, parent))
        parent = node

    for child in part.get_children():
        walk_joints(actor, child, joint_list, parent, node_fn)

def filter_joints(joint_list, root_name, exclude):
    filtered_joint_list = []

    root = None
    for node, parent in joint_list:
        if root is None: # found root
            if node.get_name() == root_name:
                filtered_joint_list.append((node, parent))
                root = node
        elif root is parent: # found descendent
            filtered_joint_list.append((node, parent))
            root = node
        else:
            break

    excluded_joint_list = []
    for node, parent in filtered_joint_list:
        if node.get_name() in exclude:
            continue
        excluded_joint_list.append((node, parent))
    return excluded_joint_list

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
        err += (diff_pos / 1.0) + (diff_quat / 180.0)

    return err

def load_model(model_path, weights_path):
    json = open(model_path, 'r').read()
    model = model_from_json(json)
    model.load_weights(weights_path)
    return model
