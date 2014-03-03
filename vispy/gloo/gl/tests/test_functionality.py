
import sys

from nose.plugins.skip import SkipTest
from nose.tools import assert_equal
from numpy.testing import assert_almost_equal

from vispy.app.backends import requires_non_glut

from vispy.gloo import gl
from vispy.util import app_opengl_context


# All these tests require a working backend. GLUT is not an option,
# since there is no safe way to terminate the mainloop.
# requires_non_glut works if there is a backend other then GLUT available.


@requires_non_glut()
def test_functionality_desktop():
    """ Test that desktop GL backend functions appropriately. """
    _test_functonality('desktop')


@requires_non_glut()
@gl._requires_pyopengl()
def test_functionality_pypengl():
    """ Test that pyopengl GL backend functions appropriately. """
    _test_functonality('pyopengl')


@requires_non_glut()
def test_functionality_angle():
    """ Test that angle GL backend functions appropriately. """
    if True:
        raise SkipTest('Skip Angle functionality test for now.')
    if sys.platform.startswith('win'):
        raise SkipTest('Can only test angle functionality on Windows.')

    _test_functonality('angle')


def _test_functonality(backend):
    """ Create app and canvas so we have a context. Then run tests.
    """

    # use the backend
    gl.use(backend)

    # Create app and canvas to get an OpenGL context
    with app_opengl_context():
        _test_setting_parameters()
        _test_enabling_disabling()
        _test_setting_stuff()
        _test_object_creation_and_deletion()


def _test_setting_parameters():
    # Set some parameters and get result
    clr = 1.0, 0.1, 0.2, 0.7
    gl.glClearColor(*clr)
    assert_almost_equal(gl.glGetParameter(gl.GL_COLOR_CLEAR_VALUE), clr)
    #
    gl.glCullFace(gl.GL_FRONT)
    assert_equal(gl.glGetParameter(gl.GL_CULL_FACE_MODE), gl.GL_FRONT)
    gl.glCullFace(gl.GL_BACK)
    assert_equal(gl.glGetParameter(gl.GL_CULL_FACE_MODE), gl.GL_BACK)
    #
    gl.glDepthFunc(gl.GL_NOTEQUAL)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_FUNC), gl.GL_NOTEQUAL)
    #
    val = 0.2, 0.3
    gl.glDepthRange(*val)
    assert_almost_equal(gl.glGetParameter(gl.GL_DEPTH_RANGE), val)


def _test_enabling_disabling():
    # Enabling/disabling
    gl.glEnable(gl.GL_DEPTH_TEST)
    assert_equal(gl.glIsEnabled(gl.GL_DEPTH_TEST), True)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_TEST), 1)
    gl.glDisable(gl.GL_DEPTH_TEST)
    assert_equal(gl.glIsEnabled(gl.GL_DEPTH_TEST), False)
    assert_equal(gl.glGetParameter(gl.GL_DEPTH_TEST), 0)
    #
    gl.glEnable(gl.GL_BLEND)
    assert_equal(gl.glIsEnabled(gl.GL_BLEND), True)
    assert_equal(gl.glGetParameter(gl.GL_BLEND), 1)
    gl.glDisable(gl.GL_BLEND)
    assert_equal(gl.glIsEnabled(gl.GL_BLEND), False)
    assert_equal(gl.glGetParameter(gl.GL_BLEND), 0)


def _test_setting_stuff():
    # Just do some actions
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glFlush()


def _test_object_creation_and_deletion():

    # Stuff that is originally glGenX

    # Create/delete texture
    assert_equal(gl.glIsTexture(1), False)
    handle = gl.glCreateTexture()
    gl.glBindTexture(gl.GL_TEXTURE_2D, handle)
    assert_equal(gl.glIsTexture(handle), True)
    gl.glDeleteTexture(handle)
    assert_equal(gl.glIsTexture(handle), False)

    # Create/delete buffer
    assert_equal(gl.glIsBuffer(1), False)
    handle = gl.glCreateBuffer()
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, handle)
    assert_equal(gl.glIsBuffer(handle), True)
    gl.glDeleteBuffer(handle)
    assert_equal(gl.glIsBuffer(handle), False)

    # Create/delete framebuffer
    assert_equal(gl.glIsFramebuffer(1), False)
    handle = gl.glCreateFramebuffer()
    gl.glBindFramebuffer(gl.GL_FRAMEBUFFER, handle)
    assert_equal(gl.glIsFramebuffer(handle), True)
    gl.glDeleteFramebuffer(handle)
    assert_equal(gl.glIsFramebuffer(handle), False)

    # Create/delete renderbuffer
    assert_equal(gl.glIsRenderbuffer(1), False)
    handle = gl.glCreateRenderbuffer()
    gl.glBindRenderbuffer(gl.GL_RENDERBUFFER, handle)
    assert_equal(gl.glIsRenderbuffer(handle), True)
    gl.glDeleteRenderbuffer(handle)
    assert_equal(gl.glIsRenderbuffer(handle), False)

    # Stuff that is originally called glCreate

    # Create/delete program
    assert_equal(gl.glIsProgram(1), False)
    handle = gl.glCreateProgram()
    assert_equal(gl.glIsProgram(handle), True)
    gl.glDeleteProgram(handle)
    assert_equal(gl.glIsProgram(handle), False)

    # Create/delete shader
    assert_equal(gl.glIsShader(1), False)
    handle = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    assert_equal(gl.glIsShader(handle), True)
    gl.glDeleteShader(handle)
    assert_equal(gl.glIsShader(handle), False)


# if __name__ == '__main__':
#     test_functionality_desktop()
#     test_functionality_pypengl()
