# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import unittest
import numpy as np
from vispy.gloo import gl

from vispy.gloo.framebuffer import RenderBuffer, FrameBuffer
from vispy.gloo.texture import Texture2D


class RenderBufferTest(unittest.TestCase):

    def test_init(self):
        # Init without args
        buffer = RenderBuffer()
        self.assertEqual(buffer._handle, 0)
        self.assertEqual(buffer._need_update, False)
        self.assertEqual(buffer._valid, False)

        # Init with shape
        buffer = RenderBuffer((100, 100))
        self.assertEqual(buffer._need_update, True)

    def test_setting_shape(self):
        buffer = RenderBuffer()

        # No format
        buffer.set_shape((100, 100))
        self.assertEqual(buffer._shape, (100, 100))
        self.assertEqual(buffer._format, None)
        #
        buffer.set_shape((100, 100, 1))
        self.assertEqual(buffer._shape, (100, 100))
        self.assertEqual(buffer._format, None)
        #
        buffer.set_shape((100, 100, 3))
        self.assertEqual(buffer._shape, (100, 100))
        self.assertEqual(buffer._format, None)

        # With invalid shape
        with self.assertRaises(ValueError):
            buffer.set_shape(None)
        with self.assertRaises(ValueError):
            buffer.set_shape(4)
        with self.assertRaises(ValueError):
            buffer.set_shape('test')
        with self.assertRaises(ValueError):
            buffer.set_shape((100,))
        with self.assertRaises(ValueError):
            buffer.set_shape((100, 100, 9))
        with self.assertRaises(ValueError):
            buffer.set_shape((100, 100, 3, 3))

        # With valid format
        buffer.set_shape((100, 100), gl.ext.GL_RGBA8)
        self.assertEqual(buffer._shape, (100, 100))
        self.assertEqual(buffer._format, gl.ext.GL_RGBA8)
        #
        buffer.set_shape((100, 100), gl.GL_DEPTH_COMPONENT16)
        self.assertEqual(buffer._shape, (100, 100))
        self.assertEqual(buffer._format, gl.GL_DEPTH_COMPONENT16)

        # With invalid format
        with self.assertRaises(ValueError):
            buffer.set_shape((100, 100), gl.GL_LUMINANCE)
        with self.assertRaises(ValueError):
            buffer.set_shape((100, 100), gl.GL_RGB)

    def test_resetting_shape(self):
        buffer = RenderBuffer()

        # Set same shape
        buffer.set_shape((100, 100))
        self.assertEqual(buffer._need_update, True)
        buffer._need_update = False
        #
        buffer.set_shape((100, 100))
        self.assertEqual(buffer._need_update, False)
        #
        buffer.set_shape((100, 100, 1))
        self.assertEqual(buffer._need_update, False)
        buffer.set_shape((100, 100, 3))
        self.assertEqual(buffer._need_update, False)

        # Set different shape
        buffer.set_shape((100, 101))
        self.assertEqual(buffer._need_update, True)


class FrameBufferTest(unittest.TestCase):

    def test_init(self):
        # Init without args
        fbo = FrameBuffer()
        self.assertEqual(fbo._handle, 0)
        self.assertEqual(fbo._need_update, False)
        self.assertEqual(fbo._valid, False)

        # Init with args
        fbo = FrameBuffer(RenderBuffer())
        self.assertEqual(fbo._need_update, True)

    def test_attaching(self):
        fbo = FrameBuffer()
        buffer = RenderBuffer()
        texture = Texture2D()

        # Attaching color
        fbo = FrameBuffer()
        fbo.attach_color(buffer)
        self.assertEqual(fbo._attachment_color, buffer)
        self.assertEqual(len(fbo._pending_attachments), 1)
        #
        fbo.attach_color(texture)
        self.assertEqual(fbo._attachment_color, texture)
        self.assertEqual(len(fbo._pending_attachments), 2)
        #
        fbo.attach_color(None)
        self.assertEqual(fbo._attachment_color, None)
        self.assertEqual(len(fbo._pending_attachments), 3)
        #
        with self.assertRaises(ValueError):
            fbo.attach_color("test")
        with self.assertRaises(ValueError):
            fbo.attach_color(3)

        # Attaching depth
        fbo = FrameBuffer()
        fbo.attach_depth(buffer)
        self.assertEqual(fbo._attachment_depth, buffer)
        self.assertEqual(len(fbo._pending_attachments), 1)
        #
        fbo.attach_depth(texture)
        self.assertEqual(fbo._attachment_depth, texture)
        self.assertEqual(len(fbo._pending_attachments), 2)
        #
        fbo.attach_depth(None)
        self.assertEqual(fbo._attachment_depth, None)
        self.assertEqual(len(fbo._pending_attachments), 3)
        #
        with self.assertRaises(ValueError):
            fbo.attach_depth("test")
        with self.assertRaises(ValueError):
            fbo.attach_depth(3)

        # Attach stencil
        fbo = FrameBuffer()
        fbo.attach_stencil(buffer)
        self.assertEqual(fbo._attachment_stencil, buffer)
        self.assertEqual(len(fbo._pending_attachments), 1)
        #
        with self.assertRaises(ValueError):
            fbo.attach_stencil(texture)
        #
        fbo.attach_stencil(None)
        self.assertEqual(fbo._attachment_stencil, None)
        self.assertEqual(len(fbo._pending_attachments), 2)
        #
        with self.assertRaises(ValueError):
            fbo.attach_stencil("test")
        with self.assertRaises(ValueError):
            fbo.attach_stencil(3)

    def test_level(self):
        fbo = FrameBuffer()
        buffer = RenderBuffer()
        texture = Texture2D()

        # Valid level
        fbo.attach_color(texture, 1)
        self.assertEqual(fbo._pending_attachments[-1][2], 1)
        fbo.attach_color(texture, 2)
        self.assertEqual(fbo._pending_attachments[-1][2], 2)

        # Invalid level
        with self.assertRaises(ValueError):
            fbo.attach_color(texture, 1.1)
        with self.assertRaises(ValueError):
            fbo.attach_color(texture, "test")

    def test_auto_format(self):
        fbo = FrameBuffer()

        buffer = RenderBuffer((100, 100))
        fbo.attach_color(buffer)
        self.assertEqual(buffer._format, gl.GL_RGB565)

        buffer = RenderBuffer((100, 100))
        fbo.attach_depth(buffer)
        self.assertEqual(buffer._format, gl.GL_DEPTH_COMPONENT16)

        buffer = RenderBuffer((100, 100))
        fbo.attach_stencil(buffer)
        self.assertEqual(buffer._format, gl.GL_STENCIL_INDEX8)


if __name__ == "__main__":
    unittest.main()
