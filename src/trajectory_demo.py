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
import glfw

from test_trajectory import test_trajectory

global trajectory
trajectory = test_trajectory()

#window dimensions
width = 1280
height = 720

global capture
capture = None

global start_time
start_time = time.time()

global time_scale
time_scale = 1

global model_scale
model_scale = 1/6.0

# Configuration variables that should be defined in the ros yaml file
global config_draw_model
config_draw_model = True

global config_animate_trajectory
config_animate_trajectory = True

global config_animation_speed
config_animation_speed = 1.0

global config_draw_orientations
config_draw_orientations = True

# Shader for the videp
global VIDEO_VERTEX_SHADER
with open("video_vert.glsl") as file:
    VIDEO_VERTEX_SHADER = file.read()

global VIDEO_FRAGMENT_SHADER
with open("video_frag.glsl") as file:
    VIDEO_FRAGMENT_SHADER = file.read()

global VIDEO_SHADER_PROGRAM
VIDEO_SHADER_PROGRAM = None

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

global video_attribs
video_attribs = []

global traj_attribs
traj_attribs = []

global ori_attribs
ori_attribs = []

global video_texture

# Vertex array objects
global video_vao
global traj_vao
global ori_vao

global vertices
vertices = trajectory.get_vertices()

global next_vertices
next_vertices = trajectory.get_next_vertices()

global vertices_direction
vertices_direction = trajectory.get_vertices_direction()

global vertices_count
vertices_count = trajectory.get_vert_count()

ori_count = 15
global ori_poses
ori_poses = trajectory.get_orientation_poses(ori_count)

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)

    init_video_shader()
    init_traj_shader()
    init_ori_shader()

def init_video_shader():
    global VIDEO_SHADER_PROGRAM
    global VIDEO_VERTEX_SHADER
    global VIDEO_FRAGMENT_SHADER
    global video_vao
    global video_texture

    video_texture = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, video_texture)

    video_vao = glGenVertexArrays(1)
    glBindVertexArray(video_vao)

    vertexshader = compileShader(VIDEO_VERTEX_SHADER, GL_VERTEX_SHADER)
    fragmentshader = compileShader(VIDEO_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)  

    VIDEO_SHADER_PROGRAM = compileProgram(vertexshader, fragmentshader)

    # Bind vertices
    position = glGetAttribLocation(VIDEO_SHADER_PROGRAM, "position")

    video_attribs.append(position)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    vert = [-1.0, 1.0, 0.0,
            1.0, 1.0, 0.0,
            1.0, -1.0, 0.0,
            -1.0, 1.0, 0.0,
            1.0, -1.0, 0.0,
            -1.0, -1.0, 0.0]

    vert = np.array(vert, dtype = np.float32)

    glBufferData(GL_ARRAY_BUFFER, vert.nbytes, vert, GL_STATIC_DRAW)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)

    # Unbind
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)
    glBindTexture(GL_TEXTURE_2D, 0)

def init_traj_shader():
    global TRAJ_SHADER_PROGRAM
    global TRAJ_VERTEX_SHADER
    global TRAJ_FRAGMENT_SHADER
    global traj_vao

    traj_vao = glGenVertexArrays(1)
    glBindVertexArray(traj_vao)

    vertexshader = compileShader(TRAJ_VERTEX_SHADER, GL_VERTEX_SHADER)
    fragmentshader = compileShader(TRAJ_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)  

    TRAJ_SHADER_PROGRAM = compileProgram(vertexshader, fragmentshader)

    # Bind vertices
    position = glGetAttribLocation(TRAJ_SHADER_PROGRAM, "position")
    next_position = glGetAttribLocation(TRAJ_SHADER_PROGRAM, "nextPosition")
    direction = glGetAttribLocation(TRAJ_SHADER_PROGRAM, "direction")
    count = glGetAttribLocation(TRAJ_SHADER_PROGRAM, "vertCount")

    traj_attribs.append(position)
    traj_attribs.append(next_position)
    traj_attribs.append(direction)
    traj_attribs.append(count)

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

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    glBufferData(GL_ARRAY_BUFFER, vertices_count.nbytes, vertices_count, GL_STATIC_DRAW)
    glVertexAttribPointer(count, 1, GL_FLOAT, GL_FALSE, 1*4, None)

    # Unbind
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

