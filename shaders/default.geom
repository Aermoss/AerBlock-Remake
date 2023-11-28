#version 460

layout (triangles) in;
layout (triangle_strip, max_vertices = 3) out;

in vec3 geomPosition[];
in vec3 geomTexCoord[];
in vec3 geomLight[];
in vec3 geomCameraPosition[];

in mat4 geomProj[];
in mat4 geomView[];

out vec3 fragPosition;
out vec3 fragTexCoord;
out vec3 fragLight;
out vec3 fragCameraPosition;

out vec3 fragNormal;

void main(void) {
    vec3 a = (gl_in[1].gl_Position - gl_in[0].gl_Position).xyz;
    vec3 b = (gl_in[2].gl_Position - gl_in[0].gl_Position).xyz;
    vec3 N = normalize(cross(b, a));

    for (int i = 0; i < gl_in.length(); ++i) {
        gl_Position = geomProj[i] * geomView[i] * gl_in[i].gl_Position;
        fragPosition = geomPosition[i];
        fragTexCoord = geomTexCoord[i];
        fragLight = geomLight[i];
        fragCameraPosition = geomCameraPosition[i];
        fragNormal = N;
        EmitVertex();
    }

    EndPrimitive();
}