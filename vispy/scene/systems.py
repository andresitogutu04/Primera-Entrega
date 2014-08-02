# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

import sys

from .visuals.visual import Visual
from ..util._logging import logger


class DrawingSystem(object):
    """ Simple implementation of a drawing engine. There is one system
    per viewbox.

    """
    def process(self, event, subscene):
        # Iterate over entities
        #assert isinstance(subscene, SubScene)  # LC: allow any part of the 
                                                #     scene to be drawn 
        self._process_entity(event, subscene, force_recurse=True)
    
    def _process_entity(self, event, entity, force_recurse=False):
        event.canvas._process_entity_count += 1

        # Push entity and set its total transform
        event.push_entity(entity)
        
        if isinstance(entity, Visual):
            try:
                entity.draw(event)
            except Exception:
                # get traceback and store (so we can do postmortem
                # debugging)
                type, value, tb = sys.exc_info()
                tb = tb.tb_next  # Skip *this* frame
                sys.last_type = type
                sys.last_value = value
                sys.last_traceback = tb
                del tb  # Get rid of it in this namespace
                # Handle
                logger.log_exception()
                logger.warning("Error drawing entity %s" % entity)
        
        # Processs children; recurse. 
        # Do not go into subscenes (SubScene.draw processes the subscene)
        
        # import here to break import cycle.
        # (LC: we should be able to remove this
        # check entirely.)
        from .subscene import SubScene
        
        if force_recurse or not isinstance(entity, SubScene):
            for sub_entity in entity:
                self._process_entity(event, sub_entity)
        
        event.pop_entity()


class MouseInputSystem(object):
    def process(self, event, subscene):
        # For simplicity, this system delivers the event to each entity
        # in the scenegraph, except for widgets that are not under the 
        # press_event. 
        # TODO: 
        #  1. This eventually should be replaced with a picking system.
        #  2. We also need to ensure that if one entity accepts a press 
        #     event, it will also receive all subsequent mouse events
        #     until the button is released.
        
        self._process_entity(event, subscene)
    
    def _process_entity(self, event, entity):
        # Push entity and set its total transform
        event.push_entity(entity)

        from .widgets.widget import Widget
        if isinstance(entity, Widget):
            # widgets are rectangular; easy to do mouse collision 
            # testing
            if event.press_event is None:
                deliver = entity.rect.contains(*event.pos[:2])
            else:
                deliver = entity.rect.contains(*event.press_event.pos[:2])
        else:
            deliver = True
                
        if deliver:
            for sub_entity in entity:
                self._process_entity(event, sub_entity)
                if event.handled:
                    break
            if not event.handled:
                getattr(entity.events, event.type)(event)
        
        event.pop_entity()
