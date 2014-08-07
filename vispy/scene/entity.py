# -*- coding: utf-8 -*-
# Copyright (c) 2014, Vispy Development Team.
# Distributed under the (new) BSD License. See LICENSE.txt for more info.

from __future__ import division

from . import transforms
from ..util.event import EmitterGroup, Event
from .events import SceneDrawEvent, SceneMouseEvent
from .transforms import NullTransform


class Entity(object):
    """ Base class to represent a citizen of a scene. Typically an
    Entity is used to visualize something, although this is not strictly
    necessary. It may for instance also be used as a container to apply
    a certain transformation to a group of objects, or an object that
    performs a specific task without being visible.

    Each entity can have zero or more children. Each entity will
    typically have one parent, although multiple parents are allowed.
    It is recommended to use multi-parenting with care.
    """

    def __init__(self, parent=None, name=None):
        self.events = EmitterGroup(source=self,
                                   auto_connect=True,
                                   parents_change=Event,
                                   active_parent_change=Event,
                                   children_change=Event,
                                   mouse_press=SceneMouseEvent,
                                   mouse_move=SceneMouseEvent,
                                   mouse_release=SceneMouseEvent,
                                   mouse_wheel=SceneMouseEvent,
                                   draw=SceneDrawEvent,
                                   children_drawn=SceneDrawEvent,
                                   update=Event,
                                   transform_change=Event,
                                   )
        self.name = name

        # Entities are organized in a parent-children hierarchy
        # todo: I think we want this to be a list. The order *may* be important
        # for some drawing systems. Using a set may lead to inconsistency
        self._children = set()
        # TODO: use weakrefs for parents.
        self._parents = set()
        if parent is not None:
            self.parents = parent

        # Components that all entities in vispy have
        # todo: default transform should be trans-scale-rot transform
        self._transform = transforms.NullTransform()
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self, n):
        self._name = n

    @property
    def children(self):
        """ The list of children of this entity. The children are in
        arbitrary order.
        """
        return list(self._children)

    @property
    def parent(self):
        """ Get/set the parent. If the entity has multiple parents while
        using this property as a getter, an error is raised.
        """
        if not self._parents:
            return None
        elif len(self._parents) == 1:
            return tuple(self._parents)[0]
        else:
            raise RuntimeError('Ambiguous parent: there are multiple parents.')

    @parent.setter
    def parent(self, parent):
        # This is basically an alias
        self.parents = parent

    @property
    def parents(self):
        """ Get/set a tuple of parents.
        """
        return tuple(self._parents)

    @parents.setter
    def parents(self, parents):
        # Test input
        if isinstance(parents, Entity):
            parents = (parents,)
        if not hasattr(parents, '__iter__'):
            raise ValueError("Entity.parents must be iterable (got %s)"
                             % type(parents))

        # Test that all parents are entities
        for p in parents:
            if not isinstance(p, Entity):
                raise ValueError('A parent of an entity must be an entity too,'
                                 ' not %s.' % p.__class__.__name__)

        # convert to set
        prev = self._parents.copy()
        parents = set(parents)

        with self.events.parents_change.blocker():
            # Remove from parents
            for parent in prev - parents:
                self.remove_parent(parent)
            # Add new
            for parent in parents - prev:
                self.add_parent(parent)

        self.events.parents_change(new=parents, old=prev)

    def add_parent(self, parent):
        if parent in self._parents:
            return
        self._parents.add(parent)
        parent._add_child(self)
        self.events.parents_change(added=parent)
        self.update()

    def remove_parent(self, parent):
        if parent not in self._parents:
            raise ValueError("Parent not in set of parents for this entity.")
        self._parents.remove(parent)
        parent._remove_child(self)
        self.events.parents_change(removed=parent)

    def _add_child(self, ent):
        self._children.add(ent)
        self.events.children_change(added=ent)
        ent.events.update.connect(self.events.update)

    def _remove_child(self, ent):
        self._children.remove(ent)
        self.events.children_change(removed=ent)
        ent.events.update.disconnect(self.events.update)

    def __iter__(self):
        return self._children.__iter__()

    @property
    def transform(self):
        """ The transform that maps the local coordinate frame to the
        coordinate frame of the parent.
        """
        return self._transform

    @transform.setter
    def transform(self, tr):
        if self._transform is not None:
            self._transform.changed.disconnect(self._transform_changed)
        assert isinstance(tr, transforms.Transform)
        self._transform = tr
        self._transform.changed.connect(self._transform_changed)
        self._transform_changed(None)

    def _transform_changed(self, event):
        self.events.transform_change()
        self.update()

    def _parent_chain(self):
        """
        Return the chain of parents starting from this entity. The chain ends
        at the first entity with either no parents or multiple parents.
        """
        chain = [self]
        while True:
            try:
                parent = chain[-1].parent
            except Exception:
                break
            if parent is None:
                break
            chain.append(parent)
        return chain

    def common_parent(self, entity):
        """
        Return the common parent of two entities. If the entities have no 
        common parent, return None. Does not search past multi-parent branches.
        """
        p1 = self._parent_chain()
        p2 = entity._parent_chain()
        for p in p1:
            if p in p2:
                return p
        return None
        
    def entity_transform(self, entity):
        """
        Return the transform that maps from the coordinate system of
        *entity* to the local coordinate system of *self*.
        
        Note that there must be a _single_ path in the scenegraph that connects
        the two entities; otherwise an exception will be raised.        
        """
        cp = self.common_parent(entity)
        # First map from entity to common parent
        tr = NullTransform()
        
        while entity is not cp:
            if entity.transform is not None:
                tr = entity.transform * tr
            
            entity = entity.parent
        
        if entity is self:
            return tr
        
        # Now map from common parent to self
        tr2 = cp.entity_transform(self)
        return tr2.inverse() * tr
        
