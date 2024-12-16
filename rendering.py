import pygame
import numpy as np
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
from load_obj import load_obj
from render_obj import render_obj
from support_functions import calculate_normals

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
brain_filename = "output\\output-t2w.obj"  # Replace with the actual path to your brain .obj file
tumor_filename = "output\\output-seg.obj"  # Replace with the actual path to your tumor .obj file

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
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.8, 0.8, 0.98, 0.95])  # Color 1 with 95% transparency
        render_obj(brain_vertices, brain_faces, brain_normals)

        # Enable depth writing again before rendering the tumor
        glDepthMask(GL_TRUE)

        # Render the tumor object (it will now be drawn on top of the brain)
        glMaterialfv(GL_FRONT, GL_DIFFUSE, [0.84, 0.1, 0.11, 1.0])  # Color 2 with no transparency
        render_obj(tumor_vertices, tumor_faces, tumor_normals, draw_edges=True)

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
