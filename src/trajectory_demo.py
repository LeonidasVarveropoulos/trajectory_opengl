import cv2
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
import time
import sys
import math

from test_trajectory import test_trajectory

#window dimensions
width = 1280
height = 720

global capture
capture = None

global start_time
start_time = time.time()

global is_draw_model
is_draw_model = True

global model_scale
model_scale = 1/6.0

# Shader for the trajectory
global TRAJ_VERTEX_SHADER
with open("traj_vert.glsl") as file:
    TRAJ_VERTEX_SHADER = file.read()

global TRAJ_FRAGMENT_SHADER
with open("traj_frag.glsl") as file:
    TRAJ_FRAGMENT_SHADER = file.read()

global TRAJ_SHADER_PROGRAM
TRAJ_SHADER_PROGRAM = None

# Shader for the orientation model
global ORI_VERTEX_SHADER
with open("ori_vert.glsl") as file:
    ORI_VERTEX_SHADER = file.read()

global ORI_FRAGMENT_SHADER
with open("ori_frag.glsl") as file:
    ORI_FRAGMENT_SHADER = file.read()

global ORI_SHADER_PROGRAM
TRAJ_SHADER_PROGRAM = None

global vertices
vertices = test_trajectory().get_vertices()

global next_vertices
next_vertices = test_trajectory().get_next_vertices()

global vertices_direction
vertices_direction = test_trajectory().get_vertices_direction()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)

    init_traj_shader()
    #init_ori_shader()
    glutDisplayFunc(display)
    glutIdleFunc(idle)  


def init_traj_shader():
    global TRAJ_SHADER_PROGRAM
    global TRAJ_VERTEX_SHADER
    global TRAJ_FRAGMENT_SHADER

    vertexshader = compileShader(TRAJ_VERTEX_SHADER, GL_VERTEX_SHADER)
    fragmentshader = compileShader(TRAJ_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)  

    TRAJ_SHADER_PROGRAM = compileProgram(vertexshader, fragmentshader)

    # Bind vertices
    position = glGetAttribLocation(TRAJ_SHADER_PROGRAM, "position")
    next_position = glGetAttribLocation(TRAJ_SHADER_PROGRAM, "nextPosition")
    direction = glGetAttribLocation(TRAJ_SHADER_PROGRAM, "direction")

    glEnableVertexAttribArray(position)
    glEnableVertexAttribArray(next_position)
    glEnableVertexAttribArray(direction)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(GL_ARRAY_BUFFER, next_vertices.nbytes, next_vertices, GL_STATIC_DRAW)
    glVertexAttribPointer(next_position, 3, GL_FLOAT, GL_FALSE, 3*4, None)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(GL_ARRAY_BUFFER, vertices_direction.nbytes, vertices_direction, GL_STATIC_DRAW)
    glVertexAttribPointer(direction, 1, GL_FLOAT, GL_FALSE, 1*4, None)


def init_ori_shader():
    global ORI_SHADER_PROGRAM
    global ORI_VERTEX_SHADER
    global ORI_FRAGMENT_SHADER

    vertexshader = compileShader(ORI_VERTEX_SHADER, GL_VERTEX_SHADER)
    fragmentshader = compileShader(ORI_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)  

    ORI_SHADER_PROGRAM = compileProgram(vertexshader, fragmentshader)

    # Bind vertices
    position = glGetAttribLocation(ORI_SHADER_PROGRAM, "position")

    glEnableVertexAttribArray(position)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    triangle_width = 0.1
    model = [0.0, 0.0, 0.0, # origin
            triangle_width, 1.0, 0.0, # y:face 1
            -triangle_width, 1.0, 0.0,
            0.0, 0.0, 0.0, # origin
            0.0, 1.0, triangle_width, # y:face 2
            0.0, 1.0, -triangle_width,
            0.0, 0.0, 0.0, # origin
            1.0, triangle_width, 0.0, # x:face 1
            1.0, -triangle_width, 0.0,
            0.0, 0.0, 0.0, # origin
            1.0, 0.0, triangle_width, # x:face 2
            1.0, 0.0, -triangle_width,
            0.0, 0.0, 0.0, # origin
            triangle_width, 0.0, 1.0, # z:face 1
            -triangle_width, 0.0, 1.0,
            0.0, 0.0, 0.0, # origin
            0.0, triangle_width, 1.0, # z:face 1
            0.0, -triangle_width, 1.0]

    model = np.array(model, dtype = np.float32)

    glBufferData(GL_ARRAY_BUFFER, model.nbytes, model, GL_STATIC_DRAW)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)


