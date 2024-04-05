#version 330 core

#define M_PI 3.1415926535897932384626433832795

uniform sampler2D tex;
uniform float time;
uniform bool toggle;

in vec2 uvs;
out vec4 fragColor;

const uint k = 1103515245U;

vec3 hash( uvec3 x ) // https://www.shadertoy.com/view/XlXcW4
{
    x = ((x>>8U)^x.yzx)*k;
    x = ((x>>8U)^x.yzx)*k;
    x = ((x>>8U)^x.yzx)*k;
    
    return vec3(x)*(1.0/float(0xffffffffU));
}

vec2 bulge(vec2 texSize, vec2 coord, float factor) {
    vec2 multiplier = vec2(length(coord) * length(coord) * factor);
    multiplier.y *= texSize.x / texSize.y;
    coord *= 1 + multiplier;
    coord += 0.5;
    return coord;
}

vec4 texture_blurred(vec2 coord, vec2 texSize) { // https://www.shadertoy.com/view/Xltfzj
    float Pi = 6.28318530718;
    
    float Directions = 16.0;
    float Quality = 3.0;
    float Size = 1.1;
   
    vec2 Radius = Size/texSize;

    vec2 uv = coord;

    vec4 Color = texture(tex, uv);

    for( float d=0.0; d<Pi; d+=Pi/Directions)
    {
		for(float i=1.0/Quality; i<=1.0; i+=1.0/Quality)
        {
			Color += texture( tex, uv+vec2(cos(d),sin(d))*Radius*i);		
        }
    }

    Color /= Quality * Directions - 15.0;
    return Color;
}

void main() {
    if (!toggle) {
        fragColor = texture(tex, uvs);
        return;
    }

    vec2 texSize = textureSize(tex, 0).xy;
    vec2 coord = uvs - 0.5;

    fragColor = vec4(0, 0, 0, 1);

    vec2 redCoord = bulge(texSize, coord, 0.28);
    vec2 greenCoord = bulge(texSize, coord, 0.24);
    vec2 blueCoord = bulge(texSize, coord, 0.2);

    uvec3 redRandomValue = uvec3(redCoord * texSize, time);
    redRandomValue.x = uint(redRandomValue.x);
    redRandomValue.y = uint(redRandomValue.y);
    uvec3 greenRandomValue = uvec3(greenCoord * texSize, time);
    greenRandomValue.x = uint(greenRandomValue.x);
    greenRandomValue.y = uint(greenRandomValue.y);
    uvec3 blueRandomValue = uvec3(blueCoord * texSize, time);
    blueRandomValue.x = uint(blueRandomValue.x);
    blueRandomValue.y = uint(blueRandomValue.y);

    fragColor.r += ((texture_blurred(redCoord, texSize).r - 0.5) * 1.1 + 0.5)      * (0.8 + abs(sin(redCoord.y * texSize.y * M_PI / 2.0)) * 0.4)      + hash(redRandomValue).r * 0.03;
    fragColor.g += ((texture_blurred(greenCoord, texSize).g - 0.5) * 1.1 + 0.5)    * (0.8 + abs(sin(greenCoord.y * texSize.y * M_PI / 2.0)) * 0.4)    + hash(greenRandomValue).g * 0.03;
    fragColor.b += ((texture_blurred(blueCoord, texSize).b - 0.5) * 1.1 + 0.5)     * (0.8 + abs(sin(blueCoord.y * texSize.y * M_PI / 2.0)) * 0.4)     + hash(blueRandomValue).b * 0.03;

    fragColor *= 1.2 - length(coord) * 1.6;

    float edge = 0.01; // https://discourse.threejs.org/t/give-a-border-blur-effect-with-glsl/47863

    float xp = smoothstep(0.0, edge, redCoord.x);
    float xn = smoothstep(1.0, 1.0-edge, redCoord.x);
    float yp = smoothstep(0.0, edge, redCoord.y);
    float yn = smoothstep(1.0, 1.0-edge, redCoord.y);

    fragColor *= (xp*xn*yp*yn);
}