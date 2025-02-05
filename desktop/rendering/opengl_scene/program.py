from OpenGL.GL import *
from OpenGL.GL import shaders

# Static shared shaders
#shared_vertex = shaders.compileShader(open("zopengltest/Shared/vertex.glsl", 'r').read(), GL_VERTEX_SHADER)
#shared_fragment = shaders.compileShader(open("zopengltest/Shared/fragment.glsl", 'r').read(), GL_FRAGMENT_SHADER)

class OpenGLProgram:
    # To properly initialize program name has to point to a folder with used shaders
    # Shaders format: "{name}/vertex.glsl", "{name}/fragment.glsl"
    # Uniform blocks are not supported!!!
    def __init__(self, name) -> None:
        self.name = name
        self.vertex = shaders.compileShader(open(name + "/vertex.glsl", 'r').read(), GL_VERTEX_SHADER)
        self.fragment = shaders.compileShader(open(name + "/fragment.glsl", 'r').read(), GL_FRAGMENT_SHADER)
        self.program = shaders.compileProgram(self.vertex, self.fragment)
        uniCount = glGetProgramiv(self.program, GL_ACTIVE_UNIFORMS, None)
        self.uniforms = {}
        for i in range(uniCount):
            data = glGetActiveUniform(self.program, i)
            self.uniforms[data[0].decode("utf-8")] = i

    def use(self):
        glUseProgram(self.program)

    def _check_uniform_id(self, id):
        return id in self.uniforms

    def set_mat4(self, key, value):
        if not self._check_uniform_id(key):
            print(f"Uniform mat4 {key} was not found in program {self.name}")
            return
        glUniformMatrix4fv(self.uniforms[key], 1, GL_FALSE, value)

    def set_vec2(self, key, value):
        if not self._check_uniform_id(key):
            print(f"Uniform vec2 {key} was not found in program {self.name}")
            return
        glUniform2f(self.uniforms[key], *value)

    def set_vec3(self, key, value):
        if not self._check_uniform_id(key):
            print(f"Uniform vec3 {key} was not found in program {self.name}")
            return
        glUniform3f(self.uniforms[key], *value)

    def set_float(self, key, value):
        if not self._check_uniform_id(key):
            print(f"Uniform float {key} was not found in program {self.name}")
            return
        glUniform1f(self.uniforms[key], value)
