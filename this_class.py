#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

from access_flags import ClassAccessFlags, InvalidFlags
from attributes import AttributesInfo
from common import *
from fields import FieldsInfo
from interfaces import InterfacesInfo
from methods import MethodsInfo
from signatures import unqualify_name


__author__ = 'Gonzalo Matamala'
__date__ = ''
__version__ = '0.1.0'


class ThisClassInfo(BaseEntry):
    def __init__(self, f):
        super().__init__(f)
        self.access_flags = ClassAccessFlags(f)
        self.this_class = f.read_u2()
        self.super_class = f.read_u2()
        self.interfaces = InterfacesInfo(f)
        self.fields = FieldsInfo(f)
        self.methods = MethodsInfo(f)
        self.attributes = AttributesInfo(f)
        self._name = None
        self._unqualified_name = None
        self._super_name = None
        self._signature = None

    def init(self, constant_pool):
        try:
            self.access_flags.init()
        except InvalidFlags as e:
            self.append_error('{}: 0x{:4x}'.format(e.message, e.flags), self.pos)
        try:
            self._name = constant_pool.get_class_name(self.this_class)
            self._unqualified_name = unqualify_name(self._name)
        except ValueError as e:
            self.append_error(str(e), self.pos + 2)
        if self.super_class > 0:
            try:
                self._super_name = constant_pool.get_class_name(self.super_class)
            except ValueError as e:
                self.append_error(str(e), self.pos + 4)
        if not self.interfaces.init(constant_pool):
            self.add_errors(self.interfaces.errors)
        if not self.fields.init(constant_pool):
            self.add_errors(self.fields.errors)
        if not self.methods.init(constant_pool, self.is_interface()):
            self.add_errors(self.methods.errors)
        if not self.attributes.init(constant_pool):
            self.add_errors(self.attributes.errors)
        return not self.errors

    def name(self):
        return self._name

    def is_enum(self):
        return self.access_flags._is_enum()

    def is_interface(self):
        return self.access_flags.is_interface()

    def signature(self):
        if self._signature is None:
            self._signature = self.access_flags.signature() + ' ' + self._unqualified_name
            if self._super_name:
                self._signature += ' extends ' + self._super_name
            if self.interfaces.interfaces_count:
                self._signature += ' implements ' + self.interfaces.signature()
            self._signature += ' {\n'
            for method in self.methods.entries:
                self._signature += '\t' + method.signature(self._unqualified_name) + ';\n'
            self._signature += '}'
        return self._signature
