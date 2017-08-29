#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-
from access_flags import FieldAccessFlags, InvalidFlags
from attributes import AttributesInfo
from common import *
from signatures import check_unqualified_name, check_field_descriptor

__author__ = 'Gonzalo Matamala'
__date__ = '2017-08-29'
__version__ = '0.1.0'


class FieldInfo(BaseEntry):
    def __init__(self, f):
        super().__init__(f)
        self.access_flags = FieldAccessFlags(f)
        self.name_index = f.read_u2()
        self.descriptor_index = f.read_u2()
        self.attributes = AttributesInfo(f)
        self._name = None
        self._descriptor = None

    def init(self, constant_pool):
        try:
            self.access_flags.init()
        except InvalidFlags as e:
            self.append_error('{}: 0x{:4x}'.format(e.message, e.flags), self.pos)
        try:
            self._name = constant_pool.get_utf8(self.name_index)
            if not check_unqualified_name(self._name):
                self.append_error('invalid field\'s unqualified name {}'.format(self._name), self.pos + 2)
        except ValueError as e:
            self.append_error(str(e), self.pos + 2)
        try:
            self._descriptor = constant_pool.get_utf8(self.descriptor_index)
            if not check_field_descriptor(self._descriptor):
                self.append_error('invalid field descriptor {}'.format(self._descriptor), self.pos + 4)
        except ValueError as e:
            self.append_error(str(e), self.pos + 4)
        if not self.attributes.init(constant_pool):
            self.add_errors(self.attributes.errors)

    def get_constant_value(self):
        pass


class FieldsInfo(ListEntry):
    def __init__(self, f):
        super().__init__(FieldInfo, f)
