from functools import lru_cache as cache

import glm, ctypes

east = glm.vec3(1, 0, 0)
west = glm.vec3(-1, 0, 0)
up = glm.vec3(0, 1, 0)
down = glm.vec3(0, -1, 0)
south = glm.vec3(0, 0, 1)
north = glm.vec3(0, 0, -1)

directions = [
    east, west, up, down, south, north
]

@cache(maxsize = None)
def smooth(a, b, c, d):
    if not a or not b or not c or not d:
        l = (a, *(i for i in (b, c, d) if i))
        minVal = min(l)
        a = max(a, minVal)
        b = max(b, minVal)
        c = max(c, minVal)
        d = max(d, minVal)
                
    return (a + b + c + d) / 4

@cache(maxsize = None)
def ao(s1, s2, c):
    if s1 and s2:
        return 0.25

    return 1 - (s1 + s2 + c) / 4