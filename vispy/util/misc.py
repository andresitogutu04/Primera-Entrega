# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

"""Miscellaneous functions
"""

import numpy as np
import sys
import getopt

from .event import EmitterGroup, EventEmitter, Event
from ._logging import logger, set_log_level


###############################################################################
# These fast normal calculation routines are adapted from mne-python

def _fast_cross_3d(x, y):
    """Compute cross product between list of 3D vectors

    Much faster than np.cross() when the number of cross products
    becomes large (>500). This is because np.cross() methods become
    less memory efficient at this stage.

    Parameters
    ----------
    x : array
        Input array 1.
    y : array
        Input array 2.

    Returns
    -------
    z : array
        Cross product of x and y.

    Notes
    -----
    x and y must both be 2D row vectors. One must have length 1, or both
    lengths must match.
    """
    assert x.ndim == 2
    assert y.ndim == 2
    assert x.shape[1] == 3
    assert y.shape[1] == 3
    assert (x.shape[0] == 1 or y.shape[0] == 1) or x.shape[0] == y.shape[0]
    if max([x.shape[0], y.shape[0]]) >= 500:
        return np.c_[x[:, 1] * y[:, 2] - x[:, 2] * y[:, 1],
                     x[:, 2] * y[:, 0] - x[:, 0] * y[:, 2],
                     x[:, 0] * y[:, 1] - x[:, 1] * y[:, 0]]
    else:
        return np.cross(x, y)


def _calculate_normals(rr, tris):
    """Efficiently compute vertex normals for triangulated surface"""
    # ensure highest precision for our summation/vectorization "trick"
    rr = rr.astype(np.float64)
    # first, compute triangle normals
    r1 = rr[tris[:, 0], :]
    r2 = rr[tris[:, 1], :]
    r3 = rr[tris[:, 2], :]
    tri_nn = _fast_cross_3d((r2 - r1), (r3 - r1))

    #   Triangle normals and areas
    size = np.sqrt(np.sum(tri_nn * tri_nn, axis=1))
    size[size == 0] = 1.0  # prevent ugly divide-by-zero
    tri_nn /= size[:, np.newaxis]

    npts = len(rr)

    # the following code replaces this, but is faster (vectorized):
    #
    # for p, verts in enumerate(tris):
    #     nn[verts, :] += tri_nn[p, :]
    #
    nn = np.zeros((npts, 3))
    for verts in tris.T:  # note this only loops 3x (number of verts per tri)
        for idx in range(3):  # x, y, z
            nn[:, idx] += np.bincount(verts, tri_nn[:, idx], minlength=npts)
    size = np.sqrt(np.sum(nn * nn, axis=1))
    size[size == 0] = 1.0  # prevent ugly divide-by-zero
    nn /= size[:, np.newaxis]
    return nn


###############################################################################
# CONFIG

class ConfigEvent(Event):

    """ Event indicating a configuration change.

    This class has a 'changes' attribute which is a dict of all name:value
    pairs that have changed in the configuration.
    """

    def __init__(self, changes):
        Event.__init__(self, type='config_change')
        self.changes = changes


class Config(object):

    """ Container for global settings used application-wide in vispy.

    Events:
    -------
    Config.events.changed - Emits ConfigEvent whenever the configuration
    changes.
    """

    def __init__(self):
        self.events = EmitterGroup(source=self)
        self.events['changed'] = EventEmitter(
            event_class=ConfigEvent,
            source=self)
        self._config = {}

    def __getitem__(self, item):
        return self._config[item]

    def __setitem__(self, item, val):
        self._config[item] = val
        # inform any listeners that a configuration option has changed
        self.events.changed(changes={item: val})

    def update(self, **kwds):
        self._config.update(kwds)
        self.events.changed(changes=kwds)

    def __repr__(self):
        return repr(self._config)

config = Config()
config.update(
    default_backend='qt',
    qt_lib='any',  # options are 'pyqt', 'pyside', or 'any'
    show_warnings=False,
    gl_debug=False,
    logging_level='info',
)

set_log_level(config['logging_level'])


def parse_command_line_arguments():
    """ Transform vispy specific command line args to vispy config.
    Put into a function so that any variables dont leak in the vispy namespace.
    """
    # Get command line args for vispy
    argnames = ['vispy-backend', 'vispy-gl-debug']
    try:
        opts, args = getopt.getopt(sys.argv[1:], '', argnames)
    except getopt.GetoptError:
        opts = []
    # Use them to set the config values
    for o, a in opts:
        if o.startswith('--vispy'):
            if o == '--vispy-backend':
                config['default_backend'] = a
                logger.info('backend', a)
            elif o == '--vispy-gl-debug':
                config['gl_debug'] = True
            else:
                logger.warning("Unsupported vispy flag: %s" % o)
