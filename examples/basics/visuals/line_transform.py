# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Demonstration of LineVisual with arbitrary transforms.

Several LineVisuals are displayed that all have the same vertex position
information, but different transformations.
"""

import numpy as np
import vispy.app
from vispy import gloo
from vispy.scene import visuals
from vispy.scene.transforms import (STTransform, LogTransform,
                                    AffineTransform, PolarTransform)

import vispy.util
vispy.util.use_log_level('debug')

# vertex positions of data to draw
N = 200
pos = np.zeros((N, 3), dtype=np.float32)
pos[:, 0] = np.linspace(-0.9, 0.9, N)
pos[:, 1] = np.random.normal(size=N, scale=0.2).astype(np.float32)

# One array of colors
color = np.ones((N, 4), dtype=np.float32)
color[:, 0] = np.linspace(0, 1, N)
color[:, 1] = color[::-1, 0]


class Canvas(vispy.app.Canvas):
    def __init__(self):

        # Define several LineVisuals that use the same position data
        # but have different colors and transformations
        colors = [color, (1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1),
                  (1, 1, 0, 1), (1, 1, 1, 1)]

        self.lines = [visuals.Line(pos=pos, color=colors[i]) for i in range(6)]

        self.lines[1].transform = STTransform(scale=(1, 0.1, 1))

        self.lines[2].transform = (STTransform(translate=(0.5, 0.6, 0)) *
                                   STTransform(scale=(0.3, 0.5, 1)))

        self.lines[3].transform = (STTransform(translate=(0, -0.7, 0),
                                               scale=(1, 0.5)) *
                                   LogTransform(base=(10, 0, 0)) *
                                   STTransform(translate=(1, 0, 0)))

        self.lines[4].transform = AffineTransform()
        self.lines[4].transform.rotate(45, (0, 0, 1))
        self.lines[4].transform.scale((0.3, 0.3, 1))
        self.lines[4].transform.translate((0.7, -0.7, 0))

        self.lines[5].transform = (STTransform(translate=(-0.5, 0.7, 0)) *
                                   PolarTransform() *
                                   LogTransform(base=(2, 0, 0)) *
                                   STTransform(scale=(6.0, 0.1),
                                               translate=(5.6, 0.2)))

        vispy.app.Canvas.__init__(self, close_keys='escape')
        self.size = (800, 800)
        self.show()

    def on_draw(self, ev):
        gloo.set_clear_color('black')
        gloo.clear(color=True, depth=True)
        gloo.set_viewport(0, 0, *self.size)
        for line in self.lines:
            line.draw()


if __name__ == '__main__':
    win = Canvas()
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