def init_ori_shader():
    global ORI_SHADER_PROGRAM
    global ORI_VERTEX_SHADER
    global ORI_FRAGMENT_SHADER
    global ori_vao

    ori_vao = glGenVertexArrays(1)
    glBindVertexArray(ori_vao)
    
    vertexshader = compileShader(ORI_VERTEX_SHADER, GL_VERTEX_SHADER)
    fragmentshader = compileShader(ORI_FRAGMENT_SHADER, GL_FRAGMENT_SHADER)  

    ORI_SHADER_PROGRAM = compileProgram(vertexshader, fragmentshader)

    # Bind vertices
    position = glGetAttribLocation(ORI_SHADER_PROGRAM, "position")
    color = glGetAttribLocation(ORI_SHADER_PROGRAM, "color")

    ori_attribs.append(position)
    ori_attribs.append(color)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    triangle_width = 0.1
    model = [0.0, 0.0, 0.0, # origin
            triangle_width, 1.0, 0.0, # y:face 1
            -triangle_width, 1.0, 0.0,
            0.0, 0.0, 0.0, # origin
            0.0, 1.0, triangle_width, # y:face 2
            0.0, 1.0, -triangle_width,
            0.0, 1.0, triangle_width, # y:cap 1
            triangle_width, 1.0, 0.0,
            0.0, 1.0, -triangle_width,
            0.0, 1.0, triangle_width, # y:cap 2
            -triangle_width, 1.0, 0.0,
            0.0, 1.0, -triangle_width,
            0.0, 0.0, 0.0, # origin
            1.0, triangle_width, 0.0, # x:face 1
            1.0, -triangle_width, 0.0,
            0.0, 0.0, 0.0, # origin
            1.0, 0.0, triangle_width, # x:face 2
            1.0, 0.0, -triangle_width,
            1.0, 0.0, triangle_width, # x:cap 1
            1.0, triangle_width, 0.0,
            1.0, 0.0, -triangle_width,
            1.0, 0.0, triangle_width, # x:cap 2
            1.0, -triangle_width, 0.0,
            1.0, 0.0, -triangle_width,
            0.0, 0.0, 0.0, # origin
            triangle_width, 0.0, -1.0, # z:face 1
            -triangle_width, 0.0, -1.0,
            0.0, 0.0, 0.0, # origin
            0.0, triangle_width, -1.0, # z:face 1
            0.0, -triangle_width, -1.0,

            0.0, triangle_width, -1.0, # z:cap 1
            triangle_width, 0.0, -1.0,
            0.0, -triangle_width, -1.0,
            0.0, triangle_width, -1.0, # z:cap 2
            -triangle_width, 0.0, -1.0,
            0.0, -triangle_width, -1.0]

    model = np.array(model, dtype = np.float32)

    glBufferData(GL_ARRAY_BUFFER, model.nbytes, model, GL_STATIC_DRAW)
    glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 0, None)

    VBO = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, VBO)

    col = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,
        -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0,
        1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0]

    col = np.array(col, dtype = np.float32)

    glBufferData(GL_ARRAY_BUFFER, col.nbytes, col, GL_STATIC_DRAW)
    glVertexAttribPointer(color, 1, GL_FLOAT, GL_FALSE, 0, None)

    # Unbind
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

def draw_video():
    glUseProgram(VIDEO_SHADER_PROGRAM)
    glBindTexture(GL_TEXTURE_2D, video_texture);
    glBindVertexArray(video_vao)

    for attrib in video_attribs:
        glEnableVertexAttribArray(attrib)

    mvp = glm.mat4(1.0)
    uniform_mvp = glGetUniformLocation(VIDEO_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glDrawArrays(GL_TRIANGLES, 0, 6)

    for attrib in video_attribs:
        glDisableVertexAttribArray(attrib)

    glBindVertexArray(0)
    glBindTexture(GL_TEXTURE_2D, 0);
    glUseProgram(0)

def draw_trajectory():
    glUseProgram(TRAJ_SHADER_PROGRAM)

    glBindVertexArray(traj_vao)

    for attrib in traj_attribs:
        glEnableVertexAttribArray(attrib)

    # MVP matrix
    mvp = glm.mat4(1.0)
    uniform_mvp = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    # Exact position
    pose = trajectory.interpolate_single_pose(time_scale)
    uniform_exact = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "exactPos")
    glUniform4f(uniform_exact, pose[0], pose[1], pose[2], 1.0)

    # Exact Next position
    time_next = time_scale + 0.1
    if (time_next > 1):
        time_next = 1
    pose = trajectory.interpolate_single_pose(time_next)
    uniform_next_exact = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "exactNextPos")
    glUniform4f(uniform_next_exact, pose[0], pose[1], pose[2], 1.0)

    # Render count for animation
    render_count = math.floor((vertices.size/6) * time_scale)
    uniform_render = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "renderCount")
    glUniform1f(uniform_render, render_count)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/3)

    # GL_TRIANGLE_STRIP GL_TRIANGLES
    glDrawArrays(GL_TRIANGLE_STRIP, 0, vert_num)

    for attrib in traj_attribs:
        glDisableVertexAttribArray(attrib)

    glBindVertexArray(0)
    glUseProgram(0)

