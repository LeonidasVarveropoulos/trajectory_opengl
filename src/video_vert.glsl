#version 330 core

layout (location = 0) in vec3 position;

out vec2 TexCoord;

uniform mat4 mvp;

void main()
{
    gl_Position = mvp * vec4(position, 1.0);
    TexCoord = position.xy;
}