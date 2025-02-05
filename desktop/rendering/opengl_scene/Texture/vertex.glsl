#version 330 core

layout (location = 0) in vec3 position;
layout (location = 1) in vec2 aTexCoord;

out vec2 TexCoord;

uniform mat4 translationMatrix;
uniform mat4 aspectMatrix;
uniform mat4 worldMatrix;
uniform mat4 projMatrix;
uniform vec2 angle;
uniform float textureAmend; // X texture coordinate compensation after applying phone screen aspect

void main()
{
    // Rotation
    mat4 rotMat = mat4(cos(angle.x),  sin(angle.y) * sin(angle.x), sin(angle.x) * cos(angle.y), 0,
                       0,             cos(angle.y),               -sin(angle.y),                0,
                       -sin(angle.x), sin(angle.y) * cos(angle.x), cos(angle.y) * cos(angle.x), 0,
                       0,             0,                           0,                           1);

    // Vertex position
    gl_Position = aspectMatrix * projMatrix * worldMatrix * rotMat * translationMatrix * vec4(position, 1.0f);

    // Texture
    vec2 transDiag = vec2(textureAmend * translationMatrix[0][0], translationMatrix[1][1]);
    vec2 transBtmRow = vec2(textureAmend * translationMatrix[3][0], translationMatrix[3][1]);
    vec2 scale_shift = -0.5 * transDiag + 0.5;
    TexCoord = transDiag * aTexCoord + scale_shift + 0.5 * transBtmRow;
}
