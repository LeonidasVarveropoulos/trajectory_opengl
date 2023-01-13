#version 110

attribute vec4 position;
uniform mat4 mvp;

varying vec3 vDepth;

void main() {

gl_Position = mvp * position;

vDepth = position.xyz;


}