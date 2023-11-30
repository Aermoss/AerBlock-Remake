#version 460

out vec4 fragColor;

uniform sampler2DArray albedoMap;

in vec3 fragPosition;
in vec3 fragTexCoord;
in vec3 fragLight;
in vec3 fragCameraPosition;
in vec3 fragNormal;

vec3 defaultValues = vec3(142, 185, 113);
vec3 plains = vec3(145, 189, 89);
vec3 snowyPlains = vec3(128, 180, 151);
vec3 lushCaves = vec3(185, 183, 91);
vec3 desert = vec3(191, 183, 85);
vec3 badlands = vec3(144, 129, 77);
vec3 swamp = vec3(106, 112, 57);
vec3 forest = vec3(121, 192, 90);
vec3 darkForest = vec3(80, 122, 50);
vec3 taiga = vec3(134, 183, 131);
vec3 jungle = vec3(89, 201, 60);
vec3 meadow = vec3(131, 187, 109);
vec3 cherryGrove = vec3(182, 219, 97);
vec3 magenta = vec3(255, 0, 255);
vec3 cyan = vec3(0, 255, 255);

void main(void) {
    vec4 albedo = texture(albedoMap, fragTexCoord);
    vec4 grassColor = vec4(cyan / 255.0f, 1.0f);

    if (fragTexCoord.z == 2) {
        vec4 color = texture(albedoMap, vec3(fragTexCoord.xy, 0));
        if (color.a != 0.0f) albedo = color * grassColor;
    }

    if (fragTexCoord.z == 3 || fragTexCoord.z == 5 || fragTexCoord.z == 6 || fragTexCoord.z == 7)
        albedo = albedo * grassColor;

    if (albedo.a == 0.0f)
        discard;

    fragColor = albedo * vec4(fragLight, 1.0f);
}