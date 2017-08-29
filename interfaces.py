#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

from common import *


__author__ = 'Gonzalo Matamala'
__date__ = '2017-08-29'
__version__ = '0.1.0'


class InterfacesInfo(BaseEntry):
    def __init__(self, f):
        super().__init__(f)
        self.interfaces_count = f.read_u2()
        self.interfaces = []
        for i in range(self.interfaces_count):
            self.interfaces.append(f.read_u2)
        self._names = []

    def init(self, constant_pool):
        for i, interface in enumerate(self.interfaces):
            name = ''
            try:
                name = constant_pool.get_class_name(interface)
            except ValueError as e:
                self.append_error(str(e), self.pos + 2 * (i + 1))
            self._names.append(name)
        return not self.errors

    def signature(self):
        return ', '.join(self._names)
