import math


class Vec3:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def sub(self, v):
        return Vec3(self.x - v.x,
                    self.y - v.y,
                    self.z - v.z)

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z

    def cross(self, v):
        return Vec3(self.y * v.z - self.z * v.y,
                    self.z * v.x - self.x * v.z,
                    self.x * v.y - self.y * v.x)

    def length(self):
        return math.sqrt(self.x * self.x +
                         self.y * self.y +
                         self.z * self.z)

    def normalize(self):
        l = self.length()
        return Vec3(self.x / l, self.y / l, self.z / l)


class Ray:
    def __init__(self, orig=None, direction=None):
        self.orig = orig
        self.direction = direction


def ray_triangle_intersect(r, v0, v1, v2):
    v0v1 = v1.sub(v0)
    v0v2 = v2.sub(v0)
    pvec = r.direction.cross(v0v2)

    det = v0v1.dot(pvec)

    if det < 0.000001:
        return float('-inf')

    invDet = 1.0 / det
    tvec = r.orig.sub(v0)
    u = tvec.dot(pvec) * invDet

    if u < 0 or u > 1:
        return float('-inf')

    qvec = tvec.cross(v0v1)
    v = r.direction.dot(qvec) * invDet

    if v < 0 or u + v > 1:
        return float('-inf')

    return v0v2.dot(qvec) * invDet