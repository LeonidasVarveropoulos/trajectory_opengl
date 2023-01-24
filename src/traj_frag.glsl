#version 110

varying vec4 depth;

void main() {
    float depthFactor = (depth.z * (1.0/1.5));
    gl_FragColor = vec4(0.3, 0.7 + depthFactor, 0.0, 0.7 + depthFactor);
}