import numpy as np
import itertools
import random

from PyQt6.QtCore import QPointF
from OpenGL.arrays.vbo import VBO
from OpenGL.GL import *

from .animation import AnimationProperty


class BaseVertex:
    def __init__(self, coords : list, *extras) -> None:
        self.coords = coords
        self.extras = extras

    def flatten(self):
        return self.coords + list(itertools.chain(*self.extras))

    def get_shape(self):
        return [len(self.coords)] + [len(x) for x in self.extras]

class TileVertex(BaseVertex):
    def __init__(self, coords : list, tex_coords : list) -> None:
        super(TileVertex, self).__init__(coords, tex_coords)

class CubeVertex(BaseVertex):
    def __init__(self, coords : list, normals : list) -> None:
        super(CubeVertex, self).__init__(coords, normals)

class Geometry:
    def __init__(self, vertices : list[BaseVertex], indices : list = None) -> None:
        self.vertex_meta = vertices[0]
        vertices = [v.flatten() for v in vertices]
        self.vertices = VBO(np.array(vertices, dtype='f'))
        self.indices = None
        if indices != None:
            self.indices = VBO(np.array(indices, dtype=np.int32), target=GL_ELEMENT_ARRAY_BUFFER)

    def bind(self):
        self.vertices.bind() # 1 gl
        if self.indices != None:
            self.indices.bind() # 1 gl

        shape = self.vertex_meta.get_shape()
        for i in range(len(shape)):
            glEnableVertexAttribArray(i) # 1 gl
            glVertexAttribPointer(i, shape[i], GL_FLOAT, False, 4 * sum(shape), ctypes.c_void_p(4 * sum(shape[:i]))) # 1 gl



class InteractiveWidget:
    def __init__(self) -> None:
        pass

    mouse_inside = False
    def set_mouse_inside(self, is_inside):
        if self.mouse_inside == False and is_inside == True:
            self.mouse_in()
        if self.mouse_inside == True and is_inside == False:
            self.mouse_out()
        self.mouse_inside = is_inside

    # Mouse starts hovering over widget
    def mouse_in(self):
        pass

    # Mouse leaves widget bbox
    def mouse_out(self):
        pass

    def mouse_clicked(self):
        pass


class NodeWidget(InteractiveWidget, AnimationProperty):
    id : int
    translation_mat = np.identity(4)
    
    def __init__(self, id, center : QPointF, level : float, scale : QPointF) -> None:
        AnimationProperty.__init__(self)
        # Constants
        self.id = id
        self.center = center
        self.level = level
        self.scale = scale

        # Very small value to avoid texture overlapping
        self.jitter = 0.002 * random.random() - 0.001

        # For animations only
        self.activation = 0.0
        self.create_anim("activation", 0.2, AnimationProperty.ease_sqrt)
        self.dilution = 0.0
        self.visibility = 1.0
        self.create_anim("visibility", 0.2, AnimationProperty.ease_sqrt)

    def mouse_in(self):
        self.activation = 1.0

    def mouse_out(self):
        self.activation = 0.0

    def get_translation_mat(self, z_offset, z_scale):
        self.translation_mat[0][0] = self.scale.x()
        self.translation_mat[1][1] = self.scale.y()
        self.translation_mat[2][2] = z_scale
        self.translation_mat[3][0] = self.center.x()
        self.translation_mat[3][1] = self.center.y()
        self.translation_mat[3][2] = z_offset + self.jitter
        return self.translation_mat
