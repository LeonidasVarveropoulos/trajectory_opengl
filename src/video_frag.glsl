#version 330 core

out vec4 FragColor;
in vec2 TexCoord;

uniform sampler2D ourTexture;

void main()
{
    vec2 newCoord = vec2((TexCoord.x + 1.0) * 0.5, (-TexCoord.y + 1.0) * 0.5);
    FragColor = texture(ourTexture, newCoord);
}