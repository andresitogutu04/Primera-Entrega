# -*- coding: utf-8 -*-

from ._testing import (SkipTest, requires_application, requires_img_lib,  # noqa
                      assert_is, assert_in, assert_not_in, has_backend,  # noqa
                      glut_skip, requires_pyopengl, requires_scipy,  # noqa
                      assert_image_equal, save_testing_image, TestingCanvas)  # noqa
from ._runners import _tester  # noqa
