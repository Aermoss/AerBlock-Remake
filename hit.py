import math

hitRange = 5

class HitRay:
    def __init__(self, world, rotation, startingPosition):
        self.world = world

        self.vector = (
            math.cos(rotation[0]) * math.cos(rotation[1]),
            math.sin(rotation[1]),
            math.sin(rotation[0]) * math.cos(rotation[1])
        )

        self.position = list(startingPosition)
        self.block = tuple(map(lambda x: int(round(x)), self.position))
        self.distance = 0

    def check(self, hitCallback, distance, currentBlock, nextBlock):
        if self.world.getBlockNumber(nextBlock):
            hitCallback(currentBlock, nextBlock)
            return True
        
        else:
            self.position = list(map(lambda x: self.position[x] + self.vector[x] * distance, range(3)))
            self.block = nextBlock
            self.distance += distance
            return False

    def step(self, hitCallback):
        bx, by, bz = self.block
        localPosition = list(map(lambda x: self.position[x] - self.block[x], range(3)))

        sign = [1, 1, 1]
        absoluteVector = list(self.vector)

        for component, element in enumerate(self.vector):
            sign[component] = 2 * (element >= 0) - 1
            absoluteVector[component] *= sign[component]
            localPosition[component] *= sign[component]
        
        lx, ly, lz = localPosition
        vx, vy, vz = absoluteVector

        if vx:
            x = 0.5
            y = (0.5 - lx) / vx * vy + ly
            z = (0.5 - lx) / vx * vz + lz

            if y >= -0.5 and y <= 0.5 and z >= -0.5 and z <= 0.5:
                distance = math.sqrt((x - lx) ** 2 + (y - ly) ** 2 + (z - lz) ** 2)
                return self.check(hitCallback, distance, (bx, by, bz), (bx + sign[0], by, bz))

        if vy:
            x = (0.5 - ly) / vy * vx + lx
            y = 0.5
            z = (0.5 - ly) / vy * vz + lz

            if x >= -0.5 and x <= 0.5 and z >= -0.5 and z <= 0.5:
                distance = math.sqrt((x - lx) ** 2 + (y - ly) ** 2 + (z - lz) ** 2)
                return self.check(hitCallback, distance, (bx, by, bz), (bx, by + sign[1], bz))
        
        if vz:
            x = (0.5 - lz) / vz * vx + lx
            y = (0.5 - lz) / vz * vy + ly
            z = 0.5

            if x >= -0.5 and x <= 0.5 and y >= -0.5 and y <= 0.5:
                distance = math.sqrt((x - lx) ** 2 + (y - ly) ** 2 + (z - lz) ** 2)
                return self.check(hitCallback, distance, (bx, by, bz), (bx, by, bz + sign[2]))