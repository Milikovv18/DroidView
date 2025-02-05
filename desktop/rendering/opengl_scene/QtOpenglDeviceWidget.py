from math import sin, cos, tan
from time import time, sleep
import numpy as np
import ctypes
import os

import OpenGL
#OpenGL.ERROR_CHECKING = False
from OpenGL.GL import *

from PyQt6.QtOpenGLWidgets import QOpenGLWidget
from PyQt6.QtOpenGL import QOpenGLFunctions_4_1_Core
from PyQt6.QtGui import QCursor, QKeyEvent
from PyQt6.QtCore import Qt, QPointF, QEvent

from .geometry import Geometry, TileVertex, CubeVertex, NodeWidget
from .animation import AnimationProperty
from .program import OpenGLProgram
from .cursor import CursorLogic
from .picking import Vec3, Ray, ray_triangle_intersect

geometry_tile = Geometry([
    TileVertex([ 1.0,  1.0, 0.0], [1.0, 1.0]),
    TileVertex([ 1.0, -1.0, 0.0], [1.0, 0.0]),
    TileVertex([-1.0, -1.0, 0.0], [0.0, 0.0]),
    TileVertex([-1.0,  1.0, 0.0], [0.0, 1.0])
], [
    [0, 1, 3],
    [1, 2, 3]
])

geometry_tube = Geometry([
    CubeVertex([-1.0,  1.0, 1.0], [-1.0,  0.0,  0.0]),
    CubeVertex([-1.0,  1.0, 0.0], [-1.0,  0.0,  0.0]),
    CubeVertex([-1.0, -1.0, 0.0], [-1.0,  0.0,  0.0]),
    CubeVertex([-1.0, -1.0, 0.0], [-1.0,  0.0,  0.0]),
    CubeVertex([-1.0, -1.0, 1.0], [-1.0,  0.0,  0.0]),
    CubeVertex([-1.0,  1.0, 1.0], [-1.0,  0.0,  0.0]),

    CubeVertex([ 1.0,  1.0, 1.0], [ 1.0,  0.0,  0.0]),
    CubeVertex([ 1.0,  1.0, 0.0], [ 1.0,  0.0,  0.0]),
    CubeVertex([ 1.0, -1.0, 0.0], [ 1.0,  0.0,  0.0]),
    CubeVertex([ 1.0, -1.0, 0.0], [ 1.0,  0.0,  0.0]),
    CubeVertex([ 1.0, -1.0, 1.0], [ 1.0,  0.0,  0.0]),
    CubeVertex([ 1.0,  1.0, 1.0], [ 1.0,  0.0,  0.0]),

    CubeVertex([-1.0, -1.0, 0.0], [ 0.0, -1.0,  0.0]),
    CubeVertex([ 1.0, -1.0, 0.0], [ 0.0, -1.0,  0.0]),
    CubeVertex([ 1.0, -1.0, 1.0], [ 0.0, -1.0,  0.0]),
    CubeVertex([ 1.0, -1.0, 1.0], [ 0.0, -1.0,  0.0]),
    CubeVertex([-1.0, -1.0, 1.0], [ 0.0, -1.0,  0.0]),
    CubeVertex([-1.0, -1.0, 0.0], [ 0.0, -1.0,  0.0]),

    CubeVertex([-1.0,  1.0, 0.0], [ 0.0,  1.0,  0.0]),
    CubeVertex([ 1.0,  1.0, 0.0], [ 0.0,  1.0,  0.0]),
    CubeVertex([ 1.0,  1.0, 1.0], [ 0.0,  1.0,  0.0]),
    CubeVertex([ 1.0,  1.0, 1.0], [ 0.0,  1.0,  0.0]),
    CubeVertex([-1.0,  1.0, 1.0], [ 0.0,  1.0,  0.0]),
    CubeVertex([-1.0,  1.0, 0.0], [ 0.0,  1.0,  0.0])
])


