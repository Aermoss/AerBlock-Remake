import math

class Collider:
    def __init__(self, pos1 = (None,) * 3, pos2 = (None,) * 3):
        self.x1, self.y1, self.z1 = pos1
        self.x2, self.y2, self.z2 = pos2
    
    def __add__(self, pos):
        x, y, z = pos

        return Collider(
            (self.x1 + x, self.y1 + y, self.z1 + z),
            (self.x2 + x, self.y2 + y, self.z2 + z)
        )
    
    def __and__(self, collider):
        x = min(self.x2, collider.x2) - max(self.x1, collider.x1)
        y = min(self.y2, collider.y2) - max(self.y1, collider.y1)
        z = min(self.z2, collider.z2) - max(self.z1, collider.z1)
        return x > 0 and y > 0 and z > 0
    
    def collide(self, collider, velocity):
        noCollision = 1, None
        vx, vy, vz = velocity
        
        time = lambda x, y: x / y if y else float("-" * (x > 0) + "inf")

        xEntry = time(collider.x1 - self.x2 if vx > 0 else collider.x2 - self.x1, vx)
        xExit = time(collider.x2 - self.x1 if vx > 0 else collider.x1 - self.x2, vx)
        yEntry = time(collider.y1 - self.y2 if vy > 0 else collider.y2 - self.y1, vy)
        yExit = time(collider.y2 - self.y1 if vy > 0 else collider.y1 - self.y2, vy)
        zEntry = time(collider.z1 - self.z2 if vz > 0 else collider.z2 - self.z1, vz)
        zExit = time(collider.z2 - self.z1 if vz > 0 else collider.z1 - self.z2, vz)

        if xEntry < 0 and yEntry < 0 and zEntry < 0:
            return noCollision

        if xEntry > 1 or yEntry > 1 or zEntry > 1:
            return noCollision

        entry = max(xEntry, yEntry, zEntry)
        exit_ = min(xExit, yExit, zExit)

        if entry > exit_:
            return noCollision
        
        nx = (0, -1 if vx > 0 else 1)[entry == xEntry]
        ny = (0, -1 if vy > 0 else 1)[entry == yEntry]
        nz = (0, -1 if vz > 0 else 1)[entry == zEntry]
        return entry, (nx, ny, nz)