def draw_model():
    # Scale and translate matrix
    mvp = glm.translate(glm.mat4(1.0), glm.vec3(-(1-model_scale), (1-model_scale), 0))

    scale = glm.vec3(model_scale)
    mvp = glm.scale(mvp, scale)

    angle = (time.time() - start_time) * 30
    rotating_mvp = glm.rotate(mvp, glm.radians(angle), glm.vec3(0,1,0))

    # Draw background (with no texture so black)
    glUseProgram(VIDEO_SHADER_PROGRAM)
    glBindVertexArray(video_vao)

    for attrib in video_attribs:
        glEnableVertexAttribArray(attrib)

    uniform_mvp = glGetUniformLocation(VIDEO_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    glDrawArrays(GL_TRIANGLES, 0, 6)

    for attrib in video_attribs:
        glDisableVertexAttribArray(attrib)

    glBindVertexArray(0)
    glBindTexture(GL_TEXTURE_2D, 0);

    # Draw model
    glUseProgram(TRAJ_SHADER_PROGRAM)

    glBindVertexArray(traj_vao)

    for attrib in traj_attribs:
        glEnableVertexAttribArray(attrib)

    uniform_mvp = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(rotating_mvp))

    # Render count for animation
    render_count = int(vertices.size/6)
    uniform_render = glGetUniformLocation(TRAJ_SHADER_PROGRAM, "renderCount")
    glUniform1f(uniform_render, render_count)

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/3)

    glDrawArrays(GL_TRIANGLE_STRIP, 0, vert_num)

    for attrib in traj_attribs:
        glDisableVertexAttribArray(attrib)

    glBindVertexArray(0)
    glUseProgram(0)

def draw_orientation_path(poses):
    # Static drawing of poses
    for pose in poses:
        draw_orientation(pose)

def draw_orientation(pose):
    glUseProgram(ORI_SHADER_PROGRAM)
    glBindVertexArray(ori_vao)

    for attrib in ori_attribs:
        glEnableVertexAttribArray(attrib)

    point_scale = 0.1 * (1 + (1.5 * pose[2]))

    mvp = glm.mat4(1.0)

    scale = glm.vec3(point_scale)
    mvp = glm.scale(mvp, scale)

    mvp = glm.rotate(mvp, glm.radians(pose[3]), glm.vec3(1,0,0))
    mvp = glm.rotate(mvp, glm.radians(pose[4]), glm.vec3(0,1,0))
    mvp = glm.rotate(mvp, glm.radians(pose[5]), glm.vec3(0,0,1))


    uniform_mvp = glGetUniformLocation(ORI_SHADER_PROGRAM, "mvp")
    glUniformMatrix4fv(uniform_mvp, 1, GL_FALSE, glm.value_ptr(mvp))

    translation = glm.mat4(1.0)
    translation = glm.translate(translation, glm.vec3(pose[0], pose[1], 0.0))

    uniform_trans = glGetUniformLocation(ORI_SHADER_PROGRAM, "translation")
    glUniformMatrix4fv(uniform_trans, 1, GL_FALSE, glm.value_ptr(translation))

    ratio_location = glGetUniformLocation(ORI_SHADER_PROGRAM, "aspectRatio")
    glUniform1f(ratio_location, width/float(height))

    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    vert_num = int(vertices.size/3)

    glDrawArrays(GL_TRIANGLES, 0, vert_num)

    for attrib in ori_attribs:
        glDisableVertexAttribArray(attrib)

    glBindVertexArray(0)
    glUseProgram(0)

def idle():
    global capture
    _,image = capture.read()

    out_image = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)

    glBindTexture(GL_TEXTURE_2D, video_texture);

    # Create Texture
    glTexImage2D(GL_TEXTURE_2D, 
      0, 
      GL_RGB, 
      out_image.shape[1], out_image.shape[0],
      0,
      GL_RGB, 
      GL_UNSIGNED_BYTE, 
      out_image)
    
    glGenerateMipmap(GL_TEXTURE_2D)

    glBindTexture(GL_TEXTURE_2D, 0);

def display():
    global time_scale
    time_start, time_end = trajectory.get_path_timing()
    time_diff = (time_end - time_start) * config_animation_speed
    time_scale = (time.time() % time_diff)/time_diff;

    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
   
    # Sets up the apha channel
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

    # DRAW VIDEO
    draw_video()

    # DRAW STUFF
    draw_trajectory()

    if (config_draw_orientations):
        if (config_animate_trajectory):
            draw_orientation(trajectory.interpolate_single_pose(time_scale))
        else:
            draw_orientation_path(ori_poses)

    if (config_draw_model):
        draw_model()

    glDisable(GL_BLEND)

    glFlush()
    glutSwapBuffers()

def on_key(window, key, scancode, action, mods):
    if key == glfw.GLFW_KEY_ESCAPE and action == glfw.GLFW_PRESS:
        glfw.set_window_should_close(window,1)

def main():
    global width
    global height

    global capture
    capture = cv2.VideoCapture(0)
    capture.set(3,width)
    capture.set(4,height)

    if not glfw.init():
        return

    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 1)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, GL_TRUE)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(width, height, "Opengl GLFW Window", None, None)
    if not window:
        glfw.terminate()
        sys.exit()

    # Make the window's context current
    glfw.make_context_current(window)

    # Install a key handler
    glfw.set_key_callback(window, on_key)

    # Set stuff up
    init()

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        width, height = glfw.get_window_size(window)

        # Update opengl
        idle()
        display()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()

    init()

if __name__ == "__main__":
    main()