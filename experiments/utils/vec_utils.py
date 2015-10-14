def flatten_vectors(arr):
    return np.array([[v.get_x(), v.get_y(), v.get_z()] for v in arr]).flatten()
