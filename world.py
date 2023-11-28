import ctypes, glm, random, moss, math
from functools import cmp_to_key
from collections import deque

import _chunk, texture, models, util, block

class World:
    def __init__(self, window):
        self.window = window
        self.textureManager = texture.TextureManager(width = 16, height = 16, maxCount = 256)
        self.chunks, self.daylight, self.timeState = {}, 1.0, True

        self.textureManager.addTexture("grass_block_side_overlay")

        self.blockTypes = [None] + [
            block.BlockType(self.textureManager, name = "cobblestone", model = models.Cube, textures = ["cobblestone"] * 6),
            block.BlockType(self.textureManager, name = "grass_block", model = models.Cube, textures = ["grass_block_side", "grass_block_side", "grass_block_top", "dirt", "grass_block_side", "grass_block_side"]),
            block.BlockType(self.textureManager, name = "grass", model = models.Plant, textures = ["grass"] * 4),
            block.BlockType(self.textureManager, name = "tall_grass_bottom", model = models.Plant, textures = ["tall_grass_bottom"] * 4),
            block.BlockType(self.textureManager, name = "tall_grass_top", model = models.Plant, textures = ["tall_grass_top"] * 4),
            block.BlockType(self.textureManager, name = "dirt", model = models.Cube, textures = ["dirt"] * 6),
            block.BlockType(self.textureManager, name = "stone", model = models.Cube, textures = ["stone"] * 6),
            block.BlockType(self.textureManager, name = "sand", model = models.Cube, textures = ["sand"] * 6),
            block.BlockType(self.textureManager, name = "planks", model = models.Cube, textures = ["spruce_planks"] * 6),
            block.BlockType(self.textureManager, name = "log", model = models.Cube, textures = ["oak_log", "oak_log", "oak_log_top", "oak_log_top", "oak_log", "oak_log"]),
            block.BlockType(self.textureManager, name = "daisy", model = models.Plant, textures = ["dandelion"] * 4),
            block.BlockType(self.textureManager, name = "rose", model = models.Plant, textures = ["poppy"] * 4),
            block.BlockType(self.textureManager, name = "cactus", model = models.Cactus, textures = ["cactus_side", "cactus_side", "cactus_top", "cactus_bottom", "cactus_side", "cactus_side"]),
            block.BlockType(self.textureManager, name = "dead_bush", model = models.Plant, textures = ["dead_bush"] * 4),
            block.BlockType(self.textureManager, name = "glass", model = models.Cube, textures = ["glass"] * 6, isGlass = True, isTransparent = True),
            block.BlockType(self.textureManager, name = "torch", model = models.Torch, textures = ["torch", "torch", "torch_top", "torch_top", "torch", "torch"]),
            block.BlockType(self.textureManager, name = "azure_bluet", model = models.Plant, textures = ["azure_bluet"] * 4),
            block.BlockType(self.textureManager, name = "blue_orchid", model = models.Plant, textures = ["blue_orchid"] * 4),
            block.BlockType(self.textureManager, name = "allium", model = models.Plant, textures = ["allium"] * 4)
        ]

        self.lightBlocks = [16]
        self.skylightIncreaseQueue = deque()
        self.lightIncreaseQueue = deque()
        self.chunkUpdateQueue = deque()
        self.chunkBuildingQueue = deque()
        self.visibleChunks = []
        self.sortedChunks = []
        self.pendingChunkUpdateCount = 0
        self.chunkUpdateCounter = 0
        self.daylight, self.incrementer = 0, 0
        self.time, self.c = 0, 0

        # self.textureManager.bind()
        # self.textureManager.generateMipmaps()
        # self.textureManager.unbind()

        for x in range(2):
            for z in range(2):
                chunkPosition = (x - 1, 0, z - 1)
                current_chunk = _chunk.Chunk(self, glm.vec3(*chunkPosition))

                for i in range(int(_chunk.chunkSize.x)):
                    for j in range(int(_chunk.chunkSize.y)):
                        for k in range(int(_chunk.chunkSize.z)):
                            if j == 15:
                                blockNumber = random.choices([0, 15, 10, 18, 19, 3, 4, 16], [20, 1, 1, 2, 1, 5, 2, 1])[0]
                                if blockNumber == 16:
                                    self.lightIncreaseQueue.append(((glm.vec3(*chunkPosition) * _chunk.chunkSize + glm.vec3(i, j, k)).to_tuple(), 15))
                                current_chunk.blocks[i, j, k] = blockNumber
                                if blockNumber == 4: current_chunk.blocks[i, j + 1, k] = 5
                            elif j == 14: current_chunk.blocks[i, j, k] = 2
                            elif j > 10 and j < 15: current_chunk.blocks[i, j, k] = 6
                            elif j < 15: current_chunk.blocks[i, j, k] = 7

                self.chunks[chunkPosition] = current_chunk

        for position in self.chunks:
            self.initSkylight(self.chunks[position])

        self.propagateIncrease(True)

        for position in self.chunks:
            self.chunks[position].updateSubchunks()
            self.chunks[position].update()

    def setBlock(self, position, number):
        x, y, z = position
        cx, cy, cz = chunkPosition = self.getChunkPosition(position)

        if not chunkPosition in self.chunks:
            if number == 0:
                return

            self.createChunk(chunkPosition)

        if self.getBlockNumber(position) == number:
            return
        
        lx, ly, lz = local = self.getLocalPosition(position)
        self.chunks[chunkPosition].blocks[local] = number
        self.chunks[chunkPosition].modified = True
        self.chunks[chunkPosition].updateAtPosition(position)

        if number:
            if number in self.lightBlocks:
                self.increaseLight(position, 15)

            elif self.blockTypes[number].isTransparent != 2:
                self.decreaseLight(position)
                self.decreaseSkylight(position)
        
        elif not number:
            self.decreaseLight(position)
            self.decreaseSkylight(position)

        def tryUpdate(chunkPosition, position):
            if chunkPosition in self.chunks:
                self.chunks[chunkPosition].updateAtPosition(position)
        
        if lx == _chunk.chunkSize.x - 1: tryUpdate((cx + 1, cy, cz), glm.vec3(x + 1, y, z))
        if lx == 0: tryUpdate((cx - 1, cy, cz), glm.vec3(x - 1, y, z))

        if ly == _chunk.chunkSize.y - 1: tryUpdate((cx, cy + 1, cz), glm.vec3(x, y + 1, z))
        if ly == 0: tryUpdate((cx, cy - 1, cz), glm.vec3(x, y - 1, z))

        if lz == _chunk.chunkSize.z - 1: tryUpdate((cx, cy, cz + 1), glm.vec3(x, y, z + 1))
        if lz == 0: tryUpdate((cx, cy, cz - 1), glm.vec3(x, y, z - 1))

    def render(self, shader: moss.Shader):
        shader.use()
        daylightMultiplier = self.daylight / 1800
        shader.setUniform1f("daylight", daylightMultiplier)
        self.window.backgroundColor = moss.Color(
             0.5 * (daylightMultiplier - 0.26) * 255.0,
             0.8 * (daylightMultiplier - 0.26) * 255.0,
            (daylightMultiplier - 0.26) * 1.36 * 255.0, 255.0)
        self.textureManager.bind()

        for chunk in self.visibleChunks:
            chunk.render()

        self.textureManager.unbind()
        shader.unuse()

    def updateDaylight(self):
        if self.incrementer == -1:
            if self.daylight < 480:
                self.incrementer = 0
                
        elif self.incrementer == 1:
            if self.daylight >= 1800:
                self.incrementer = 0

        if int(self.time) % 36000 > -100 and int(self.time) % 36000 < 100:
            self.incrementer = 1

        elif int(self.time) % 36000 > 17000 and int(self.time) % 36000 < 19000:
            self.incrementer = -1

        self.daylight += self.incrementer * self.window.deltaTime * 30
    
    def buildPendingChunks(self):
        if self.chunkBuildingQueue:
            pendingChunk = self.chunkBuildingQueue.popleft()
            pendingChunk.update()

    def processChunkUpdates(self):
        for chunk in self.visibleChunks:
            chunk.processChunkUpdates()
    
    def tick(self):
        self.chunkUpdateCounter = 0
        self.time += 1 * self.window.deltaTime * 150
        self.pendingChunkUpdateCount = sum(len(chunk.chunkUpdateQueue) for chunk in self.chunks.values())
        self.updateDaylight()
        self.buildPendingChunks()
        self.processChunkUpdates()

    def isOpaqueBlock(self, position):
        blockType = self.blockTypes[self.getBlockNumber(position)]

        if blockType is None:
            return False
        
        return not blockType.isTransparent
    
    def getTransparency(self, position):
        blockType = self.blockTypes[self.getBlockNumber(position)]

        if not blockType:
            return 2
        
        return blockType.isTransparent

    def getChunkPosition(self, position):
        return glm.floor(position // _chunk.chunkSize).to_tuple()

    def getLocalPosition(self, position):
        return glm.floor(position % _chunk.chunkSize).to_tuple()

    def getBlockNumber(self, position):
        chunkPosition = self.getChunkPosition(position)

        if not chunkPosition in self.chunks:
            return 0

        local = self.getLocalPosition(position)
        return self.chunks[chunkPosition].blocks[local]

    def getRawLight(self, position):
        chunk = self.chunks.get(self.getChunkPosition(position), None)

        if not chunk:
            return 15 << 4
        
        local_position = self.getLocalPosition(position)
        return chunk.getRawLight(local_position)
    
    def getLight(self, position):
        chunk = self.chunks.get(self.getChunkPosition(position), None)

        if not chunk:
            return 0
        
        localPosition = self.getLocalPosition(position)
        return chunk.getBlockLight(localPosition)
    
    def getSkylight(self, position):
        chunk = self.chunks.get(self.getChunkPosition(position), None)

        if not chunk:
            return 15
        
        localPosition = self.getLocalPosition(position)
        return chunk.getSkylight(localPosition)
    
    def setLight(self, position, light):
        chunk = self.chunks.get(self.getChunkPosition(position), None)
        localPosition = self.getLocalPosition(position)
        chunk.setBlockLight(localPosition, light)
    
    def setSkylight(self, position, light):
        chunk = self.chunks.get(self.getChunkPosition(position), None)
        localPosition = self.getLocalPosition(position)
        chunk.setSkylight(localPosition, light)

    def increaseLight(self, position, newlight, lightUpdate = True):
        chunk = self.chunks[self.getChunkPosition(position)]
        local = self.getLocalPosition(position)
        chunk.setBlockLight(local, newlight)
        self.lightIncreaseQueue.append((position, newlight))
        self.propagateIncrease(lightUpdate)

    def propagateIncrease(self, lightUpdate):
        while self.lightIncreaseQueue:
            pos, lightLevel = self.lightIncreaseQueue.popleft()			

            for direction in util.directions:
                neighbourPos = pos + direction

                chunk = self.chunks.get(self.getChunkPosition(neighbourPos), None)
                if not chunk: continue
                local = self.getLocalPosition(neighbourPos)

                if not self.isOpaqueBlock(neighbourPos) and chunk.getBlockLight(local) + 2 <= lightLevel:
                    chunk.setBlockLight(local, lightLevel - 1)

                    self.lightIncreaseQueue.append((neighbourPos, lightLevel - 1))

                    if lightUpdate:
                        chunk.updateAtPosition(neighbourPos)

    def initSkylight(self, chunk: _chunk.Chunk):
        height = 0
        
        for x in range(int(_chunk.chunkSize.x)):
            for z in range(int(_chunk.chunkSize.z)):
                for y in range(int(_chunk.chunkSize.y) - 1, -1, -1):
                    if chunk.blocks[x, y, z]:
                        break

                if y > height:
                    height = y

        for x in range(int(_chunk.chunkSize.x)):
            for z in range(int(_chunk.chunkSize.z)):
                for y in range(int(_chunk.chunkSize.y) - 1, height, -1):
                    chunk.setSkylight((x, y, z), 15)

                position = glm.vec3(_chunk.chunkSize.x * chunk.position.x + x, y, _chunk.chunkSize.z * chunk.position.z + z)
                self.skylightIncreaseQueue.append((position, 15))

        self.propagateSkylightIncrease(False)

    def propagateSkylightIncrease(self, lightUpdate):
        while self.skylightIncreaseQueue:
            position, lightLevel = self.skylightIncreaseQueue.popleft()

            for direction in util.directions:
                neighbourPos = position + direction
                if neighbourPos.y > _chunk.chunkSize.y:
                    continue

                chunk = self.chunks.get(self.getChunkPosition(neighbourPos), None)
                if not chunk: continue
                localPos = self.getLocalPosition(neighbourPos)

                transparency = self.getTransparency(neighbourPos)

                if transparency and chunk.getSkylight(localPos) < lightLevel:
                    newlight = lightLevel - (2 - transparency)

                    if lightUpdate:
                        chunk.updateAtPosition(neighbourPos)

                    if direction.y == -1:
                        chunk.setSkylight(localPos, newlight)
                        self.skylightIncreaseQueue.append((neighbourPos, newlight))

                    elif chunk.getSkylight(localPos) + 2 <= lightLevel:
                        chunk.setSkylight(localPos, newlight - 1)
                        self.skylightIncreaseQueue.append((neighbourPos, newlight - 1))

    def decreaseLight(self, position):
        chunk = self.chunks[self.getChunkPosition(position)]
        local = self.getLocalPosition(position)
        oldLight = chunk.getBlockLight(local)
        chunk.setBlockLight(local, 0)
        self.lightDecreaseQueue.append((position, oldLight))
        self.propagateDecrease(True)
        self.propagateIncrease(True)
    
    def propagateDecrease(self, lightUpdate):
        while self.lightDecreaseQueue:
            pos, lightLevel = self.lightDecreaseQueue.popleft()

            for direction in util.directions:
                neighbourPos = pos + direction

                chunk = self.chunks.get(self.getChunkPosition(neighbourPos), None)
                if not chunk: continue
                local = self.getLocalPosition(neighbourPos)

                if self.getBlockNumber(neighbourPos) in self.lightBlocks:
                    self.lightIncreaseQueue.append((neighbourPos, 15))
                    continue

                if not self.isOpaqueBlock(neighbourPos):
                    neighbourLevel = chunk.getBlockLight(local)
                    if not neighbourLevel: continue

                    if neighbourLevel < lightLevel:
                        chunk.setBlockLight(local, 0)

                        if lightUpdate:
                            chunk.updateAtPosition(neighbourPos)

                        self.lightDecreaseQueue.append((neighbourPos, neighbourLevel))

                    elif neighbourLevel >= lightLevel:
                        self.lightIncreaseQueue.append((neighbourPos, neighbourLevel))

    def decreaseSkylight(self, position, lightUpdate = True):
        chunk = self.chunks.get(self.getChunkPosition(position), None)
        local = self.getLocalPosition(position)
        oldLight = chunk.getSkyLight(local)
        chunk.setSkyLight(local, 0)
        self.skylightDecreaseQueue.append((position, oldLight))
        self.propagateSkylightDecrease(lightUpdate)
        self.propagateSkylightIncrease(lightUpdate)
    
    def propagateSkylightDecrease(self, lightUpdate = True):
        while self.skylightDecreaseQueue:
            position, lightLevel = self.skylightDecreaseQueue.popleft()

            for direction in util.directions:
                neighbourPos = position + direction

                chunk = self.chunks.get(self.getChunkPosition(neighbourPos), None)
                if not chunk: continue
                local = self.getLocalPosition(neighbourPos)

                if self.getTransparency(neighbourPos):
                    neighbourLevel = chunk.getSkyLight(local)
                    if not neighbourLevel: continue

                    if direction.y == -1 or neighbourLevel < lightLevel:
                        chunk.setSkyLight(local, 0)

                        if lightUpdate:
                            chunk.updateAtPosition(neighbourPos)

                        self.skylightDecreaseQueue.append((neighbourPos, neighbourLevel))

                    elif neighbourLevel >= lightLevel:
                        self.skylightIncreaseQueue.append((neighbourPos, neighbourLevel))

    def canRenderChunk(self, position):
        RENDER_DISTANCE = 4
        return self.player.checkInFrustum(position) and math.dist(self.getChunkPosition(glm.vec3(*self.player.position)), position) <= RENDER_DISTANCE

    def prepareRendering(self):
        self.visibleChunks = [self.chunks[position] for position in self.chunks if self.canRenderChunk(glm.vec3(*position))]
        self.sortChunks()
    
    def sortChunks(self):
        currentChunk = self.getChunkPosition(glm.vec3(*self.player.position))
        self.visibleChunks.sort(key = cmp_to_key(lambda a, b: math.dist(currentChunk, a.position) - math.dist(currentChunk, b.position)))
        self.sortedChunks = tuple(reversed(self.visibleChunks))