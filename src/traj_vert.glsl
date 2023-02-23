#version 330

layout(location = 0)in vec4 position;
layout(location = 1)in vec4 nextPosition;
layout(location = 2)in float direction;
layout(location = 3)in float vertCount;

out float depth;

uniform mat4 mvp;

uniform vec4 exactPos;
uniform vec4 exactNextPos;
uniform float renderCount;

void main() {
    vec4 p1 = position;
    vec4 p2 = nextPosition;
    if (vertCount >= renderCount) {
        p1 = exactPos;
        p2 = exactNextPos;
    }

    vec4 old = p1;

    p1 = mvp * p1;
    p2 = mvp * p2;

    p1/=p1.w;
    p2/=p2.w;

    depth = p1.z;

    vec2 currentScreen = p1.xy;

    vec2 nextScreen = p2.xy;

    //normal of line (B - A)
    vec2 dir = normalize(nextScreen - currentScreen);
    vec2 normal = vec2(-dir.y, dir.x);

    normal *= 0.01 * ((depth + 1.1) * 2.0);

    //offset by the direction of this point in the pair (-1 or 1)
    vec4 offset = vec4(normal * direction, 0.0, 0.0);
    
    gl_Position = p1 + offset;
}