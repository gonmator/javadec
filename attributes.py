#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

from common import *


__author__ = 'Gonzalo Matamala'
__date__ = '2017-08-25'
__version__ = '0.1.0'


class AttributeInfo(BaseEntry):
    def __init__(self, f):
        super().__init__(f)
        self.attribute_name_index = f.read_u2()
        self.attribute_length = f.read_u4()
        self.info = f.read_buffer(self.attribute_length)
        self._name = None

    def init(self, constant_pool):
        try:
            self._name = constant_pool.get_utf8(self.attribute_name_index)
        except ValueError as e:
            self.append_error(str(e), self.pos)
        return not self.errors

    def name(self):
        return self._name


class AttributesInfo(ListEntry):
    def __init__(self, f):
        super().__init__(AttributeInfo, f)
        self._attributes_map = {}

    def init(self, constant_pool):
        super().init(constant_pool)
        for attribute in self.entries:
            if attribute.name():
                self._attributes_map[attribute.name()] = attribute.info
        return not self.errors

    def get_attribute(self, name):
        return self._attributes_map[name]

    def get_code(self):
        if 'Code' in self._attributes_map:
            return CodeAttribute(self._attributes_map['Code'])
        return None


class Attribute:
    def __init__(self, attribute):
        self .attribute = attribute
        self.errors = []
        self._f = BufferFile(attribute.info)

    def init(self, constant_pool):
        return True

    def name(self):
        return self.attribute.name()


class CodeAttribute(Attribute):
    class ExceptionEntry:
        def __init__(self, f):
            self.start_pc = f.read_u2()
            self.end_pc = f.read_u2()
            self.handler_pc = f.read_u2()
            self.catch_type = f.read_u2()

    def __init__(self, attribute_info):
        super().__init__(attribute_info)
        self.max_stack = self._f.read_u2()
        self.max_locals = self._f.read_u2()
        self.code_length = self._f.read_u4()
        self.code = self._f.read_buffer(self.code_length)
        self.exception_table_length = self._f.read_u2()
        self.exception_table = []
        for index in range(self.exception_table_length):
            self.exception_table.append(CodeAttribute.ExceptionEntry(self._f))
        self.attributes = AttributesInfo(self._f)
        self._name = 'Code'

    def init(self, constant_pool):
        if not self.attributes.init(constant_pool):
            self.errors += self.attributes.errors
        return not self.errors


class Deprecated(Attribute):
    pass


class Signature(Attribute):
    def __init__(self, attribute):
        super().__init__(attribute)
        self.signature_index = self._f.read_u2()

    def init(self, constant_pool):
        pass


class SyntheticAttribute(Attribute):
    pass