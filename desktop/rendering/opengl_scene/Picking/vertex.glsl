#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 aColor;

uniform mat4 translationMatrix;
uniform mat4 aspectMatrix;
uniform mat4 worldMatrix;
uniform mat4 projMatrix;
uniform vec2 angle;

out float z;

void main()
{
    // Rotation
    mat4 rotMat = mat4(cos(angle.x),  sin(angle.y) * sin(angle.x), sin(angle.x) * cos(angle.y), 0,
                       0,             cos(angle.y),               -sin(angle.y),                0,
                       -sin(angle.x), sin(angle.y) * cos(angle.x), cos(angle.y) * cos(angle.x), 0,
                       0,             0,                           0,                           1);

    gl_Position = aspectMatrix * projMatrix * worldMatrix * rotMat * translationMatrix * vec4(position, 1.0f);
    z = translationMatrix[3][2] / 1.5;
}
