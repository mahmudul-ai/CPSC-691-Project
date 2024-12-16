import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
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

# Render the loaded object using VBOs
def render_obj(vertices, faces, normals):
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

# Initialize Pygame and OpenGL
pygame.init()
display = (600, 600)
pygame.display.set_mode(display, DOUBLEBUF | OPENGL)

# Adjust perspective and camera
gluPerspective(45, (display[0] / display[1]), 0.1, 500.0)
glTranslatef(-30.0, -20.0, -100.0)

# Set up OpenGL settings
glClearColor(0.0, 0.0, 0.0, 1.0)
glEnable(GL_DEPTH_TEST)

# Set up lighting (Ambient, Diffuse, Specular)
glEnable(GL_LIGHTING)
glEnable(GL_LIGHT0)
glLightfv(GL_LIGHT0, GL_POSITION, [0.0, -20.0, -100.0, 1.0])
glLightfv(GL_LIGHT0, GL_DIFFUSE, [1.0, 1.0, 1.0, 1.0])
glLightfv(GL_LIGHT0, GL_AMBIENT, [0.5, 0.5, 0.5, 1.0])
glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])

# Material properties
glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
glMaterialfv(GL_FRONT, GL_SHININESS, [50.0])

# Load the brain and segmented tumor objects
brain_filename = "output-t2w.obj"  # Replace with the actual path to your brain .obj file
tumor_filename = "output-seg.obj"  # Replace with the actual path to your tumor .obj file

try:
    # Load and prepare the brain object
    brain_vertices, brain_faces = load_obj(brain_filename)
    brain_normals = calculate_normals(brain_vertices, brain_faces)
    brain_vertices *= 0.25
    brain_center = np.mean(brain_vertices, axis=0)

    # Load and prepare the tumor object
    tumor_vertices, tumor_faces = load_obj(tumor_filename)
    tumor_normals = calculate_normals(tumor_vertices, tumor_faces)
    tumor_vertices *= 0.25
    tumor_center = np.mean(tumor_vertices, axis=0)

    # Mouse rotation variables
    rotation_x, rotation_y = 0, 0
    mouse_down = False
    last_mouse_x, last_mouse_y = 0, 0

    # Interactive slicing variables
    slice_position = 0.0

    # Main rendering loop
    clock = pygame.time.Clock()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_down = True
                    last_mouse_x, last_mouse_y = event.pos
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_down = False
            elif event.type == pygame.MOUSEMOTION:
                if mouse_down:
                    mouse_x, mouse_y = event.pos
                    dx = mouse_x - last_mouse_x
                    dy = mouse_y - last_mouse_y
                    rotation_x += dy * 0.5
                    rotation_y += dx * 0.5
                    last_mouse_x, last_mouse_y = mouse_x, mouse_y
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    slice_position += 0.1
                elif event.key == pygame.K_DOWN:
                    slice_position -= 0.1

        # # Clear the screen and depth buffer
        # glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # # Enable blending for transparency
        # glEnable(GL_BLEND)
        # glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # # Apply rotations
        # glPushMatrix()
        # glTranslatef(brain_center[0], brain_center[1], brain_center[2])
        # glRotatef(rotation_x, 1, 0, 0)
        # glRotatef(rotation_y, 0, 1, 0)
        # glTranslatef(-brain_center[0], -brain_center[1], -brain_center[2])

        # # Apply slicing plane
        # glEnable(GL_CLIP_PLANE0)
        # slice_eqn = [1.0, 0.0, 0.0, -slice_position]  # Adjust slicing plane equation as needed
        # glClipPlane(GL_CLIP_PLANE0, slice_eqn)

        # # Render the brain object with transparency
        # glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.0, 1.0, 0.0, 0.2])  # Green with 50% transparency
        # render_obj(brain_vertices, brain_faces, brain_normals)

        # # Render the tumor object
        # glMaterialfv(GL_FRONT, GL_DIFFUSE, [1.0, 0.0, 0.0, 1.0])  # Red
        # render_obj(tumor_vertices, tumor_faces, tumor_normals)

        # # Disable slicing plane
        # glDisable(GL_CLIP_PLANE0)

        # # Restore the original matrix
        # glPopMatrix()

        # # Update the display
        # pygame.display.flip()
        # Clear the screen and depth buffer
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Enable blending for transparency
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

        # Disable depth writing (not depth testing)
        glDepthMask(GL_FALSE)

        # Apply rotations
        glPushMatrix()
        glTranslatef(brain_center[0], brain_center[1], brain_center[2])
        glRotatef(rotation_x, 1, 0, 0)
        glRotatef(rotation_y, 0, 1, 0)
        glTranslatef(-brain_center[0], -brain_center[1], -brain_center[2])

        # Apply slicing plane
        glEnable(GL_CLIP_PLANE0)
        slice_eqn = [1.0, 0.0, 0.0, -slice_position]  # Adjust slicing plane equation as needed
        glClipPlane(GL_CLIP_PLANE0, slice_eqn)

        # Render the brain object with transparency
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.98, 0.95])  # Green with 50% transparency
        render_obj(brain_vertices, brain_faces, brain_normals)

        # Enable depth writing again before rendering the tumor
        glDepthMask(GL_TRUE)

        # Render the tumor object (it will now be drawn on top of the brain)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.84, 0.1, 0.11, 1.0])  # Red
        render_obj(tumor_vertices, tumor_faces, tumor_normals)

        # Disable slicing plane
        glDisable(GL_CLIP_PLANE0)

        # Restore the original matrix
        glPopMatrix()

        # Update the display
        pygame.display.flip()

        # # Limit the frame rate to 30 FPS
        # clock.tick(30)


        # Limit the frame rate to 30 FPS
        clock.tick(30)
    pygame.quit()
except FileNotFoundError as fnf_error:
    print(fnf_error)
except Exception as e:
    print(e)
