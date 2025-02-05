#version 330 core

in vec2 TexCoord;

out vec4 outputColor;

uniform sampler2D ourTexture;
uniform float dilutionFactor;
uniform float visibility;

void main()
{
    float size = 0.01;

    float x = TexCoord.x / size;
    float y = TexCoord.y / size;

    float sum = x + y;

    bool visible = false;
    if (int(mod(float(sum), float(3))) == 0)
        visible = true;

    vec4 texColor = texture(ourTexture, TexCoord);
    if (TexCoord.x < 0.0 || TexCoord.x > 1.0 || TexCoord.y < 0.0 || TexCoord.y > 1.0) {
        if (!visible)
            discard;
        outputColor = vec4(1.0,1.0,1.0,0.5);
    } else {
        outputColor = mix(mix(texColor, vec4(vec3(1.0), 0.0), 1.0 - visibility), vec4(vec3(1.0), 1.0), dilutionFactor);
    }
}