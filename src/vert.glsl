#version 110

attribute vec4 position;
attribute vec4 nextPosition;
attribute float direction;

uniform mat4 mvp;

void main() {

    vec2 currentScreen = position.xy/position.w;

    vec2 nextScreen = nextPosition.xy/nextPosition.w;

    //normal of line (B - A)
    vec2 dir = normalize(nextScreen - currentScreen);
    vec2 normal = vec2(-dir.y, dir.x);

    vec4 depth = mvp * position;

    normal *= ((0.01) * (1.0 + (depth.z * 0.8) + 0.3));

    //offset by the direction of this point in the pair (-1 or 1)
    vec4 offset = vec4(normal * direction, 0.0, 0.0);
    
    gl_Position = mvp * (position + offset);
}