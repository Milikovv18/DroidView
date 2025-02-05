#version 330 core

out vec4 outputColor;

uniform vec3 color;
uniform float saturation;

void main()
{
    outputColor = vec4(color, saturation);
}