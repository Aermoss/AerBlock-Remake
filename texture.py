import pyglet.gl as gl
import pyglet, ctypes

class TextureManager:
    def __init__(self, width, height, maxCount):
        self.width = width
        self.height = height
        self.maxCount = maxCount
        self.textures = []

        self.id = ctypes.c_uint32()
        gl.glGenTextures(1, ctypes.byref(self.id))
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.id)
        gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_MIN_FILTER, gl.GL_NEAREST)
        gl.glTexParameteri(gl.GL_TEXTURE_2D_ARRAY, gl.GL_TEXTURE_MAG_FILTER, gl.GL_NEAREST)
        gl.glTexImage3D(gl.GL_TEXTURE_2D_ARRAY, 0, gl.GL_RGBA, self.width, self.height, self.maxCount, 0, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, None)
    
    def generateMipmaps(self):
        gl.glGenerateMipmap(gl.GL_TEXTURE_2D_ARRAY)

    def bind(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.id)

    def unbind(self):
        gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, 0)
    
    def addTexture(self, textureName):
        if not textureName in self.textures:
            self.textures.append(textureName)
            texture = pyglet.image.load(f"textures/{textureName}.png").get_image_data()
            index = self.textures.index(textureName)
            gl.glBindTexture(gl.GL_TEXTURE_2D_ARRAY, self.id)
            gl.glTexSubImage3D(gl.GL_TEXTURE_2D_ARRAY, 0, 0, 0, index, self.width, self.height, 1, gl.GL_RGBA, gl.GL_UNSIGNED_BYTE, texture.get_data("RGBA", texture.width * 4))
            return index
        
        else:
            return self.textures.index(textureName)