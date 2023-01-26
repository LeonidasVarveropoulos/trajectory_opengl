#version 330

layout(location = 0)in vec4 position;
layout(location = 1)in float color;

out vec4 axisColor;

uniform mat4 mvp;
uniform float aspectRatio;

void main() {
    vec4 pos = mvp * position;
    vec4 temp = vec4(1.0);
    if (aspectRatio > 1) {
        temp = vec4(pos.x/aspectRatio, pos.y, pos.zw);
    } else {
        temp = vec4(pos.x, pos.y * aspectRatio, pos.zw);
    }
    gl_Position = temp;

    if (color == -1.0)
        axisColor = vec4(1.0, 0.0, 0.0, 1.0);
    else if (color == 0.0)
        axisColor = vec4(0.0, 1.0, 0.0, 1.0);
    else
        axisColor = vec4(0.0, 0.0, 1.0, 1.0);
}