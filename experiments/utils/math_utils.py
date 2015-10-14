
def get_angle(angle):
    while angle > 180.0:
        angle -= 360.0
    while angle < -180.0:
        angle += 360.0
    return angle

get_angle_vec = np.vectorize(get_angle)

def get_rotation_quat(node, dh, dp, dr):
    dq = Quat()
    dq.set_hpr(Vec3(dh, dp, dr))
    return dq
