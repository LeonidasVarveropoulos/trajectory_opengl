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

global VERTEX_SHADER
with open("vert.glsl") as file:
    VERTEX_SHADER = file.read()

global FRAGMENT_SHADER
with open("frag.glsl") as file:
    FRAGMENT_SHADER = file.read()

global shaderProgram
shaderProgram = None

global vertices
vertices = test_trajectory().get_vertices()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)

    init_shaders()
    glutDisplayFunc(display)
    glutIdleFunc(idle)  


def init_shaders():
    global shaderProgram
    global VERTEX_SHADER
    global FRAGMENT_SHADER
    global GEOMETRY_SHADER

    vertexshader = compileShader(VERTEX_SHADER, GL_VERTEX_SHADER)
    fragmentshader = compileShader(FRAGMENT_SHADER, GL_FRAGMENT_SHADER)  

    shaderProgram = compileProgram(vertexshader, fragmentshader)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    # Bind vertices
    position = glGetAttribLocation(shaderProgram, "position")
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 7*4, None)
    glEnableVertexAttribArray(position)

    # Bind next vertices
    next_position = glGetAttribLocation(shaderProgram, "nextPosition")
    glVertexAttribPointer(next_position, 3, GL_FLOAT, GL_FALSE, 7*4, 3*4)
    glEnableVertexAttribArray(next_position)

    # Bind direction
    direction = glGetAttribLocation(shaderProgram, "direction")
    glVertexAttribPointer(direction, 1, GL_FLOAT, GL_FALSE, 7*4, 6*4)
    glEnableVertexAttribArray(direction)


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

    if (is_draw_model):
        draw_model()

    glDisable(GL_BLEND)

    glFlush()
    glutSwapBuffers()

def draw_trajectory():
    glUseProgram(shaderProgram)

    mvp = glm.mat4(1.0)
    uniform_mvp = glGetUniformLocation(shaderProgram, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/7)

    glDrawArrays(GL_LINE_STRIP, 0, vert_num)

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
    glUseProgram(shaderProgram)

    # Scale and translate matrix
    mvp = glm.translate(glm.mat4(1.0), glm.vec3(-(1-model_scale), (1-model_scale), 0))

    scale = glm.vec3(model_scale)
    mvp = glm.scale(mvp, scale)

    angle = (time.time() - start_time) * 30
    mvp = glm.rotate(mvp, glm.radians(angle), glm.vec3(0,1,0))

    uniform_mvp = glGetUniformLocation(shaderProgram, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/7)

    glDrawArrays(GL_LINE_STRIP, 0, vert_num)
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