def idle():
    global capture
    _,image = capture.read()

    out_image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    # Create Texture
    glTexImage2D(GL_TEXTURE_2D, 
      0, 
      GL_RGB, 
      width, height,
      0,
      GL_RGB, 
      GL_UNSIGNED_BYTE, 
      out_image)
    
    glutPostRedisplay()


def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glEnable(GL_TEXTURE_2D)
   
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)

    # Set Projection Matrix
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluOrtho2D(0, width, 0, height)

    # Switch to Model View Matrix
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    # Draw textured Quads
    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, height)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(width, height)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(width, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, 0.0)
    glEnd()

    
    # Sets up the apha channel
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glBegin(GL_QUADS)
    glTexCoord2f(0.0, 0.0)
    glVertex2f(0.0, height)
    glTexCoord2f(1.0, 0.0)
    glVertex2f(width, height)
    glTexCoord2f(1.0, 1.0)
    glVertex2f(width, 0.0)
    glTexCoord2f(0.0, 1.0)
    glVertex2f(0.0, 0.0)
    glEnd()

    # DRAW STUFF
    draw_trajectory()

    #draw_orientations()

    if (is_draw_model):
        draw_model()

    glDisable(GL_BLEND)

    glFlush()
    glutSwapBuffers()

def draw_trajectory():
    glUseProgram(TRAJ_SHADER_PROGRAM)

    mvp = glm.mat4(1.0)
    uniform_mvp = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/3)

    # GL_TRIANGLE_STRIP GL_TRIANGLES
    glDrawArrays(GL_TRIANGLES, 0, vert_num)

    glUseProgram(0)

def draw_model():
    # Draw background
    glColor4f(0.0, 0.0, 0.0, 0.7)
    glBegin(GL_QUADS)
    glVertex2f(0, height)
    glVertex2f(0, height - height * model_scale)
    glVertex2f(width * model_scale, height - height * model_scale)
    glVertex2f(width * model_scale, height)
    glEnd()
    glColor4f(1.0, 1.0, 1.0, 1.0)

    # Draw model
    glUseProgram(TRAJ_SHADER_PROGRAM)

    # Scale and translate matrix
    mvp = glm.translate(glm.mat4(1.0), glm.vec3(-(1-model_scale), (1-model_scale), 0))

    scale = glm.vec3(model_scale)
    mvp = glm.scale(mvp, scale)

    angle = (time.time() - start_time) * 30
    mvp = glm.rotate(mvp, glm.radians(angle), glm.vec3(0,1,0))

    uniform_mvp = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/3)

    glDrawArrays(GL_TRIANGLE_STRIP, 0, vert_num)
    glUseProgram(0)

def draw_orientations():
    glUseProgram(ORI_SHADER_PROGRAM)

    mvp = glm.mat4(1.0)
    uniform_mvp = glGetUniformLocation(ORI_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/3)

    glDrawArrays(GL_TRIANGLES, 0, vert_num)

    glUseProgram(0)


def main():
    global capture
    capture = cv2.VideoCapture(0)
    capture.set(3,width)
    capture.set(4,height)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(width, height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow("OpenGL + OpenCV")

    init()
    glutMainLoop()


if __name__ == "__main__":
    main()