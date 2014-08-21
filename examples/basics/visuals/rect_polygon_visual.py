# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""
Simple demonstration of RectPolygonVisual. 
"""

import vispy.app
from vispy import gloo
from vispy.scene import visuals


class Canvas(vispy.scene.SceneCanvas):
    def __init__(self):
        self.rectpolygon = visuals.RectPolygon(pos=(400, 400, 0), height=250.,
                                               width=300.,
                                               radius=[80., 0., 45., 25.],
                                               color='red',
                                               border_color='white')
        
        vispy.scene.SceneCanvas.__init__(self, keys='interactive')
        self.size = (800, 800)
        self.show()
        
    def on_draw(self, ev):
        gloo.clear('black')
        self.draw_visual(self.rectpolygon)
        

if __name__ == '__main__':
    win = Canvas() 
    import sys
    if sys.flags.interactive != 1:
        vispy.app.run()
