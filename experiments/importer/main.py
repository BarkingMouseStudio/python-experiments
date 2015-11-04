from __future__ import print_function
from __future__ import division

import sys

import fbx
import FbxCommon

from pandac.PandaModules import CSYupRight
from panda3d.core import Mat4D, VBase3D, Vec3, TransformState
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

def convert_fbx_matrix(m):
    return Mat4D(m[0][0], m[0][1], m[0][2], m[0][3], m[1][0], m[1][1], m[1][2], m[1][3], m[2][0], m[2][1], m[2][2], m[2][3], m[3][0], m[3][1], m[3][2], m[3][3])

def get_curve_values(curve):
    # for key_index in range(curve.KeyGetCount()):
    #     yield curve.KeyGetValue(key_index)
    yield curve.KeyGetValue(0)

def get_curves_channels(curve_node):
    if curve_node is not None:
        for i in range(curve_node.GetChannelsCount()):
            yield list(get_curve_values(curve_node.GetCurve(i)))

def get_curve_vectors(curve_node):
    curve_channels = list(get_curves_channels(curve_node))
    for channels in zip(*curve_channels):
        yield VBase3D(*channels)

def get_transforms(translation_curve_node, rotation_curve_node, scaling_curve_node):
    translations = list(get_curve_vectors(translation_curve_node))
    rotations = list(get_curve_vectors(rotation_curve_node))
    scalings = list(get_curve_vectors(scaling_curve_node))

    for pos, hpr, scale in map(None, translations, rotations, scalings):
        if pos is None:
            pos = VBase3D(0, 0, 0)
        if hpr is None:
            hpr = VBase3D(0, 0, 0)
        if scale is None:
            scale = VBase3D(1, 1, 1)

        shear = VBase3D(0, 0, 0)
        order = EggXfmSAnim.getStandardOrder()
        cs = CSYupRight

        mat = Mat4D()
        EggXfmSAnim.composeWithOrder(mat, scale, shear, hpr, pos, order, cs)
        yield mat

def traverse_animation_curves(fbx_scene, fbx_node, fbx_layer, egg_parent):
    for i in range(fbx_node.GetChildCount()):
        fbx_child = fbx_node.GetChild(i)

        if fbx_child.GetSkeleton() is None:
            continue

        xform_new = EggXfmSAnim("xform")
        xform_new.setOrder(EggXfmSAnim.getStandardOrder())
        # xform_new.setFps(30)

        translation_curve_node = fbx_child.LclTranslation.GetCurveNode(fbx_layer)
        rotation_curve_node = fbx_child.LclRotation.GetCurveNode(fbx_layer)
        scaling_curve_node = fbx_child.LclScaling.GetCurveNode(fbx_layer)

        for transform in get_transforms(translation_curve_node, rotation_curve_node, scaling_curve_node):
            xform_new.addData(transform)

        # xform_new.normalize()

        egg_table = EggTable(fbx_child.GetName())
        egg_table.addChild(xform_new)

        egg_parent.addChild(egg_table)

        traverse_animation_curves(fbx_scene, fbx_child, fbx_layer, egg_table)

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

def actor2fbx(fbx_path):
    # manager, scene = FbxCommon.InitializeSdkObjects()
    # TODO: write fbx from Actor
    # FbxCommon.SaveScene(manager, scene, fbx_path)
    pass

def main():
    # fbx2egg(sys.argv[1], sys.argv[2])
    fbx2egg_animation(sys.argv[1], sys.argv[2])

if __name__ == '__main__':
    main()
