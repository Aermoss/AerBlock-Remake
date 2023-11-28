import moss, glm, ctypes
import pyglet.gl as gl

from collections import deque

import subchunk

chunkSize = glm.vec3(16, 256, 16)
chunkUpdates = 4

class Chunk:
    def __init__(self, world, position):
        self.world, self.position = world, position
        self.worldPosition = self.position * chunkSize
        self.subchunks, self.blocks, self.lightmap = {}, {}, {}

        for x in range(int(chunkSize.x / subchunk.subchunkSize.x)):
            for y in range(int(chunkSize.y / subchunk.subchunkSize.y)):
                for z in range(int(chunkSize.z / subchunk.subchunkSize.z)):
                    self.subchunks[x, y, z] = subchunk.Subchunk(self, glm.vec3(x, y, z))

        for x in range(int(chunkSize.x)):
            for y in range(int(chunkSize.y)):
                for z in range(int(chunkSize.z)):
                    self.blocks[x, y, z], self.lightmap[x, y, z] = 0, 0

        self.chunkUpdateQueue = deque()

        self.vertexArray = moss.VAO()
        self.vertexArray.bind()
        self.vertexPositionBuffer = moss.VBO()
        self.texCoordBuffer = moss.VBO()
        self.shadingValueBuffer = moss.VBO()
        self.indexBuffer = moss.IBO()
        self.vertexArray.unbind()

    def getBlockLight(self, position):
        return self.lightmap[position] & 0xF

    def setBlockLight(self, position, value):
        self.lightmap[position] = (self.lightmap[position] & 0xF0) | value

    def getSkylight(self, position):
        return (self.lightmap[position] >> 4) & 0xF

    def setSkylight(self, position, value):
        self.lightmap[position] = (self.lightmap[position] & 0xF) | (value << 4)

    def getRawLight(self, position):
        return self.lightmap[position]

    def updateSubchunks(self):
        for position in self.subchunks:
            self.subchunks[position].update()

    def updateAtPosition(self, position):
        lx, ly, lz = glm.floor(position % subchunk.subchunkSize).to_tuple()
        sx, sy, sz = glm.floor(self.world.getLocalPosition(position) / subchunk.subchunkSize).to_tuple()

        self.subchunks[(sx, sy, sz)].update()

        def updateSubchunk(position):
            if position in self.subchunks:
                self.subchunks[position].update()

        if lx == subchunk.subchunkSize.x - 1: updateSubchunk((sx + 1, sy, sz))
        if lx == 0: updateSubchunk((sx - 1, sy, sz))

        if ly == subchunk.subchunkSize.y - 1: updateSubchunk((sx, sy + 1, sz))
        if ly == 0: updateSubchunk((sx, sy - 1, sz))

        if lz == subchunk.subchunkSize.z - 1: updateSubchunk((sx, sy, sz + 1))
        if lz == 0: updateSubchunk((sx, sy, sz - 1))

    def processChunkUpdates(self):
        for i in range(chunkUpdates):
            if self.chunkUpdateQueue:
                subchunk = self.chunkUpdateQueue.popleft()
                subchunk.update()
                self.world.chunkUpdateCounter += 1

                if not self.chunkUpdateQueue:
                    self.world.chunkBuildingQueue.append(self)
                    return

    def update(self):
        self.indexCounter = 0
        self.indices = []
        self.vertexPositions = []
        self.texCoords = []
        self.shadingValues = []

        for position in self.subchunks:
            subchunk = self.subchunks[position]

            self.vertexPositions += subchunk.vertexPositions
            self.texCoords += subchunk.texCoords
            self.shadingValues += subchunk.shadingValues

            indices = [index + self.indexCounter for index in subchunk.indices]
            
            self.indices.extend(indices)
            self.indexCounter += subchunk.indexCounter

        self.indexCount = len(self.indices)
        self.updateBuffers()
        
        del self.indices
        del self.vertexPositions
        del self.texCoords
        del self.shadingValues
    
    def updateBuffers(self):
        if not self.indexCounter:
            return
        
        self.indices = moss.mkarr(ctypes.c_uint32, self.indices)
        self.vertexPositions = moss.mkarr(ctypes.c_float, self.vertexPositions)
        self.texCoords = moss.mkarr(ctypes.c_float, self.texCoords)
        self.shadingValues = moss.mkarr(ctypes.c_float, self.shadingValues)

        self.vertexArray.bind()
        self.vertexPositionBuffer.bind()
        self.vertexPositionBuffer.bufferData(ctypes.sizeof(self.vertexPositions), self.vertexPositions)
        self.vertexArray.enableAttrib(0, 3, 0, 0)
        self.vertexPositionBuffer.unbind()
        self.texCoordBuffer.bind()
        self.texCoordBuffer.bufferData(ctypes.sizeof(self.texCoords), self.texCoords)
        self.vertexArray.enableAttrib(1, 3, 0, 0)
        self.texCoordBuffer.unbind()
        self.shadingValueBuffer.bind()
        self.shadingValueBuffer.bufferData(ctypes.sizeof(self.shadingValues), self.shadingValues)
        self.vertexArray.enableAttrib(2, 1, 3 * ctypes.sizeof(ctypes.c_float), 0 * ctypes.sizeof(ctypes.c_float))
        self.vertexArray.enableAttrib(3, 1, 3 * ctypes.sizeof(ctypes.c_float), 1 * ctypes.sizeof(ctypes.c_float))
        self.vertexArray.enableAttrib(4, 1, 3 * ctypes.sizeof(ctypes.c_float), 2 * ctypes.sizeof(ctypes.c_float))
        self.shadingValueBuffer.unbind()
        self.indexBuffer.bind()
        self.indexBuffer.bufferData(ctypes.sizeof(self.indices), self.indices),
        self.indexBuffer.unbind()
        self.vertexArray.unbind()

    def render(self):
        if not self.indexCounter:
            return

        self.vertexArray.bind()
        self.indexBuffer.bind()
        gl.glDrawElements(gl.GL_TRIANGLES, self.indexCount, gl.GL_UNSIGNED_INT, None)
        self.indexBuffer.unbind()
        self.vertexArray.unbind()