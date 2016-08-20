import collections
from contextlib import contextmanager

from grako.model import NodeWalker, Node


class ContextWalker(NodeWalker):
    def __init__(self, initial_context):
        super(ContextWalker, self).__init__()
        self._initial_context = initial_context
        self._context_stack = [initial_context]

    # abstract
    def get_node_context(self, node, *args, **kwargs):
        return node

    # abstract
    def enter_context(self, ctx):
        pass

    # abstract
    def leave_context(self, ctx):
        pass

    def push_context(self, ctx):
        self._context_stack.append(ctx)

    def pop_context(self):
        self._context_stack.pop()

    @property
    def initial_context(self):
        return self._initial_context

    @property
    def context(self):
        return self._context_stack[-1]

    @contextmanager
    def new_context(self, node, *args, **kwargs):
        ctx = self.get_node_context(node, *args, **kwargs)
        if ctx == self.context:
            yield ctx
        else:
            self.enter_context(ctx)
            try:
                self.push_context(ctx)
                try:
                    yield ctx
                finally:
                    self.pop_context()
            finally:
                self.leave_context(ctx)


class PreOrderWalker(NodeWalker):
    def walk(self, node, *args, parent=None, **kwargs):
        supers_walk = super(PreOrderWalker, self).walk

        if isinstance(node, Node):
            new_parent = supers_walk(node, *args, parent=parent, **kwargs)
            for child in node.children():
                self.walk(child, *args, parent=new_parent, **kwargs)
        elif isinstance(node, collections.Mapping):
            return {n: self.walk(e, *args, parent=parent, **kwargs) for n, e in node.items()}
        elif isinstance(node, collections.Iterable):
            return [self.walk(e, *args, parent=parent, **kwargs) for e in iter(node)]
        else:
            return supers_walk(node, *args, parent=parent, **kwargs)
