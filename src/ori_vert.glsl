#version 330

layout(location = 0)in vec4 position;
layout(location = 1)in float color;

out vec4 axisColor;

uniform mat4 mvp;
uniform mat4 translation;
uniform float aspectRatio;

void main() {
    vec4 pos = mvp * position;
    vec4 temp = vec4(1.0);
    if (aspectRatio > 1) {
        temp = vec4(pos.x/aspectRatio, pos.y, pos.zw);
    } else {
        temp = vec4(pos.x, pos.y * aspectRatio, pos.zw);
    }
    gl_Position = translation * temp;

    float depthFactor = (pos.z * (1.0/1.5));

    if (color == -1.0)
        axisColor = vec4(1.0, 0.0, 0.0, 0.5 + depthFactor);
    else if (color == 0.0)
        axisColor = vec4(0.0, 1.0, 0.0, 0.5 + depthFactor);
    else
        axisColor = vec4(0.0, 0.0, 1.0, 0.5 + depthFactor);
}