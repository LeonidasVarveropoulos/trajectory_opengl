#version 110

varying vec3 vDepth;

void main() {

    gl_FragColor = vec4(0.7 + (vDepth.z * 2.0), 0.7 + (vDepth.z * 2.0), 0.5 + (vDepth.z * 1.0), 0.8s);
}