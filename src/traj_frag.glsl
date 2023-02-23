#version 330

in float depth;

out vec4 fragColor;

void main() {
    float depthFactor = (-depth*3.0 + 2.0) * 0.2;
    fragColor = vec4(0.7 + depthFactor, 0.5 + depthFactor, 0.0, 0.7 + depthFactor);
}