from PyQt6.QtCore import QPointF

from rendering.opengl_scene.geometry import NodeWidget


class VisualizationPackageProcessor:
    max_level : int = 0
    lowest_y : float = 0

    def set_dims(self, dims):
        self.width = dims[0]
        self.height = dims[1]

    def convert(self, id, node, level, _):
        cur_node = NodeWidget(
            id,
            QPointF(+2 * node["x"] / self.width - 1, -2 * node["y"] / self.height + 1),
            level,
            QPointF(abs(node["w"]) / self.width, abs(node["h"]) / self.height)
        )

        if level > self.max_level:
            self.max_level = level
        lowest_point = cur_node.center.y() - cur_node.scale.y()
        if lowest_point < self.lowest_y:
            self.lowest_y = lowest_point

        return cur_node

    def get_stats(self):
        return self.max_level, self.lowest_y
