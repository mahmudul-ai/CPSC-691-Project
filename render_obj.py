from OpenGL.GL import *
from OpenGL.GLU import *

# Render the loaded object using VBOs
def render_obj(vertices, faces, normals, draw_edges=False):
    # Create Vertex Buffer Object (VBO) for vertices, normals, and indices
    vertex_data = vertices.flatten()
    normal_data = normals.flatten()
    index_data = faces.flatten()

    # Create VBOs and bind them
    vertex_buffer = glGenBuffers(1)
    normal_buffer = glGenBuffers(1)
    index_buffer = glGenBuffers(1)

    # Bind vertex buffer
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glBufferData(GL_ARRAY_BUFFER, vertex_data.nbytes, vertex_data, GL_STATIC_DRAW)

    # Bind normal buffer
    glBindBuffer(GL_ARRAY_BUFFER, normal_buffer)
    glBufferData(GL_ARRAY_BUFFER, normal_data.nbytes, normal_data, GL_STATIC_DRAW)

    # Bind index buffer
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

    # Enable vertex and normal arrays
    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glBindBuffer(GL_ARRAY_BUFFER, vertex_buffer)
    glVertexPointer(3, GL_FLOAT, 0, None)
    glBindBuffer(GL_ARRAY_BUFFER, normal_buffer)
    glNormalPointer(GL_FLOAT, 0, None)

    # Draw the object
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, index_buffer)
    glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)

    if draw_edges:
        glDisable(GL_LIGHTING)
        glColor3f(0.0, 0.0, 0.0)
        glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        glDrawElements(GL_TRIANGLES, len(index_data), GL_UNSIGNED_INT, None)
        glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        glEnable(GL_LIGHTING)

    # Disable vertex and normal arrays
    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)

    # Unbind buffers
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    # Delete buffers to free up memory
    glDeleteBuffers(1, [vertex_buffer])
    glDeleteBuffers(1, [normal_buffer])
    glDeleteBuffers(1, [index_buffer])