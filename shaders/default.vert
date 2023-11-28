#version 460

layout (location = 0) in vec3 position;
layout (location = 1) in vec3 texCoord;
layout (location = 2) in float shading;
layout (location = 3) in float light;
layout (location = 4) in float skylight;

out vec3 geomPosition;
out vec3 geomTexCoord;
out vec3 geomLight;
out vec3 geomCameraPosition;

out mat4 geomProj;
out mat4 geomView;

uniform mat4 view;
uniform mat4 proj;

uniform vec3 cameraPosition;
uniform float daylight;

void main(void) {
    geomPosition = position;
    geomTexCoord = texCoord;
    geomProj = proj;
    geomView = view;
    geomCameraPosition = cameraPosition;

    float blocklightMultiplier = pow(0.8f, 15.0f - light);
	float skylightMultiplier = pow(0.8f, 15.0f - skylight);

	geomLight = vec3(
		clamp(blocklightMultiplier * 1.5f, skylightMultiplier * daylight, 1.0f),
		clamp(blocklightMultiplier * 1.25f, skylightMultiplier * daylight, 1.0f),
		clamp(skylightMultiplier * (2.0f - pow(daylight, 2)), blocklightMultiplier, 1.0f)
	) * shading;

    gl_Position = vec4(position, 1.0f);
}