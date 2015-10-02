from __future__ import division

import cPickle as pickle
import random
import sys

from direct.showbase.ShowBase import ShowBase
from direct.task import Task

from panda3d import bullet
from panda3d.core import Vec3, PerspectiveLens, ClockObject, DirectionalLight

from arm import Arm

def create_lens(aspect_ratio):
    lens = PerspectiveLens()
    lens.setFov(60)
    lens.setAspectRatio(aspect_ratio)
    return lens

class App(ShowBase):

    def __init__(self, args):
        ShowBase.__init__(self)

        headless = args['--headless']
        width = args['--width']
        height = args['--height']

        self.save_path = args['<save_path>']
        self.train_count = 60000
        self.test_count = 10000
        self.home_position = [-135, -90, -45, 0, 45, 90, 135, 180]
        self.iteration_count = 0
        self.home_count = 0

        globalClock.set_mode(ClockObject.MNonRealTime)
        globalClock.set_dt(0.02) # 20ms per frame

        # self.toggleWireframe()
        self.disableMouse() # just disables camera movement with mouse

        light = DirectionalLight('light')
        light_np = self.render.attach_new_node(light)
        self.render.set_light(light_np)

        if not headless:
            self.cam.set_pos(0, -20, 0)
            self.cam.look_at(0, 0, 0)
            self.cam.node().set_lens(create_lens(width / height))

        self.arm = Arm(self.render)

        self.X_train = []
        self.Y_train = []

        self.X_test = []
        self.Y_test = []

        self.accept('escape', sys.exit)
        self.taskMgr.add(self.update, 'update')

    def save(self):
        print 'saving...', self.save_path
        data = ((self.X_train, self.Y_train), (self.X_test, self.Y_test))

        f = open(self.save_path, 'wb')
        pickle.dump(data, f)
        f.close()

    def generate(self):
        if self.iteration_count % 10 == 0:
            # move to a random home position
            h = random.choice(self.home_position)
            p = random.choice(self.home_position)
            r = random.choice(self.home_position)
            self.arm.shoulder_pivot.set_hpr(h, p, r)

            h = random.choice(self.home_position)
            p = random.choice(self.home_position)
            r = random.choice(self.home_position)
            self.arm.elbow_pivot.set_hpr(h, p, r)

            self.shoulder_vel = Vec3()
            self.elbow_vel = Vec3()
            self.end_vel = Vec3()

            self.home_count += 1

        # save current position as previous
        shoulder_pos = self.arm.shoulder_pivot.get_pos(self.arm.arm_pivot)
        elbow_pos = self.arm.elbow_pivot.get_pos(self.arm.arm_pivot)
        end_pos = self.arm.end_effector.get_pos(self.arm.arm_pivot)

        # rotate to a position random +/- 5 degrees
        shoulder_dh = random.uniform(-5.0, 5.0)
        shoulder_dp = random.uniform(-5.0, 5.0)
        shoulder_dr = random.uniform(-5.0, 5.0)
        self.arm.rotate_shoulder(shoulder_dh, shoulder_dp, shoulder_dr)

        elbow_dh = random.uniform(-5.0, 5.0)
        elbow_dp = random.uniform(-5.0, 5.0)
        elbow_dr = random.uniform(-5.0, 5.0)
        self.arm.rotate_elbow(elbow_dh, elbow_dp, elbow_dr)

        # save current position as target
        next_shoulder_pos = self.arm.shoulder_pivot.get_pos(self.arm.arm_pivot)
        next_elbow_pos = self.arm.elbow_pivot.get_pos(self.arm.arm_pivot)
        next_end_pos = self.arm.end_effector.get_pos(self.arm.arm_pivot)

        # calculate target direction from new position
        shoulder_target = next_shoulder_pos - shoulder_pos
        elbow_target = next_elbow_pos - elbow_pos
        end_target = next_end_pos - end_pos

        # current
        position = [
            elbow_pos.get_x() / 10.0,
            elbow_pos.get_y() / 10.0,
            elbow_pos.get_z() / 10.0,
            end_pos.get_x() / 10.0,
            end_pos.get_y() / 10.0,
            end_pos.get_z() / 10.0]

        # past
        velocity = [
            self.elbow_vel.get_x() / 5.0,
            self.elbow_vel.get_y() / 5.0,
            self.elbow_vel.get_z() / 5.0,
            self.end_vel.get_x() / 5.0,
            self.end_vel.get_y() / 5.0,
            self.end_vel.get_z() / 5.0]

        # future
        target = [
            elbow_target.get_x() / 5.0,
            elbow_target.get_y() / 5.0,
            elbow_target.get_z() / 5.0,
            end_target.get_x() / 5.0,
            end_target.get_y() / 5.0,
            end_target.get_z() / 5.0]

        X = position + target

        # output (delta euler rotation)
        Y = [
            shoulder_dh / 5.0,
            shoulder_dp / 5.0,
            shoulder_dr / 5.0,
            elbow_dh / 5.0,
            elbow_dp / 5.0,
            elbow_dr / 5.0]

        self.shoulder_vel = shoulder_target
        self.elbow_vel = elbow_target
        self.end_vel = end_target

        self.iteration_count += 1

        return X, Y

    def update(self, task):
        train_complete = len(self.X_train) == self.train_count
        test_complete = len(self.X_test) == self.test_count

        if not train_complete: # motor babbling
            X, Y = self.generate()
            self.X_train.append(X)
            self.Y_train.append(Y)
        elif not test_complete: # move positions
            X, Y = self.generate()
            self.X_test.append(X)
            self.Y_test.append(Y)

        if train_complete and test_complete:
            self.save()
            sys.exit()
            return task.done

        total_completed = len(self.X_train) + len(self.X_test)
        total_count = self.train_count + self.test_count

        print 'progress: %f%%, homes: %d' % ((total_completed / total_count) * 100.0, self.home_count)

        return task.cont
