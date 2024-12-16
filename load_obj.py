import numpy as np

# Load the .obj file (vertices and faces)
def load_obj(filename):
    vertices = []
    faces = []
    with open(filename, 'r') as file:
        for line in file:
            parts = line.split()
            if len(parts) == 0:
                continue
            if parts[0] == 'v':  # vertex
                vertices.append([float(x) for x in parts[1:4]])
            elif parts[0] == 'f':  # face
                # face indices are 1-based, subtract 1 to make them 0-based
                face = [int(x.split('/')[0]) - 1 for x in parts[1:4]]
                faces.append(face)
    return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.uint32)
