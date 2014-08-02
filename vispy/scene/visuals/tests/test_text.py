# -*- coding: utf-8 -*-
from nose.tools import assert_equal

from vispy.app import Canvas
from vispy.scene.visuals import Text
from vispy.scene.transforms import STTransform
from vispy import gloo
from vispy.testing import requires_application


@requires_application()
def test_text():
    """Test basic text support"""
    with Canvas(size=(100, 100)) as c:
        text = Text('X', bold=True, color=(1., 1., 1., 1.))
        transform = STTransform((1., 1., 1.))
        text._program['transform'] = transform.shader_map()
        gloo.set_viewport(0, 0, *c.size)
        gloo.clear(color=(0., 0., 0., 1.))
        text.draw()

        s = gloo.util._screenshot()
        assert_equal(s.min(), 0)
        assert_equal(s.max(), 255)

        # let's just peek at the texture, make sure it has something
        gloo.clear(color=(0., 0., 0., 1.))
        gloo.util.draw_texture(text._font._atlas)
        s = gloo.util._screenshot()
        assert_equal(s.max(), 255)
        assert_equal(s.min(), 0)
