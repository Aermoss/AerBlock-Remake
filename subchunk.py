import glm, ctypes
import util

subchunkSize = glm.vec3(4, 4, 4)

class Subchunk:
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position
        self.world = self.parent.world
        self.localPosition = self.position * subchunkSize
        self.worldPosition = self.parent.worldPosition + self.localPosition

    def getRawLight(self, pos, direction):
        if not direction: lightLevels = self.world.getLight(pos)
        else: lightLevels = self.world.getLight(direction)
        return [lightLevels] * 4

    def getRawSkylight(self, pos, direction):
        if not direction: lightLevels = self.world.getSkylight(pos)
        else: lightLevels = self.world.getSkylight(direction)
        return [lightLevels] * 4

    def getFaceAO(self, s1, s2, s3, s4, s5, s6, s7, s8):
        vertex1 = util.ao(s2, s4, s1)
        vertex2 = util.ao(s4, s7, s6)
        vertex3 = util.ao(s5, s7, s8)
        vertex4 = util.ao(s2, s5, s3)
        return (vertex1, vertex2, vertex3, vertex4)

    def getSmoothFaceLight(self, light, light1, light2, light3, light4, light5, light6, light7, light8):
        vertex1 = util.smooth(light, light2, light4, light1)
        vertex2 = util.smooth(light, light4, light7, light6)
        vertex3 = util.smooth(light, light5, light7, light8)
        vertex4 = util.smooth(light, light2, light5, light3)
        return (vertex1, vertex2, vertex3, vertex4)

    def getNeighbourVoxels(self, direction, index):
        if not index:
            neighbours = [
                direction + util.up + util.south, direction + util.up, direction + util.up + util.north,
                direction + util.south, direction + util.north,
                direction + util.down + util.south, direction + util.down, direction + util.down + util.north
            ]
        elif index == 1:
            neighbours = [
                direction + util.up + util.north, direction + util.up, direction + util.up + util.south,
                direction + util.north, direction + util.south,
                direction + util.down + util.north, direction + util.down, direction + util.down + util.south
            ]
        elif index == 2:
            neighbours = [
                direction + util.south + util.east, direction + util.south, direction + util.south + util.west,
                direction + util.east, direction + util.west,
                direction + util.north + util.east, direction + util.north, direction + util.north + util.west
            ]
        elif index == 3:
            neighbours = [
                direction + util.south + util.west, direction + util.south, direction + util.south + util.east,
                direction + util.west, direction + util.east,
                direction + util.north + util.west, direction + util.north, direction + util.north + util.east
            ]
        elif index == 4:
            neighbours = [
                direction + util.up + util.west, direction + util.up, direction + util.up + util.east,
                direction + util.west, direction + util.east,
                direction + util.down + util.west, direction + util.down, direction + util.down + util.east
            ]
        elif index == 5:
            neighbours = [
                direction + util.up + util.east, direction + util.up, direction + util.up + util.west,
                direction + util.east, direction + util.west,
                direction + util.down + util.east, direction + util.down, direction + util.down + util.west
            ]
        else:
            return []
        
        return neighbours

    def getLight(self, blockNumber, index, position, direction):
        if not direction or blockNumber in self.world.lightBlocks:
            return [self.world.getLight(position)] * 4

        neighbours = self.getNeighbourVoxels(direction, index)
        nlights = (self.world.getLight(neighbourPos) for neighbourPos in neighbours)
        return self.getSmoothFaceLight(self.world.getLight(direction), *nlights)

    def getSkylight(self, blockNumber, index, position, direction):
        if not direction or blockNumber in self.world.lightBlocks:
            return [self.world.getSkylight(position)] * 4

        neighbours = self.getNeighbourVoxels(direction, index)
        nlights = (self.world.getSkylight(neighbourPos) for neighbourPos in neighbours)
        return self.getSmoothFaceLight(self.world.getSkylight(direction), *nlights)

    def getShading(self, blockNumber, blockType, index, direction):
        rawShading = blockType.shadingValues[index]

        if not blockType.isBlock or blockNumber in self.world.lightBlocks:
            return rawShading

        neighbours = self.getNeighbourVoxels(direction, index)
        neighbourOpacity = (self.world.isOpaqueBlock(neighbourPos) for neighbourPos in neighbours)
        faceAO = self.getFaceAO(*neighbourOpacity)
        return [a * b for a, b in zip(faceAO, rawShading)]

    def update(self):
        self.indexCounter = 0
        self.indices = []
        self.vertexPositions = []
        self.texCoords = []
        self.shadingValues = []

        def addFace(blockType, blockNumber, index, parentPosition, position, direction = None):
            vertexPositions = blockType.vertexPositions[index].copy()
            shading = self.getShading(blockNumber, blockType, index, direction)
            light = self.getLight(blockNumber, index, position, direction)
            skylight = self.getSkylight(blockNumber, index, position, direction)

            for i in range(4):
                vertexPositions[i * 3 + 0] += position.x
                vertexPositions[i * 3 + 1] += position.y
                vertexPositions[i * 3 + 2] += position.z
                self.shadingValues += [shading[i], light[i], skylight[i]]
            
            self.vertexPositions += vertexPositions
            indices = [0, 1, 2, 0, 2, 3]

            for i in range(6):
                indices[i] += self.indexCounter
            
            self.indices.extend(indices)
            self.indexCounter += 4

            self.texCoords += blockType.texCoords[index]

        def shouldRender(blockType, blockNumber, position):
            if not self.world.isOpaqueBlock(position):
                if blockType.isGlass and self.world.getBlockNumber(position) == blockNumber:
                    return False
                
                return True
            
            return False

        for x in range(int(subchunkSize.x)):
            for y in range(int(subchunkSize.y)):
                for z in range(int(subchunkSize.z)):
                    parentPosition = self.localPosition + glm.vec3(x, y, z)
                    blockNumber = self.parent.blocks[parentPosition.x, parentPosition.y, parentPosition.z]

                    if blockNumber != 0:
                        blockType = self.world.blockTypes[blockNumber]
                        position = self.worldPosition + glm.vec3(x, y, z)

                        if blockType.isBlock:
                            for i in range(6):
                                if shouldRender(blockType, blockNumber, position + util.directions[i]):
                                    addFace(blockType, blockNumber, i, parentPosition, position, position + util.directions[i])

                        else:
                            for i in range(len(blockType.vertexPositions)):
                                addFace(blockType, blockNumber, i, parentPosition, position)