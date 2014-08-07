# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of EllipseVisual. 
"""

import vispy.app
from vispy import gloo
from vispy.scene import visuals, transforms


class Canvas(vispy.app.Canvas):
    def __init__(self):
        self.ellipse = visuals.Ellipse(pos=(0.5, 0.3, 0), radius=(0.4, 0.3),
                                       color=(1, 0, 0, 1),
                                       border_color=(1, 1, 1, 1),
                                       start_angle=180., span_angle=150.)
        self.ellipse.transform = transforms.STTransform(scale=(0.5, 1.5))
        
        vispy.app.Canvas.__init__(self, close_keys='escape')
        self.size = (800, 800)
        self.show()
        
    def on_draw(self, ev):
        gloo.set_clear_color((0, 0, 0, 1))
        gloo.clear()
        gloo.set_viewport(0, 0, *self.size)
        self.ellipse.draw()
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
