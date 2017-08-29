#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

from access_flags import MethodAccessFlags, InvalidFlags
from attributes import AttributesInfo
from common import *
from signatures import check_method_descriptor, parse_method_descriptor, unqualify_name

__author__ = 'Gonzalo Matamala'
__date__ = ''
__version__ = '0.1.0'


class MethodInfo(BaseEntry):
    def __init__(self, f):
        super().__init__(f)
        self.access_flags = MethodAccessFlags(f)
        self.name_index = f.read_u2()
        self.descriptor_index = f.read_u2()
        self.attributes = AttributesInfo(f)
        self._name = None
        self._descriptor = None
        self._signature = None

    def init(self, constant_pool, is_interface):
        try:
            self._name = constant_pool.get_utf8(self.name_index)
        except ValueError as e:
            self.append_error(str(e), self.pos + 2)
        try:
            self.access_flags.init(is_interface, self.is_initialization())
        except InvalidFlags as e:
            self.append_error('{}: 0x{:4x}'.format(e.message, e.flags), self.pos)
        try:
            self._descriptor = constant_pool.get_utf8(self.descriptor_index)
            if not check_method_descriptor(self._descriptor):
                self.append_error('invalid method descriptor {}'.format(self._descriptor), self.pos + 4)
        except ValueError as e:
            self.append_error(str(e), self.pos + 4)
        if not self.attributes.init(constant_pool):
            self.errors += self.attributes.errors
        return not self.errors

    def name(self):
        return self._name

    def descriptor(self):
        return self._descriptor

    def is_initialization(self):
        return self._name == '<init>' or self._name == '<cinit>'

    def is_class_initialization(self):
        return self._name == '<cinit>'

    def is_instance_initialization(self):
        return self._name == '<init>'

    def signature(self, class_name=None):
        if self._signature is None:
            flags_signature = self.access_flags.signature()
            parameters_signature, return_signature = parse_method_descriptor(self._descriptor)
            self._signature = flags_signature
            if self._signature:
                self._signature += ' '
            if self.is_class_initialization() and not self.access_flags._is_static():
                self._signature += 'static '
            self._signature += return_signature + ' '
            if self.is_initialization() and class_name:
                self._signature += unqualify_name(class_name)
            else:
                self._signature += self._name
            self._signature += parameters_signature
        return self._signature


class MethodsInfo(ListEntry):
    def __init__(self, f):
        super().__init__(MethodInfo, f)

    def init(self, constant_pool, is_interface):
        for method in self.entries:
            if not method.init(constant_pool, is_interface):
                self.add_errors(method.errors)
        return not self.errors