#     def on_draw(self, event):
#         """
#         Draw this entity, given that we are drawing through
#         the given scene *path*.
#         """
#         pass

#     def _process_draw_event(self, event):
#         """
#         Draw the entire tree of Entities beginning here.
#         """
#         for enter, path in self.walk():
#             event._set_path(path)
#             entity = path[-1]
#             if enter:
#                 entity.events.draw(event)
#             else:
#                 entity.events.children_drawn(event)

    def _process_mouse_event(self, event):
        """
        Propagate a mouse event through the scene tree starting at this Entity.
        """
        # 1. find all entities whose mouse-area includes the click point.
        # 2. send the event to each entity one at a time
        #    (we should use a specialized emitter for this, rather than
        #     rebuild the emitter machinery!)

        # TODO: for now we send the event to all entities; need to use
        # picking to decide which entities should receive the event.
        for enter, path in self.walk():
            event._set_path(path)
            entity = path[-1]
            getattr(entity.events, event.type)(event)

#     def walk(self, path=None):
#         """
#         Return an iterator that walks the entire scene graph starting at this
#         Entity. Yields (True, [list of Entities]) as each path in the
#         scenegraph is visited. Yields (False, [list of Entities]) as each
#         path is finished.
#         """
#         # TODO: need some control over the order..
#         #if path is None:
#             #path = []
#             #yield path, self
#         #if len(self.children) > 0:
#             #path = path + [self]
#             #yield path, self.children
#             #for ch in self:
#                 #for e in ch.walk(path):
#                     #yield e
#         path = (path or []) + [self]
#         yield (True, path)
#         for ch in self:
#             for p in ch.walk(path):
#                 yield p
#         yield (False, path)

    def update(self):
        """
        Emit an event to inform Canvases that this Entity needs to be redrawn.
        """
        self.events.update()

    def __str__(self):
        name = "" if self.name is None else " name="+self.name
        return "<%s%s id=0x%x>" % (self.__class__.__name__, name, id(self))
