import sys, os, moss, glm, ctypes, glfw, pyglet, random, math, threading
from collections import deque
import pyglet.gl as gl

import world, player

def shaderReloadFix(self):
    if self.vertexFilePath != None:
        self.vertexSource = moss.readFile(self.vertexFilePath)

    if self.fragmentFilePath != None:
        self.fragmentSource = moss.readFile(self.fragmentFilePath)

    if self.geometryFilePath != None:
        self.geometrySource = moss.readFile(self.geometryFilePath)

    self.delete()
    self.__init__(self.vertexSource, self.fragmentSource, self.geometrySource, self.vertexFilePath, self.fragmentFilePath, self.geometryFilePath)

moss.Shader.reload = shaderReloadFix

class App:
    def __init__(self):
        self.window = moss.Window(
            title = "AerBlock Remake",
            width = 1600, # moss.context.displayWidth
            height = 800, # moss.context.displayHeight
            backgroundColor = moss.Color(0.0, 0.0, 0.0),
            fullscreen = False, samples = 16
        )
        
        self.window.event(self.setup)
        self.window.event(self.update)
        self.window.event(self.exit)

    def setup(self, window):
        self.renderer = moss.Renderer(self.window)
        self.renderer.bindTextures = lambda: None

        self.shader = moss.Shader(
            vertexFilePath = "shaders/default.vert",
            fragmentFilePath = "shaders/default.frag",
            geometryFilePath = "shaders/default.geom"
        )

        self.world = world.World(self.window)
        self.player = player.Player(
            self.world, self.shader, fov = 90,
            position = glm.vec3(-5.0, 30.0, -5.0)
        )
        self.world.player = self.player

    def update(self, window):
        self.window.clear()
        self.player.proccessInputs()
        self.player.updateMatrices()

        if self.window.input.getKey(moss.KEY_R):
            self.window.reloadShaders()

        self.world.tick()
        self.world.prepareRendering()

        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)
        self.world.render(self.shader)
        self.renderer.render(None, False, False)
        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_DEPTH_TEST)

    def exit(self, window):
        self.shader.delete()

    def run(self):
        moss.run()

def main(argv):
    app = App()
    app.run()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))