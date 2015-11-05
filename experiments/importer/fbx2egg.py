from __future__ import print_function
from __future__ import division

import fbx
import FbxCommon

from pandac.PandaModules import CSDefault, CSZupRight, CSYupRight, CSZupLeft, CSYupLeft, CSInvalid
from panda3d.core import Mat4D, VBase3D, Vec3, Quat, TransformState
from panda3d.egg import EggData, EggTable, EggCoordinateSystem, EggXfmAnimData, EggXfmSAnim, EggGroup, EggTransform

def fbx2egg(fbx_path, egg_path):
    manager, scene = FbxCommon.InitializeSdkObjects()
    FbxCommon.LoadScene(manager, scene, fbx_path)

    data = EggData()
    data.addChild(EggCoordinateSystem(CSYupRight))

    group = EggGroup("walking") # TODO: get name from fbx anim layer
    group.setDartType(EggGroup.DTDefault)

    traverse_joints(scene, scene.GetRootNode(), group)

    data.addChild(group)
    data.writeEgg(egg_path)

def traverse_joints(fbx_scene, fbx_node, egg_parent):
    for i in range(fbx_node.GetChildCount()):
        fbx_child = fbx_node.GetChild(i)

        if fbx_child.GetSkeleton() is None:
            # we're only concerned with the skeleton for now
            continue

        fbx_transform = fbx_child.EvaluateLocalTransform()
        egg_transform = convert_fbx_matrix(fbx_transform)

        egg_joint = EggGroup(fbx_child.GetName())
        egg_joint.setGroupType(EggGroup.GTJoint)
        egg_joint.setTransform3d(egg_transform)

        egg_parent.addChild(egg_joint)

        traverse_joints(fbx_scene, fbx_child, egg_joint)

def convert_fbx_matrix(m):
    return Mat4D(m[0][0], m[0][1], m[0][2], m[0][3], m[1][0], m[1][1], m[1][2], m[1][3], m[2][0], m[2][1], m[2][2], m[2][3], m[3][0], m[3][1], m[3][2], m[3][3])

def fbx2egg_animation(fbx_path, egg_path):
    manager, scene = FbxCommon.InitializeSdkObjects()
    FbxCommon.LoadScene(manager, scene, fbx_path)

    data = EggData()
    data.addChild(EggCoordinateSystem(CSYupRight))

    skeleton = EggTable("<skeleton>")

    walking = EggTable("walking")
    walking.setTableType(EggTable.stringTableType("bundle"))
    walking.addChild(skeleton)

    table = EggTable()
    table.addChild(walking)

    for layer in get_anim_layers(scene):
        traverse_animation_curves(scene, scene.GetRootNode(), layer, skeleton)

    data.addChild(table)
    data.writeEgg(egg_path)

def get_anim_stacks(scene):
    for i in range(scene.GetSrcObjectCount(fbx.FbxAnimStack.ClassId)):
        yield scene.GetSrcObject(fbx.FbxAnimStack.ClassId, i)

def get_anim_layers(scene):
    for stack in get_anim_stacks(scene):
        for i in range(stack.GetMemberCount(fbx.FbxAnimLayer.ClassId)):
            yield stack.GetMember(fbx.FbxAnimLayer.ClassId, i)

def get_curve_values(curve):
    # for key_index in range(curve.KeyGetCount()):
    #     yield curve.KeyGetValue(key_index)
    yield curve.KeyGetValue(0)

def get_curves_channels(curve_node):
    if curve_node is not None:
        for i in range(curve_node.GetChannelsCount()):
            channel = curve_node.GetCurve(i)
            yield list(get_curve_values(channel))

def get_curve_vectors(fbx_node, curve_node):
    if curve_node is not None:
        X = curve_node.GetCurve(curve_node.GetChannelIndex("X")).KeyGetValue(0)
        Y = curve_node.GetCurve(curve_node.GetChannelIndex("Y")).KeyGetValue(0)
        Z = curve_node.GetCurve(curve_node.GetChannelIndex("Z")).KeyGetValue(0)
        yield VBase3D(X, Y, Z)

    # curve_channels = list(get_curves_channels(curve_node))
    # for channels in zip(*curve_channels):
    #     yield VBase3D(*channels)

def get_transforms(fbx_node, fbx_layer):
    translation = fbx_node.LclTranslation
    rotation = fbx_node.LclRotation
    scaling = fbx_node.LclScaling

    pos_default = VBase3D(*translation.Get())
    hpr_default = VBase3D(*rotation.Get())
    scale_default = VBase3D(*scaling.Get())
    shear_default = VBase3D(0, 0, 0)

    translation_curve_node = translation.GetCurveNode(fbx_layer)
    rotation_curve_node = rotation.GetCurveNode(fbx_layer)
    scaling_curve_node = scaling.GetCurveNode(fbx_layer)

    translations = list(get_curve_vectors(fbx_child, translation_curve_node))
    rotations = list(get_curve_vectors(fbx_child, rotation_curve_node))
    scalings = list(get_curve_vectors(fbx_child, scaling_curve_node))

    order = EggXfmSAnim.getStandardOrder()

    for pos, hpr, scale in map(None, translations, rotations, scalings):
        pos = pos or pos_default
        scale = scale or scale_default
        hpr = hpr or hpr_default
        shear = shear_default

        mat = Mat4D()
        EggXfmSAnim.composeWithOrder(mat, scale, shear, hpr, pos, order, CSYupRight)
        yield mat

def traverse_animation_curves(fbx_scene, fbx_node, fbx_layer, egg_parent):
    for i in range(fbx_node.GetChildCount()):
        fbx_child = fbx_node.GetChild(i)

        if fbx_child.GetSkeleton() is None:
            continue

        xform_new = EggXfmSAnim("xform")
        xform_new.setOrder(EggXfmSAnim.getStandardOrder())
        xform_new.setFps(30)

        for transform in get_transforms(fbx_child, fbx_layer):
            xform_new.addData(transform)

        egg_table = EggTable(fbx_child.GetName())
        egg_table.addChild(xform_new)

        egg_parent.addChild(egg_table)

        traverse_animation_curves(fbx_scene, fbx_child, fbx_layer, egg_table)
