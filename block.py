import models, collider

class BlockType:
    def __init__(self, textureManager, name, model, textures, isBlock = None, isTransparent = None, isGlass = None):
        self.name = name
        self.textures = textures
        self.model = model
        self.isBlock = model.isBlock if isBlock is None else isBlock
        self.isTransparent = model.isTransparent if isTransparent is None else isTransparent
        self.isGlass = model.isGlass if isGlass is None else isGlass

        self.colliders = []

        for _collider in model.colliders:
            self.colliders.append(collider.Collider(*_collider))

        self.vertexPositions = self.model.vertexPositions
        self.texCoords = self.model.texCoords.copy()
        self.shadingValues = self.model.shadingValues

        for index, texture in enumerate(self.textures):
            textureIndex = textureManager.addTexture(texture)
            self.texCoords[index] = self.texCoords[index].copy()

            for vertex in range(4):
                self.texCoords[index][vertex * 3 + 2] = textureIndex