class QtOpenglDeviceWidget(QOpenGLWidget, AnimationProperty):
    screen_scale_factor = 1.0
    texture_id = -1
    texture_pixels = []
    pbo_id = -1
    selection_2d_thickness = 1
    angle = QPointF(0.0, 0.0)
    shift = QPointF(0.0, 0.0)
    zoom_factor = 1.0
    rotation_coef = 2 # How many times faster should the object rotate relative to screen size (1 = from center to window edge until max_angles)
    shift_coef = 3 # More -> faster object shifting
    enabled_3d = True
    max_angles = QPointF(0.0, 0.0) # Absolute values
    max_node_z_distance = 20
    max_node_dilution = 0.2

    test_max_level = 0.0
    test_lowest_y = 0.0

    selection_node = None
    test_nodes = []

    prepare_request = False

    def __init__(self, refresh_period, update_request_callback) -> None:
        super().__init__()
        self.refresh_period = refresh_period
        self.update_request_callback = update_request_callback

    initialized = False
    def initializeGL(self):
        self.create_anim("max_angles", 0.2, AnimationProperty.ease_sqrt)
        self.create_anim("zoom_factor", 0.1, AnimationProperty.ease_linear)
        # For animation "shift" must undergo reassignment, for immediate change only setX and setY are used
        self.create_anim("shift", 0.2, AnimationProperty.ease_sqrt)

        if os.name == 'nt': # To be DPI aware on Windows
            self.screen_scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100

        # Cursor math
        self.cursor_props = CursorLogic(self.get_mouse_pos())

        # Texture shaders
        self.program_texture = OpenGLProgram(os.path.join(os.path.dirname(__file__), "Texture"))
        self.program_selection = OpenGLProgram(os.path.join(os.path.dirname(__file__), "Selection"))
        self.program_picking = OpenGLProgram(os.path.join(os.path.dirname(__file__), "Picking"))
        self.program_floor = OpenGLProgram(os.path.join(os.path.dirname(__file__), "Floor"))

        # Picking result canvas and frame buffer
        self.picking_texture = glGenTextures(1)
        self.picking_vbo = glGenFramebuffers(1)

        # Before window is first resized windowMatrix is identity
        self.aspectMatrix = np.identity(4, np.float32)

        # Perspective view
        self.perProjMat = self.generate_perspective_proj_mat(45.0, 1.0, 1.0, 10.0)
        self.ortProjMat = self.generate_orthographic_proj_mat(-1, 1, 1, -1, 1.0, 10.0)
        self.projMat = self.ortProjMat
        self.create_anim("projMat", 0.2, AnimationProperty.ease_linear)

        self.worldMat = np.array([[1.0, 0.0, 0.0, 0.0], 
                                  [0.0, 1.0, 0.0, 0.0], 
                                  [0.0, 0.0, 1.0, 0.0], 
                                  [0.0, 0.0, -2.0, 1.0]], np.float32)

        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_BLEND)

        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LESS)

        glLineWidth(self.selection_2d_thickness)

        self.setMinimumWidth(100)
        self.setMinimumHeight(100)
        self.startTimer(self.refresh_period)

        self.initialized = True

    anim_start_time = time()
    def paintGL(self):
        glClear(GL_DEPTH_BUFFER_BIT)
        glClearColor(0.85, 0.9, 1.0, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)

        if len(self.test_nodes) == 0:
            return

        self.apply_zoom()

        # Loading new texture
        self.update_texture()

        # Drawing screen texture
        self.draw_node_textures()

        # 2D and 3D renderings use the same program from this point on
        self.program_selection.use()
        geometry_tube.bind()

        self.program_selection.set_mat4("worldMatrix", self.worldMat)
        self.program_selection.set_mat4("aspectMatrix", self.aspectMatrix)
        self.program_selection.set_mat4("projMatrix", self.projMat)
        self.program_selection.set_float("saturation", 1.0)
        self.program_selection.set_vec2("angle", [self.angle.x(), self.angle.y()])

        if self.enabled_3d:
            # Drawing columns
            self.draw_columns()
        else:
            # Drawing available nodes
            self.draw_selection_2d()

        # Floor of lines
        self.draw_floor()
        
    saved_selections = [] # Static
    printed = False
    def mouseCheck(self):
        self.cursor_props.update(self.get_mouse_pos(), self.is_mouse_pressed)
        windowDims = self.screen_scale_factor * self.size()

        # If mouse button is pressed, drag image
        angle_shift = [self.angle.x(), self.angle.y()]
        if self.cursor_props.is_mouse_pressed: # No cursor_props.is_dragging(), because dragging has to be started immediatelly
            if self.ctrl_pressed:
                self.shift.setX(self.shift.x() + self.shift_coef * self.cursor_props.delta().x() / windowDims.width() / self.zoom_factor)
                self.shift.setY(self.shift.y() - self.shift_coef * self.cursor_props.delta().y() / windowDims.height() / self.zoom_factor)
            else:
                angle_shift[0] -= self.rotation_coef * self.cursor_props.delta().x() / windowDims.width()
                angle_shift[1] -= self.rotation_coef * self.cursor_props.delta().y() / windowDims.height()
        # Even if mouse hasnt moved or wasnt pressed, max_angles might be updated e.g. while switching projection matrix
        self.angle.setX(max(min(self.max_angles.x(), angle_shift[0]), -self.max_angles.x()))
        self.angle.setY(max(min(self.max_angles.y(), angle_shift[1]), -self.max_angles.y()))

        # Clearing object shift
        if self.double_ctrl_pressed:
            self.shift = QPointF(0, 0)

        # Disable selection while dragging object
        if self.cursor_props.is_dragging() and self.cursor_props.is_mouse_pressed:
            return

        cur_selections : list[NodeWidget] = []
        cursor_coords = Ray(Vec3(2.0 * self.cursor_props.current_location.x() / windowDims.width() - 1.0,
                                 -(2.0 * self.cursor_props.current_location.y() / windowDims.height() - 1.0), -10.0), Vec3(0.0, 0.0, 1.0))
        mat_comb = self.aspectMatrix.T @ self.projMat.T @ self.worldMat.T @ self.get_rot_matrix(self.angle).T
        for node in self.test_nodes:
            mat_node = mat_comb @ self.get_translation_mat(node, node.level * self.thickness, 1.0).T
            a = mat_node.dot(np.array([ 1.0,  1.0, 0.0, 1.0]))
            a = Vec3(*(a / a[3])[0:3])
            b = mat_node.dot(np.array([ 1.0, -1.0, 0.0, 1.0]))
            b = Vec3(*(b / b[3])[0:3])
            c = mat_node.dot(np.array([-1.0, -1.0, 0.0, 1.0]))
            c = Vec3(*(c / c[3])[0:3])
            d = mat_node.dot(np.array([-1.0,  1.0, 0.0, 1.0]))
            d = Vec3(*(d / d[3])[0:3])
            # Triangle 1
            res = ray_triangle_intersect(cursor_coords, a, b, d)
            # Triangle 2
            res = max(res, ray_triangle_intersect(cursor_coords, b, c, d))
            if res > 0:
                cur_selections.append(node)

        # Remove selection
        cur_selections.sort(key=lambda x: x.level, reverse=True)
        for node in self.test_nodes:
            if len(cur_selections) == 0 or node != cur_selections[0]:
                node.set_mouse_inside(False)

        # If there is something to select, saving selection array
        if len(cur_selections) > 0:
            if self.selection_node == None:
                self.saved_selections = cur_selections
                cur_selections[0].set_mouse_inside(True)

        # Selection node
        if self.cursor_props.been_released() and not self.cursor_props.is_dragging(): # Released inside epsilon
            if len(self.saved_selections) > 0 and self.saved_selections == cur_selections and self.cursor_props.static_clicks_counter < len(cur_selections):
                self.update_request_callback(self.saved_selections[self.cursor_props.static_clicks_counter].id)
            else:
                self.unselect_node()
                    
    def select_node(self, node : NodeWidget):
        if self.selection_node is not None:
            self.unselect_node()

        self.selection_node = node
        # Mouse is still inside, but stretchy animation should be disabled for selected nodes
        self.selection_node.set_mouse_inside(False)
        # Making all higher-level nodes invisible
        for node in self.test_nodes:
            if node.level > self.selection_node.level:
                node.visibility = 0.0

    def unselect_node(self):
        self.selection_node = None
        # Making all nodes visible again
        for node in self.test_nodes:
            node.visibility = 1.0

    def draw_node_textures(self):
        self.program_texture.use()
        geometry_tile.bind()

        self.program_texture.set_mat4("worldMatrix", self.worldMat)
        self.program_texture.set_mat4("aspectMatrix", self.aspectMatrix)
        self.program_texture.set_mat4("projMatrix", self.projMat)
        self.program_texture.set_vec2("angle", [self.angle.x(), self.angle.y()])
        self.program_texture.set_float("textureAmend", 1.0 / self.texture_ratio)

        for node in self.test_nodes:
            if node.visibility == 0.0:
                continue
            if self.enabled_3d:
                node.dilution = self.max_node_dilution if self.is_node_should_be_highlighted(node) else 0.0
                #self.program_texture.set_float("dilutionFactor", node.dilution)
                glUniform1f(self.program_texture.uniforms["dilutionFactor"], node.dilution)
            else:
                glUniform1f(self.program_texture.uniforms["dilutionFactor"], 0.0)
                #self.program_texture.set_float("dilutionFactor", 0.0)
            glUniform1f(self.program_texture.uniforms["visibility"], node.visibility)
            #self.program_texture.set_float("visibility", node.visibility)
            glUniformMatrix4fv(self.program_texture.uniforms["translationMatrix"], 1, GL_FALSE, self.get_translation_mat(node, self.get_node_texture_offset(node), 1.0))
            #self.program_texture.set_mat4("translationMatrix", self.get_translation_mat(node, self.get_node_texture_offset(node), 1.0))
            glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, None)

    def draw_columns(self):
        geometry_tube.bind()

        for node in self.test_nodes:
            if node.visibility == 0.0:
                continue

            # Dilution has already been set in draw_node_textures
            glUniform3f(self.program_selection.uniforms["color"], *(3 * [0.7 * (1.0 - self.max_node_dilution * node.dilution)]))
            #self.program_selection.set_vec3("color", 3 * [0.7 * (1.0 - self.max_node_dilution * node.dilution)])
            glUniformMatrix4fv(self.program_selection.uniforms["translationMatrix"], 1, GL_FALSE, self.get_translation_mat(node, (node.level - 1) * self.thickness, self.get_node_column_scale(node)))
            #self.program_selection.set_mat4("translationMatrix", self.get_translation_mat(node, (node.level - 1) * self.thickness, self.get_node_column_scale(node)))
            glDrawArrays(GL_TRIANGLES, 0, 24)

    def draw_selection_2d(self):
        geometry_tile.bind()

        # Drawing current selection node
        if self.selection_node != None:
            self.program_selection.set_vec3("color", [1.0, 0.0, 0.0])
            self.program_selection.set_float("saturation", 1.0)
            self.program_selection.set_mat4("translationMatrix", self.get_translation_mat(self.selection_node, 1.0, 1.0))
            glDrawArrays(GL_LINE_LOOP, 0, 4)

        self.program_selection.set_vec3("color", [1.0, 1.0, 0.0])
        for node in self.test_nodes:
            if node.visibility == 0.0 or node.activation == 0.0:
                continue
            self.program_selection.set_float("saturation", node.activation)
            # Always on top of every node
            self.program_selection.set_mat4("translationMatrix", self.get_translation_mat(node, 1.0, 1.0))
            glDrawArrays(GL_LINE_LOOP, 0, 4)

    def draw_floor(self):
        self.program_floor.use()
        geometry_tile.bind()

        self.program_floor.set_mat4("worldMatrix", self.worldMat)
        self.program_floor.set_mat4("aspectMatrix", self.aspectMatrix)
        self.program_floor.set_mat4("projMatrix", self.projMat)
        self.program_floor.set_float("lowestNode", self.test_lowest_y)
        self.program_floor.set_vec2("angle", [self.angle.x(), self.angle.y()])

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)

    def prepare_for_device(self, resolution):
        self.tex_resolution = resolution
        self.prepare_texture()

    def update_content(self, image, nodes, meta):
        self.test_nodes = nodes
        self.texture_pixels = image

        max_level, self.test_lowest_y = meta[0], meta[1]
        self.test_max_level = max(max_level, self.max_node_z_distance)
        self.thickness = 1 / self.test_max_level
        self.selection_3d_thickness = 0.5 / self.test_max_level

    def prepare_texture(self):
        bit_depth = 3
        pixels = np.empty(self.tex_resolution[0] * self.tex_resolution[1] * bit_depth)
        
        # create pixel buffer object for transferring textures
        self.pbo_id = glGenBuffers(1)
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER, self.pbo_id)
        glBufferData(GL_PIXEL_UNPACK_BUFFER, self.tex_resolution[0] * self.tex_resolution[1] * bit_depth, None, GL_STREAM_DRAW)
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)

        # map and modify pixel buffer
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER, self.pbo_id)
        #glFuncs = self.context().currentContext().extraFunctions()
        pbo_addr = glMapBuffer(GL_PIXEL_UNPACK_BUFFER, GL_WRITE_ONLY)
        # write to PBO using numpy interface
        pbo_ptr = ctypes.cast(pbo_addr, ctypes.POINTER(ctypes.c_uint8))
        self.pbo_np = np.ctypeslib.as_array(pbo_ptr, shape=(self.tex_resolution[1] * self.tex_resolution[0] * bit_depth,))
        self.pbo_np[:] = pixels
        glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)

        # create texture from pixel buffer object
        self.texture_id = glGenTextures(1)
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER, self.pbo_id)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_BASE_LEVEL, 0)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAX_LEVEL, 0)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, self.tex_resolution[0], self.tex_resolution[1], 0, GL_RGB, GL_UNSIGNED_BYTE, None)
        glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)

        # Secondary stuff
        self.texture_ratio = self.tex_resolution[0] / self.tex_resolution[1]

    def update_texture(self):
        if self.texture_pixels is not None:
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, self.pbo_id)
            glMapBuffer(GL_PIXEL_UNPACK_BUFFER, GL_WRITE_ONLY)
            self.pbo_np[:] = self.texture_pixels
            glUnmapBuffer(GL_PIXEL_UNPACK_BUFFER)
            # Not necessary to bind, this is the only texture
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB8, self.tex_resolution[0], self.tex_resolution[1], 0, GL_RGB, GL_UNSIGNED_BYTE, None)
            glBindBuffer(GL_PIXEL_UNPACK_BUFFER, 0)


    def apply_zoom(self):
        if self.double_ctrl_pressed:
            self.zoom_factor = 1.0
        self.worldMat[0][0] = self.zoom_factor
        self.worldMat[1][1] = self.zoom_factor
        self.worldMat[3][0] = self.zoom_factor * self.shift.x()
        self.worldMat[3][1] = self.zoom_factor * self.shift.y()

    def get_mouse_pos(self):
        return self.screen_scale_factor * self.mapFromGlobal(QCursor.pos())
    
    def generate_perspective_proj_mat(self, fov, aspect, near, far):
        angle = (fov / 180.0) * np.pi
        f = 1.0 / tan(angle * 0.5)
        return np.array([[f / aspect, 0.0, 0.0,                             0.0],
                        [0.0,         f,   0.0,                             0.0],
                        [0.0,         0.0, (far + near) / (near - far),    (2.0 * far*near) / (near - far)],
                        [0.0,         0.0, -1.0, 1.0]], np.float32)
    
    def generate_orthographic_proj_mat(self, left, right, top, bottom, near, far):
        return np.array([[2 / (right - left),              0.0,                              0.0,                          0.0],
                        [0.0,                              2 / (top - bottom),               0.0,                          0.0],
                        [0.0,                              0.0,                              -2 / (far - near),            0.0],
                        [-(right + left) / (right - left), -(top + bottom) / (top - bottom), -(far + near) / (far - near), 1.0]], np.float32)
    
    # Phone-screen-ratio-aware node translation matrix
    def get_translation_mat(self, node : NodeWidget, z_offset, z_scale):
        mat = node.get_translation_mat(z_offset, z_scale)
        mat[0][0] *= self.texture_ratio
        mat[3][0] *= self.texture_ratio
        return mat
    
    def get_rot_matrix(self, angle):
        return np.array([[cos(angle.x()),  sin(angle.y()) * sin(angle.x()), sin(angle.x()) * cos(angle.y()), 0],
                       [0,             cos(angle.y()),               -sin(angle.y()),                0],
                       [-sin(angle.x()), sin(angle.y()) * cos(angle.x()), cos(angle.y()) * cos(angle.x()), 0],
                       [0,             0,                           0,                           1]])
    
    def is_node_should_be_highlighted(self, node):
        return (self.selection_node == None and node.activation > 0) or (self.selection_node != None and not node == self.selection_node)
    
    def get_node_texture_offset(self, node):
        return (node.level + node.visibility - 1) * self.thickness + self.selection_3d_thickness * node.activation
    
    def get_node_column_scale(self, node):
        return node.visibility * self.thickness + self.selection_3d_thickness * node.activation


    # EVENTS (not much logic here) #

    def resizeGL(self, width, height):
        if self.texture_id == -1:
            return # Not yet initialized
        glBindTexture(GL_TEXTURE_2D, self.texture_id)
        ratio = height / width
        self.aspectMatrix = np.array([[ratio, 0.0, 0.0, 0.0], 
                                      [0.0, 1.0, 0.0, 0.0], 
                                      [0.0, 0.0, 1.0, 0.0], 
                                      [0.0, 0.0, 0.0, 1.0]], np.float32)

    is_mouse_pressed = False
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_mouse_pressed = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_mouse_pressed = False

    def wheelEvent(self, event):
        # Zoom
        if self.animatables["zoom_factor"].finished:
            delta = event.angleDelta().y() / 120
            delta *= self.zoom_factor
            if delta < 0:
                delta /= 2
            self.zoom_factor = max(self.zoom_factor + delta, 0.1)

    ctrl_pressed = False
    double_ctrl_pressed = False
    last_ctrl_press = 0
    def keyPressEvent(self, event: QKeyEvent):
        # Zoom selection
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = True
            cur_time = time()
            # Double press
            if cur_time - self.last_ctrl_press < 0.2:
                self.double_ctrl_pressed = True
            self.last_ctrl_press = cur_time

        # Projection switch
        if event.key() == Qt.Key.Key_Shift:
            if self.enabled_3d:
                self.projMat = self.ortProjMat
                self.max_angles = QPointF(0.0, 0.0)
                self.enabled_3d = False
            else:
                self.projMat = self.perProjMat
                self.max_angles = QPointF(1.0, 1.0)
                self.enabled_3d = True

    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        # Zoom selection
        if event.key() == Qt.Key.Key_Control:
            self.ctrl_pressed = False
            self.double_ctrl_pressed = False
        return super().keyReleaseEvent(event)

        
    def timerEvent(self, _):
        if not self.initialized:
            return
        
        # Update nodes selection state
        self.mouseCheck()

        # Update animations (synchronization mechanism)
        AnimationProperty.update(self)
        for node in self.test_nodes:
            node.update()

        # Update frame
        self.update()
