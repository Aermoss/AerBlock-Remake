import math, glm, moss, time
import entity, _chunk

WALKING_SPEED = 4.317
SPRINTING_SPEED = 7

class Frustum:
    left = glm.vec4(1.0)
    right = glm.vec4(1.0)
    top = glm.vec4(1.0)
    bottom = glm.vec4(1.0)
    near = glm.vec4(1.0)
    far = glm.vec4(1.0)

def normalize(plane):
    return plane / glm.length(plane.xyz)

class Player(entity.Entity):
    def __init__(self, world, shader, fov = 90, sensitivity = 100.0, position = glm.vec3(0.0, 0.0, 1.0), front = glm.vec3(0.0, 0.0, -1.0), near = 0.01, far = 1000.0):
        super().__init__(world, width = 0.6, height = 1.8)
        self.world, self.shader = world, shader
        self.window = moss.context.getCurrentWindow()
        self.sensitivity, self.front = sensitivity, front
        self.fov, self.smoothFov, self.position = fov, fov, position.to_list()
        self.near, self.far = near, far
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.yaw, self.pitch = 0.0, 0.0
        self.eyelevel = self.height - 0.2
        self.targetSpeed = WALKING_SPEED
        self.speed = self.targetSpeed
        self.jumpHeight = 1.25
        self.lastPress = {moss.KEY_SPACE: 0, moss.KEY_W: 0}
        self.lastFirstPress = {moss.KEY_SPACE: 0, moss.KEY_W: 0}
        self.lastHoldTime = {moss.KEY_SPACE: 0, moss.KEY_W: 0}
        self.state = {moss.KEY_SPACE: False, moss.KEY_W: False}

    def proccessInputs(self):
        if self.window.width == 0: return

        self.input = [
            (1 if self.window.input.getKey(moss.KEY_D) else 0) + (-1 if self.window.input.getKey(moss.KEY_A) else 0),
            (1 if self.window.input.getKey(moss.KEY_SPACE) else 0) + (-1 if self.window.input.getKey(moss.KEY_LEFT_SHIFT) else 0),
            (1 if self.window.input.getKey(moss.KEY_W) else 0) + (-1 if self.window.input.getKey(moss.KEY_S) else 0)
        ]

        for key in [moss.KEY_SPACE, moss.KEY_W]:
            if self.window.input.getKey(key):
                if self.state[key] and self.lastPress[key] + 0.2 > time.time() and self.lastHoldTime[key] < 0.2:
                    self.lastHoldTime[key], self.lastFirstPress[key], self.lastPress[key] = 0, 0, 0
                    if key == moss.KEY_SPACE: self.flying = not self.flying
                    if key == moss.KEY_W: self.targetSpeed = SPRINTING_SPEED

                else:
                    if self.state[key] == True:
                        self.lastFirstPress[key] = time.time()

                    self.lastPress[key] = time.time()

                self.state[key] = False

            else:
                if self.state[key] == False:
                    self.lastHoldTime[key] = self.lastPress[key] - self.lastFirstPress[key]

                self.state[key] = True

        speed = glm.sqrt(glm.pow(self.velocity[0], 2) + glm.pow(self.velocity[2], 2))

        if ((self.window.input.getKey(moss.KEY_LEFT_CONTROL) and speed > 2.0) or self.targetSpeed == SPRINTING_SPEED) \
            and self.window.input.getKey(moss.KEY_W) and not self.window.input.getKey(moss.KEY_S):
            if (self.lastNormal[0] or self.lastNormal[2]) and (speed < 2.0): self.targetSpeed = WALKING_SPEED
            else: self.targetSpeed = SPRINTING_SPEED

        else:
            self.targetSpeed = WALKING_SPEED

        if self.window.deltaTime * 20 > 1: self.speed = self.targetSpeed
        else: self.speed += (self.targetSpeed - self.speed) * self.window.deltaTime * 20

        multiplier = self.speed * (2 if self.flying else 1)

        if self.flying and self.input[1]:
            self.accel[1] = self.input[1] * multiplier

        if self.input[0] or self.input[2]:
            angle = math.radians(self.yaw) - math.atan2(self.input[2], self.input[0]) + math.tau / 4
            self.accel[0] = math.cos(angle) * multiplier
            self.accel[2] = math.sin(angle) * multiplier

        if not self.flying and self.input[1] > 0:
            self.jump()

        if self.grounded:
            self.flying = False
            
        super().update(self.window.deltaTime)

        self.window.input.setCursorVisible(False)
        x, y = self.window.input.getCursorPosition()

        x_offset = self.sensitivity * (x - int(self.window.width / 2)) / self.window.width
        y_offset = self.sensitivity * (y - int(self.window.height / 2)) / self.window.height

        self.yaw += x_offset
        self.pitch -= y_offset

        if self.pitch >= 89.9:
            self.pitch = 89.9

        if self.pitch <= -89.9:
            self.pitch = -89.9

        self.window.input.setCursorPosition(self.window.width / 2, self.window.height / 2)

    def checkInFrustum(self, chunkPosition):
        planes = (Frustum.left, Frustum.right, Frustum.bottom, Frustum.top, Frustum.near, Frustum.far)
        center = glm.vec3(chunkPosition * glm.vec3(_chunk.chunkSize.x,  0, _chunk.chunkSize.z) + _chunk.chunkSize / 2)
        result = 2

        for plane in planes:
            _in, _out = 0, 0
            normal = plane.xyz
            w = plane.w

            if glm.dot(normal, center + glm.vec3(_chunk.chunkSize.x / 2, _chunk.chunkSize.y / 2, _chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1

            if glm.dot(normal, center + glm.vec3(-_chunk.chunkSize.x / 2, _chunk.chunkSize.y / 2, _chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1

            if glm.dot(normal, center + glm.vec3(_chunk.chunkSize.x / 2, _chunk.chunkSize.y / 2, -_chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1

            if glm.dot(normal, center + glm.vec3(-_chunk.chunkSize.x / 2, _chunk.chunkSize.y / 2, -_chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1

            if glm.dot(normal, center + glm.vec3(_chunk.chunkSize.x / 2, -_chunk.chunkSize.y / 2, _chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1

            if glm.dot(normal, center + glm.vec3(-_chunk.chunkSize.x / 2, -_chunk.chunkSize.y / 2, _chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1

            if glm.dot(normal, center + glm.vec3(_chunk.chunkSize.x / 2, -_chunk.chunkSize.y / 2, -_chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1

            if glm.dot(normal, center + glm.vec3(-_chunk.chunkSize.x / 2, -_chunk.chunkSize.y / 2, -_chunk.chunkSize.z / 2)) + w < 0: _out += 1
            else: _in += 1
            
            if not _in: return 0
            elif _out: result = 1

        return result
    
    def updateFrustum(self, mat):
        mat = glm.transpose(mat)

        for i in range(4):
            Frustum.left[i] = mat[3][i] + mat[0][i]
            Frustum.right[i] = mat[3][i] - mat[0][i]
            Frustum.bottom[i] = mat[3][i] + mat[1][i]
            Frustum.top[i] = mat[3][i] - mat[1][i]
            Frustum.near[i] = mat[3][i] + mat[2][i]
            Frustum.far[i] = mat[3][i] - mat[2][i]

        Frustum.left = normalize(Frustum.left)
        Frustum.right = normalize(Frustum.right)
        Frustum.bottom = normalize(Frustum.bottom)
        Frustum.top = normalize(Frustum.top)
        Frustum.near = normalize(Frustum.near)
        Frustum.far = normalize(Frustum.far)

    def teleport(self, position):
        self.position = position
        self.velocity = glm.vec3(0.0, 0.0, 0.0)

    def jump(self, height = None):
        if not self.grounded:
            return

        if height is None:
            height = self.jumpHeight

        self.velocity[1] = math.sqrt(2 * height * -entity.gravityAccel[1])

    def updateMatrices(self):
        if self.window.width == 0: return

        self.front = glm.normalize(glm.vec3(
            math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch)),
            math.sin(glm.radians(self.pitch)),
            math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        ))

        self.smoothFov = glm.lerp(self.smoothFov, self.fov + (15 if self.flying else 0) + (25 if self.targetSpeed == SPRINTING_SPEED else 0), 0.01)
        proj = glm.perspective(glm.radians(self.smoothFov), self.window.width / self.window.height, self.near, self.far)
        position = glm.vec3(*self.position) + glm.vec3(0.0, self.eyelevel, 0.0)
        view = glm.lookAt(position, position + self.front, self.up)
        self.shader.use()
        self.shader.setUniform3fv("cameraPosition", glm.value_ptr(position))
        self.shader.setUniformMatrix4fv("proj", glm.value_ptr(proj))
        self.shader.setUniformMatrix4fv("view", glm.value_ptr(view))
        self.shader.unuse()

        self.updateFrustum(proj * view)