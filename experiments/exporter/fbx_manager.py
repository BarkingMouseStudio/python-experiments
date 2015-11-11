import fbx
import FbxCommon

class FBXManager:
    def __init__(self):
        self.manager, self.scene = FbxCommon.InitializeSdkObjects()

        scene_info = fbx.FbxDocumentInfo.Create(self.manager, "SceneInfo")
        scene_info.mTitle = "Example scene"
        scene_info.mSubject = "Illustrates the creation and animation of a deformed cylinder."
        scene_info.mAuthor = "ExportScene01.exe sample program."
        scene_info.mRevision = "rev. 1.0"

        self.scene.SetSceneInfo(scene_info)

        self.animation_stack = fbx.FbxAnimStack.Create(self.scene, "Animation Stack")
        self.animation_layer = fbx.FbxAnimLayer.Create(self.scene, "Base Layer")
        self.animation_stack.AddMember(self.animation_layer)

    def setupJoints(self, control_joints):
        self.fbx_nodes = dict()

        for panda_node, panda_parent in control_joints:
            pos = panda_node.getPos()
            hpr = panda_node.getHpr()
            scale = panda_node.getScale()
            name = panda_node.getName()

            skeleton_type = fbx.FbxSkeleton.eRoot if panda_parent is None else fbx.FbxSkeleton.eLimbNode

            fbx_node_attribute = fbx.FbxSkeleton.Create(self.manager, name)
            fbx_node_attribute.SetSkeletonType(skeleton_type)
            fbx_node_attribute.Size.Set(1.0)

            fbx_node = fbx.FbxNode.Create(self.manager, name)
            fbx_node.SetNodeAttribute(fbx_node_attribute)

            fbx_node.LclTranslation.Set(fbx.FbxDouble3(*pos))
            fbx_node.LclRotation.Set(fbx.FbxDouble3(*hpr))
            fbx_node.LclScaling.Set(fbx.FbxDouble3(*scale))

            self.fbx_nodes[name] = fbx_node

        for panda_node, panda_parent in control_joints:
            name = panda_node.getName()
            fbx_node = self.fbx_nodes[name]

            if panda_parent is None:
                self.scene.GetRootNode().AddChild(fbx_node)
            else:
                fbx_parent = self.fbx_nodes[panda_parent.getName()]
                fbx_parent.AddChild(fbx_node)

    def addKeyframe(self, curve, key_index, value):
        time = fbx.FbxTime()
        time.SetFrame(key_index)

        curve.KeyModifyBegin()
        curve.KeyAdd(time)
        curve.KeySet(key_index, time, value, fbx.FbxAnimCurveDef.eInterpolationConstant)
        curve.KeyModifyEnd()

    def setPropKeyframe(self, prop, key_index, values):
        curve_x = prop.GetCurve(self.animation_layer, "X", True)
        curve_y = prop.GetCurve(self.animation_layer, "Y", True)
        curve_z = prop.GetCurve(self.animation_layer, "Z", True)

        self.addKeyframe(curve_x, key_index, values[0])
        self.addKeyframe(curve_y, key_index, values[1])
        self.addKeyframe(curve_z, key_index, values[2])

    def setPropKeyframeRotation(self, prop, key_index, hpr):
        curve_x = prop.GetCurve(self.animation_layer, "X", True)
        curve_y = prop.GetCurve(self.animation_layer, "Y", True)
        curve_z = prop.GetCurve(self.animation_layer, "Z", True)

        self.addKeyframe(curve_x, key_index, hpr[1])
        self.addKeyframe(curve_y, key_index, hpr[2])
        self.addKeyframe(curve_z, key_index, hpr[0])

    def setKeyframe(self, key_index, control_joints):
        for panda_node, panda_parent in control_joints:
            name = panda_node.getName()
            fbx_node = self.fbx_nodes[name]

            pos = panda_node.getPos()
            hpr = panda_node.getHpr()
            scale = panda_node.getScale()

            self.setPropKeyframe(fbx_node.LclTranslation, key_index, pos)
            self.setPropKeyframeRotation(fbx_node.LclRotation, key_index, hpr)
            self.setPropKeyframe(fbx_node.LclScaling, key_index, scale)

    def save(self, fbx_path):
        fbx.FbxAxisSystem.MayaYUp.ConvertChildren(self.scene.GetRootNode(), fbx.FbxAxisSystem.MayaZUp)
        FbxCommon.SaveScene(self.manager, self.scene, fbx_path)
