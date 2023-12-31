class Cube:
    isBlock = True
    isTransparent = False
    isGlass = False

    colliders = [
        [
            (-0.5, -0.5, -0.5),
            ( 0.5,  0.5,  0.5)
        ]
    ]

    vertexPositions = [
        [ 0.5,  0.5,  0.5,  0.5, -0.5,  0.5,  0.5, -0.5, -0.5,  0.5,  0.5, -0.5],
        [-0.5,  0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5,  0.5,  0.5],
        [ 0.5,  0.5,  0.5,  0.5,  0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5,  0.5],
        [-0.5, -0.5,  0.5, -0.5, -0.5, -0.5,  0.5, -0.5, -0.5,  0.5, -0.5,  0.5],
        [-0.5,  0.5,  0.5, -0.5, -0.5,  0.5,  0.5, -0.5,  0.5,  0.5,  0.5,  0.5],
        [ 0.5,  0.5, -0.5,  0.5, -0.5, -0.5, -0.5, -0.5, -0.5, -0.5,  0.5, -0.5]
    ]

    texCoords = [
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0]
    ]

    shadingValues = [
        [0.6, 0.6, 0.6, 0.6],
        [0.6, 0.6, 0.6, 0.6],
        [1.0, 1.0, 1.0, 1.0],
        [0.4, 0.4, 0.4, 0.4],
        [0.8, 0.8, 0.8, 0.8],
        [0.8, 0.8, 0.8, 0.8]
    ]

class Plant:
    isBlock = False
    isTransparent = True
    isGlass = False

    colliders = []

    vertexPositions = [
        [-0.3536, 0.5000,  0.3536, -0.3536, -0.5000,  0.3536,  0.3536, -0.5000, -0.3536,  0.3536, 0.5000, -0.3536],
        [-0.3536, 0.5000, -0.3536, -0.3536, -0.5000, -0.3536,  0.3536, -0.5000,  0.3536,  0.3536, 0.5000,  0.3536],
        [ 0.3536, 0.5000, -0.3536,  0.3536, -0.5000, -0.3536, -0.3536, -0.5000,  0.3536, -0.3536, 0.5000,  0.3536],
        [ 0.3536, 0.5000,  0.3536,  0.3536, -0.5000,  0.3536, -0.3536, -0.5000, -0.3536, -0.3536, 0.5000, -0.3536]
    ]

    texCoords = [
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0]
    ]

    shadingValues = [
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0],
        [1.0, 1.0, 1.0, 1.0]
    ]

class Cactus:
    isTransparent = True
    isBlock = False
    isGlass = False

    colliders = [
        [
            (-0.4375, -0.5, -0.4375),
            ( 0.4375,  0.5,  0.4375)
        ]
    ]

    vertexPositions = [
        [ 0.4375,  0.5000,  0.5000,  0.4375, -0.5000,  0.5000,  0.4375, -0.5000, -0.5000,  0.4375,  0.5000, -0.5000],
        [-0.4375,  0.5000, -0.5000, -0.4375, -0.5000, -0.5000, -0.4375, -0.5000,  0.5000, -0.4375,  0.5000,  0.5000],
        [ 0.5000,  0.5000,  0.5000,  0.5000,  0.5000, -0.5000, -0.5000,  0.5000, -0.5000, -0.5000,  0.5000,  0.5000],
        [-0.5000, -0.5000,  0.5000, -0.5000, -0.5000, -0.5000,  0.5000, -0.5000, -0.5000,  0.5000, -0.5000,  0.5000],
        [-0.5000,  0.5000,  0.4375, -0.5000, -0.5000,  0.4375,  0.5000, -0.5000,  0.4375,  0.5000,  0.5000,  0.4375],
        [ 0.5000,  0.5000, -0.4375,  0.5000, -0.5000, -0.4375, -0.5000, -0.5000, -0.4375, -0.5000,  0.5000, -0.4375]
    ]

    texCoords = [
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0]
    ]

    shadingValues = [
        [0.6, 0.6, 0.6, 0.6],
        [0.6, 0.6, 0.6, 0.6],
        [1.0, 1.0, 1.0, 1.0],
        [0.4, 0.4, 0.4, 0.4],
        [0.8, 0.8, 0.8, 0.8],
        [0.8, 0.8, 0.8, 0.8]
    ]

class Torch:
    isTransparent = True
    isBlock = False
    isGlass = False

    colliders = []

    vertexPositions = [
        [ 0.0625, 0.5,  0.5, 0.0625, -0.5,  0.5, 0.0625, -0.5, -0.5, 0.0625, 0.5, -0.5],
        [-0.0625, 0.5, -0.5, -0.0625, -0.5, -0.5, -0.0625, -0.5, 0.5, -0.0625, 0.5, 0.5],
        [ 0.5, 0.125, 0.5, 0.5, 0.125, -0.5, -0.5,  0.125, -0.5, -0.5, 0.125, 0.5],
        [-0.5, -0.5, 0.5, -0.5, -0.5, -0.5, 0.5, -0.5, -0.5, 0.5, -0.5, 0.5],
        [-0.5, 0.5, 0.0625, -0.5, -0.5, 0.0625, 0.5, -0.5, 0.0625, 0.5, 0.5, 0.0625],
        [ 0.5, 0.5, -0.0625, 0.5, -0.5, -0.0625, -0.5, -0.5, -0.0625, -0.5, 0.5, -0.0625]
    ]

    texCoords = [
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0],
        [0.0, 1.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 0.0]
    ]

    shadingValues = [
        [0.6, 0.6, 0.6, 0.6],
        [0.6, 0.6, 0.6, 0.6],
        [1.0, 1.0, 1.0, 1.0],
        [0.4, 0.4, 0.4, 0.4],
        [0.8, 0.8, 0.8, 0.8],
        [0.8, 0.8, 0.8, 0.8]
    ]