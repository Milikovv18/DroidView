#version 330 core

in float z;

out vec4 outputColor;

void main()
{
    outputColor = vec4(z, 0.0, 0.0, 1.0);
}