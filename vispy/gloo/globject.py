# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Vispy Development Team. All Rights Reserved.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------

class GLObject(object):
    """ Generic GL object that may live both on CPU and GPU """

    # Internal id counter to keep track of GPU objects
    _idcount = 0

    def __init__(self):
        """ Initialize the object in the default state """

        self._handle = -1
        self._target = None
        self._need_create = True
        self._need_update = True
        self._need_delete = False

        GLObject._idcount += 1
        self._id = GLObject._idcount


    def delete(self):
        """ Delete the object from GPU memory """

        if self._need_delete:
            self._delete()
        self._handle = -1
        self._need_create = True
        self._need_update = True
        self._need_delete = False


    def activate(self):
        """ Activate the object on GPU """

        if self._need_create:
            self._create()
            self._need_create = False
        self._activate()
        if self._need_update:
            self._update()
            self._need_update = False


    def deactivate(self):
        """ Deactivate the object on GPU """

        self._deactivate()


    def update(self):
        """ Update the object in GPU """

        if not self._need_update:
            return
        self.activate()
        self._update()
        self._need_update = False
        self.deactivate()


    @property
    def handle(self):
        """ Name of this object on the GPU """

        return self._handle


    @property
    def target(self):
        """ OpenGL type of object. """

        return self._target


    def _create(self):
        """ Dummy create method """

        pass


    def _delete(self):
        """ Dummy delete method """

        pass


    def _activate(self):
        """ Dummy activate method """

        pass


    def _deactivate(self):
        """ Dummy deactivate method """

        pass


    def _update(self):
        """ Dummy update method """

        pass
