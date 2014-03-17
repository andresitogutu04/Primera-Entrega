# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import numpy as np

from . import gl


def _screenshot(viewport=None):
    """ Take a screenshot using glReadPixels. Not sure where to put this
    yet, so a private function for now. Used in make.py.
    """
    # gl.glReadBuffer(gl.GL_BACK)  Not avaliable in ES 2.0
    if viewport is None:
        viewport = gl.glGetParameter(gl.GL_VIEWPORT)
    x, y, w, h = viewport
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 1)  # PACK, not UNPACK
    im = gl.glReadPixels(x, y, w, h, gl.GL_RGB, gl.GL_UNSIGNED_BYTE)
    gl.glPixelStorei(gl.GL_PACK_ALIGNMENT, 4)
    # reshape, flip, and return
    if not isinstance(im, np.ndarray):
        im = np.frombuffer(im, np.uint8)
    im.shape = h, w, 3
    im = np.flipud(im)
    return im


KEYWORDS = set(['active', 'asm', 'cast', 'class', 'common', 'default',
                'double', 'dvec2', 'dvec3', 'dvec4', 'enum', 'extern',
                'external', 'filter', 'fixed', 'flat', 'fvec2', 'fvec3',
                'fvec4', 'goto', 'half', 'hvec2', 'hvec3', 'hvec4', 'iimage1D',
                'iimage1DArray', 'iimage2D', 'iimage2DArray', 'iimage3D',
                'iimageBuffer', 'iimageCube', 'image1D', 'image1DArray',
                'image1DArrayShadow', 'image1DShadow', 'image2D',
                'image2DArray', 'image2DArrayShadow', 'image2DShadow',
                'image3D', 'imageBuffer', 'imageCube', 'inline', 'input',
                'interface', 'long', 'namespace', 'noinline', 'output',
                'packed', 'partition', 'public', 'row_major', 'sampler1D',
                'sampler1DShadow', 'sampler2DRect', 'sampler2DRectShadow',
                'sampler2DShadow', 'sampler3D', 'sampler3DRect', 'short',
                'sizeof', 'static', 'superp', 'switch', 'template', 'this',
                'typedef', 'uimage1D', 'uimage1DArray', 'uimage2D',
                'uimage2DArray', 'uimage3D', 'uimageBuffer', 'uimageCube',
                'union', 'unsigned', 'using', 'volatile'])


def check_variable(name):
    """
    Return None if *name* is expected to be a valid variable name in any GLSL
    version. Otherwise, return a string describing the problem.
    """
    # Limit imposed by glGetActive* in pyopengl
    if len(name) > 31:
        return ("Variable names >31 characters may not function on some "
                "systems.")
    
    return check_identifier(name)


def check_identifier(name):
    if '__' in name:
        return "Identifiers may not contain double-underscores."
    
    if name[:3] == 'gl_' or name[:3] == 'GL_':
        return "Identifiers may not begin with gl_ or GL_."
    
    if name in KEYWORDS:
        return "Identifier is a reserved keyword."
