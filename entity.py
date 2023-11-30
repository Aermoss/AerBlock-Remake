import math, glm, moss
import collider

flyingAccel = (0.0, 0.0, 0.0)
gravityAccel = (0.0, -32.0, 0.0)

friction = (20, 20, 20)

dragFly = (5.0, 5.0, 5.0)
dragJump = (1.8, 0.0, 1.8)
dragFall = (1.8, 0.4, 1.8)

class Entity:
    def __init__(self, world, width, height):
        self.world = world
        self.position = (0.0, 0.0, 0.0)
        self.velocity = (0.0, 0.0, 0.0)
        self.accel = (0.0, 0.0, 0.0)
        self.width, self.height = width, height
        self.collider = collider.Collider()
        self.grounded = False
        self.flying = False
        self.lastNormal = (0, 0, 0)

    def updateCollider(self):
        self.collider.x1 = self.position[0] - self.width / 2
        self.collider.x2 = self.position[0] + self.width / 2
        self.collider.y1 = self.position[1]
        self.collider.y2 = self.position[1] + self.height
        self.collider.z1 = self.position[2] - self.width / 2
        self.collider.z2 = self.position[2] + self.width / 2

    @property
    def friction(self):
        if self.flying:
            return dragFly

        elif self.grounded:
            return friction

        elif self.velocity[0] > 0:
            return dragJump

        return dragFall

    def update(self, deltaTime):
        self.velocity = [v + a * f * deltaTime for v, a, f in zip(self.velocity, self.accel, self.friction)]
        self.accel = [0, 0, 0]

        self.updateCollider()
        self.grounded = False

        for _ in range(3):
            adjustedVelocity = [v * deltaTime for v in self.velocity]

            stepX = 1 if adjustedVelocity[0] > 0 else -1
            stepY = 1 if adjustedVelocity[1] > 0 else -1
            stepZ = 1 if adjustedVelocity[2] > 0 else -1

            stepsXZ = int(self.width / 2)
            stepsY = int(self.height)

            x, y, z = map(int, self.position)
            cx, cy, cz = [int(x + v) for x, v in zip(self.position, adjustedVelocity)]

            potentialCollisions = []

            for i in range(x - stepX * (stepsXZ + 1), cx + stepX * (stepsXZ + 2), stepX):
                for j in range(y - stepY * (stepsY + 2), cy + stepY * (stepsY + 3), stepY):
                    for k in range(z - stepZ * (stepsXZ + 1), cz + stepZ * (stepsXZ + 2), stepZ):
                        num = self.world.getBlockNumber(glm.vec3(i, j, k))

                        if not num:
                            continue

                        for _collider in self.world.blockTypes[num].colliders:
                            entryTime, normal = self.collider.collide(_collider + (i, j, k), adjustedVelocity)

                            if normal is None:
                                continue

                            potentialCollisions.append((entryTime, normal))

            if not potentialCollisions:
                break

            entryTime, normal = min(potentialCollisions, key = lambda x: x[0])
            entryTime -= 0.001

            if normal[0]:
                self.velocity[0] = 0
                self.position[0] += adjustedVelocity[0] * entryTime
            
            if normal[1]:
                self.velocity[1] = 0
                self.position[1] += adjustedVelocity[1] * entryTime

            if normal[2]:
                self.velocity[2] = 0
                self.position[2] += adjustedVelocity[2] * entryTime

            if normal[1] == 1:
                self.grounded = True

            self.lastNormal = normal

        self.position = [x + v * deltaTime for x, v in zip(self.position, self.velocity)]
        gravity = flyingAccel if self.flying else gravityAccel
        self.velocity = [v + a * deltaTime for v, a in zip(self.velocity, gravity)]
        self.velocity = [v - min(v * f * deltaTime, v, key = abs) for v, f in zip(self.velocity, self.friction)]
        self.updateCollider()