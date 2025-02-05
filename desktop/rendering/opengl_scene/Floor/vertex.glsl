#version 330 core
#define M_PI 3.1415926535897932384626433832795

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 aColor;

uniform mat4 aspectMatrix;
uniform float lowestNode;
uniform mat4 worldMatrix;
uniform mat4 projMatrix;
uniform vec2 angle;

out vec2 coord;

mat4 getRot(float x, float y, float z)
{
    return mat4(cos(y) * cos(z), sin(x) * sin(y) * cos(z) - cos(x) * sin(z), cos(x) * sin(y) * cos(z) + sin(x) * sin(z), 0.0,
                cos(y) * sin(z), sin(x) * sin(y) * sin(z) + cos(x) * cos(z), cos(x) * sin(y) * sin(z) - sin(x) * cos(z), 0.0,
                -sin(y),         sin(x) * cos(y),                            cos(x) * cos(y),                            0.0,
                0.0,             0.0,                                        0.0,                                        1.0);
}

void main()
{
    // Rotation
    float angle_y = angle.y + 0.5 * M_PI;
    mat4 rotMat = getRot(angle.y + 0.5 * M_PI, 0, angle.x);

    mat4 shiftedWorld = mat4(1.0);
    shiftedWorld[3][2] += lowestNode - 0.5; // Altitude is represented with Z value due to rotation
    gl_Position = aspectMatrix * projMatrix * worldMatrix * rotMat * shiftedWorld * vec4(10 * position, 1.0f);
    coord = (vec2(position.x, position.y) + vec2(1.0)) / vec2(2.0);
}