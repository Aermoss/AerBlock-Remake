import aerics, imgui, moss, glm, random, pickle
import pyglet.gl as gl

domainAPI = __import__("domain")
_chunk = __import__("_chunk")
world = __import__("world")

world.World.loadWorld = lambda self: None
world.World.updateDaylight = lambda self: None
world.World.tick = lambda self: None

class TooManyPlayers(domainAPI.ModBase):
    def __init__(self):
        super().__init__(domainAPI.getContextCurrent())

    def worldTick(self):
        self.client.send(("getTime", ))
        self.world.time, self.world.daylight = self.client.recv()
        self.world.chunkUpdateCounter = 0
        self.world.pendingChunkUpdateCount = sum(len(chunk.chunkUpdateQueue) for chunk in self.world.chunks.values())
        self.world.buildPendingChunks()
        self.world.processChunkUpdates()

    def loadWorld(self):
        self.client.send(("getWorldSize", ))
        worldSize = self.client.recv()
        data = bytearray()

        while len(data) != worldSize:
            self.client.send(("getWorldData", ))
            result = self.client.recv()
            if result == "finished": break
            data += result

        chunks = pickle.loads(data)

        for chunkPosition in chunks:
            self.world.chunks[chunkPosition] = _chunk.Chunk(self.world, glm.vec3(*chunkPosition))

            for i in chunks[chunkPosition]:
                if chunks[chunkPosition][i] == 16:
                    self.world.lightIncreaseQueue.append(((glm.vec3(*chunkPosition) * _chunk.chunkSize + glm.vec3(*i)).to_tuple(), 15))

                self.world.chunks[chunkPosition].blocks[i] = chunks[chunkPosition][i]

        for position in self.world.chunks:
            self.world.initSkylight(self.world.chunks[position])

        self.world.propagateIncrease(True)

        for position in self.world.chunks:
            self.world.chunks[position].updateSubchunks()
            self.world.chunks[position].update()

    def renderPlayers(self):
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glEnable(gl.GL_CULL_FACE)

        for i in self.playerLightLevels.copy():
            if i not in self.players:
                del self.playerLightLevels[i]

        for i in self.players:
            if i == self.id: continue
            position = glm.vec3(*self.players[i]["position"]) + glm.vec3(0, self.player.height / 2, 0)
            scale = glm.vec3((self.player.width + 0.2) / 2, self.player.height / 2, (self.player.width + 0.2) / 2)

            tempShader = self.player.shader
            self.player.shader = self.renderer.basicShader
            self.player.updateMatrices(updateFrustum = False)
            self.player.shader = tempShader

            if i not in self.playerLightLevels: self.playerLightLevels[i] = 0.0
            self.playerLightLevels[i] = glm.lerp(self.playerLightLevels[i], self.world.getLight(glm.floor(position)), 5.0 * self.window.deltaTime)

            self.renderer.basicShader.use()
            self.renderer.basicShader.setUniform1i("useAlbedoMap", 0)
            self.renderer.basicShader.setUniform3fv("albedoDefault", glm.value_ptr(glm.vec3(self.playerLightLevels[i] / 16.0)))
            model =  glm.rotate(glm.scale(glm.translate(glm.mat4(1.0), position), scale), glm.radians(-self.players[i]["yaw"]), glm.vec3(0.0, 1.0, 0.0))
            self.renderer.basicShader.setUniformMatrix4fv("model", moss.valptr(model))
            self.renderer.basicShader.setUniformMatrix3fv("normalMatrix", moss.valptr(glm.transpose(glm.inverse(glm.mat3(model)))))
            moss.renderCube()
            self.renderer.basicShader.unuse()

        gl.glDisable(gl.GL_CULL_FACE)
        gl.glDisable(gl.GL_DEPTH_TEST)

    def setup(self):
        self.reloadShaders = self.window.reloadShaders
        self.chatState, self.tabState = False, False
        self.chat, self.message = [], ""
        self.playerLightLevels = {}
        self.players, self.name = {}, "Unknown"
        self.client = aerics.Client("localhost", "5656", recv_size = 2048)
        self.connected, self.id = False, None

    def update(self):
        if not self.connected:
            self.context.setPhysicsState(False)
            self.context.setInputState(False)
            imgui.begin("TooManyPlayers")
            _, self.name = imgui.input_text("Name", self.name, 512)
            _, self.client.ip = imgui.input_text("Ip", self.client.ip, 512)
            _, self.client.port = imgui.input_text("Port", self.client.port, 512)

            if imgui.button("Connect"):
                self.client.port = int(self.client.port)
                self.client.connect()
                self.connected = True
                self.client.send(("getId", ))
                self.id = self.client.recv()
                self.client.send(("setName", self.name))
                result = self.client.recv()
                self.loadWorld()

            imgui.end()

        else:
            self.context.setPhysicsState(True)
            self.client.send(("updatePlayer", self.player.position, self.player.velocity, self.player.yaw, self.player.pitch))
            result = self.client.recv()
            self.client.send(("getPlayers", ))
            self.players = self.client.recv()

            if self.window.input.getKey(moss.KEY_TAB):
                if self.tabState:
                    self.chatState = not self.chatState
                    self.tabState = False

            else:
                self.tabState = True

            imgui.begin("TooManyPlayers - Chat")
            self.client.send(("pollMessages", ))

            while (result := self.client.recv()) != (None, None):
                if len(self.chat) == 16: self.chat.pop(0)
                self.chat.append(result)
                self.client.send(("pollMessages", ))

            for i in self.chat:
                imgui.text(f"{i[0]}: {i[1]}")

            if self.chatState:
                self.context.setInputState(False)
                self.window.reloadShaders = lambda: None

                _, self.message = imgui.input_text("", self.message, 512)
                imgui.same_line()

                if imgui.button("Send") or (self.window.input.getKey(moss.KEY_ENTER) and self.message != ""):
                    imgui.set_keyboard_focus_here(0)
                    self.client.send(("sendMessage", self.message))
                    result = self.client.recv()
                    self.message = ""
            
            else:
                self.context.setInputState(True)
                self.window.reloadShader = self.reloadShaders

            imgui.end()

            self.renderPlayers()
            self.worldTick()

    def exit(self):
        if self.connected:
            self.client.destroy()