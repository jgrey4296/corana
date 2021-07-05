#!/usr/bin/env python3
from code_analysis.util.parse_base import ParseBase

class LuaClass(ParseBase):

    def __init__(self, name, parent=None):
        super().__init__()
        self._type = "Class"
        self._name = name
        self._parent = parent

    def __str__(self):
        parent = ""
        if self._parent is not None:
            parent = self._parent

        return "{} : {} : {} : {}".format(self._line_no,
                                          self._type,
                                          self._name,
                                          self._parent)

class LuaFn(ParseBase):

    def __init__(self, name):
        super().__init__()
        self._type = "Function"
        self._name = name

class LuaRecipe(ParseBase):

    def __init__(self, name, rest):
        super().__init__()
        self._type = "Recipe"
        self._name = name
        self._rest = rest

    def __str__(self):
        return "{} : {} : {} : {}".format(self._line_no,
                                          self._type,
                                          self._name,
                                          self._rest)
