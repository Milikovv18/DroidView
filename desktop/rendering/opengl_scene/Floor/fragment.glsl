#version 330 core
#extension GL_OES_standard_derivatives : enable

in vec2 coord;

out vec4 outputColor;

void main()
{
    float divisions = 15.0;
    float thickness = 0.01;

    float x = fract(coord.x * divisions);
    x = min(x, 1.0 - x);

    float xdelta = fwidth(x);
    x = smoothstep(x - xdelta, x + xdelta, thickness);

    float y = fract(coord.y * divisions);
    y = min(y, 1.0 - y);

    float ydelta = fwidth(y);
    y = smoothstep(y - ydelta, y + ydelta, thickness);

    float c = clamp(x + y, 0.0, 1.0);

    float transparency = pow(min(0.5 - abs(coord.x - 0.5), 0.5 - abs(coord.y - 0.5)), 0.8);

    outputColor = vec4(c, c, c, transparency);
}