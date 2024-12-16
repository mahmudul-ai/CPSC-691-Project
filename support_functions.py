import numpy as np
# Calculate normals for the mesh
def calculate_normals(vertices, faces):
    normals = np.zeros(vertices.shape, dtype=vertices.dtype)
    for face in faces:
        v0, v1, v2 = vertices[face]
        edge1 = v1 - v0
        edge2 = v2 - v0
        normal = np.cross(edge1, edge2)
        normal /= np.linalg.norm(normal)
        normals[face] += normal
    normals /= np.linalg.norm(normals, axis=1).reshape(-1, 1)
    return normals