class RigidBodyRig:

    def __init__(self, exposed_joints):
        self.root = NodePath('root')
        # self.walk_joints(actor, actor.getPartBundle('modelRoot'), [])
        # self.constrain_joints(self.physical_rig, self.world)
        # self.disable_collisions(self.physical_rig, self.floor, self.world)

    def constrain_joints(self, root, world):
        for joint_config, rb_parent, rb_child in self.get_joint_pairs(root):
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

            cs = BulletSphericalConstraint(rb_parent, rb_child, offset_parent, offset_child)
            cs.setDebugDrawSize(3.0)
            world.attachConstraint(cs, linked_collision=True)

    def disable_collisions(self, root, floor, world):
        for i in range(32):
            world.setGroupCollisionFlag(i, i, False)

        proxy_group = BitMask32.bit(0)
        floor_group = BitMask32.bit(1)

        world.setGroupCollisionFlag(0, 1, True)

        for child in root.getChildren():
            child.setCollideMask(proxy_group)

        floor.setCollideMask(floor_group)

    def get_joint_pairs(self, root):
        for key_parent in joints_config:
            joint_config_parent = joints_config[key_parent]
            parent = root.find(key_parent)
            rb_parent = parent.node()

            if 'joints' in joint_config_parent:
                for key_child in joint_config_parent['joints']:
                    joint_config_child = joint_config_parent['joints'][key_child]
                    other = root.find(key_child)
                    rb_child = other.node()
                    yield (joint_config_child, rb_parent, rb_child)

    def walk_joints(self, actor, part, parents):
        parents = list(parents)

        if isinstance(part, CharacterJoint) and part.get_name() not in excluded_joints:
            node = actor.exposeJoint(None, 'modelRoot', part.get_name())

            parents_len = len(parents)
            if parents_len > 0:
                parent = parents[-1]

                mass = get_mass(parents_len, 1.0, 5.0)
                node_name = node.get_name()

                joint_config = joints_config[node_name] if node_name in joints_config else None
                joint_pos = node.get_pos(parent)
                joint_midpoint = joint_pos / 2.0
                joint_length = joint_pos.length()
                joint_width = joint_length / 2.0 if joint_length > 0 else mass

                if joint_config is not None and 'scale' in joint_config:
                    sx, sy, sz = joint_config['scale']
                    scale = Vec3(sx, sy if sy != -1 else joint_width, sz)
                else:
                    scale = Vec3(mass, joint_width, mass)

                box_scale = Vec3(1, joint_width, 1)
                box_scale = scale

                box_rb = BulletRigidBodyNode(node_name)
                box_rb.setMass(mass)
                box_rb.addShape(BulletBoxShape(box_scale))
                box_rb.setLinearDamping(0.2)
                box_rb.setAngularDamping(0.9)
                box_rb.setFriction(0.2)

                self.world.attachRigidBody(box_rb)

                # align rigidbody with relative position node
                np = parent.attachNewNode(box_rb)
                np.setPos(joint_midpoint)
                np.lookAt(node)

                # reparent to root
                box_np = self.physical_rig.attachNewNode(box_rb)
                np.removeNode() # cleanup relative position node

                # load model
                # model = self.loader.loadModel('cube.egg')
                # model.reparentTo(box_np)
                # model.flattenLight()
                # model.setScale(Vec3(scale))

            parents.append(node)

        for child in part.get_children():
            self.walk_joints(actor, child, parents)

    def babble(self, torque_min, torque_max):
        for child in self.physical_rig.getChildren():
            T_local = Vec3(0, 0, random.random() * 10000.0)
            T_world = child.getQuat(self.render).xform(T_local)
            child.node().applyTorque(T_world)

    def get_mass(self, depth, min_mass, max_mass):
        depth_multiplier = 1.0
        depth_factor = 3.0
        if depth > 0:
            return min(max_mass * (depth_factor / (depth * depth_multiplier)) + min_mass, max_mass)
        else:
            return max_mass
