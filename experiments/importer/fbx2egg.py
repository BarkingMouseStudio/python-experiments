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

def get_key_times(curve):
    for t in range(curve.KeyGetCount() if curve is not None else 0):
        yield curve.KeyGet(t).GetTime()

def get_transforms(fbx_node, fbx_layer):
    pos_default = VBase3D(*fbx_node.LclTranslation.Get())
    hpr_default = VBase3D(*fbx_node.LclRotation.Get())
    scale_default = VBase3D(*fbx_node.LclScaling.Get())
    shear_default = VBase3D(0, 0, 0)

    translation_curve = fbx_node.LclTranslation.GetCurve(fbx_layer, False)
    rotation_curve = fbx_node.LclRotation.GetCurve(fbx_layer, False)
    scaling_curve = fbx_node.LclScaling.GetCurve(fbx_layer, False)

    translation_times = get_key_times(translation_curve)
    rotation_times = get_key_times(rotation_curve)
    scaling_times = get_key_times(scaling_curve)

    translations = []
    for key_time in translation_times:
        translation = fbx_node.EvaluateLocalTranslation(key_time)
        translation = VBase3D(translation[0], translation[1], translation[2])
        translations.append(translation)

    rotations = []
    for key_time in rotation_times:
        rotation = fbx_node.EvaluateLocalRotation(key_time)
        # hpr
        # rhp
        rotation = VBase3D(-rotation[2], rotation[0], -rotation[1])
        rotations.append(rotation)

    scalings = []
    for key_time in scaling_times:
        scaling = fbx_node.EvaluateLocalScaling(key_time)
        scaling = VBase3D(scaling[0], scaling[1], scaling[2])
        scalings.append(scaling)

    order = EggXfmSAnim.getStandardOrder() # srpht

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
