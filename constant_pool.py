#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

from common import *
from signatures import check_binary_name, name_from_binary_name, unqualify_name

__author__ = 'Gonzalo Matamala'
__date__ = ''
__version__ = '0.1.0'


CONSTANT_CLASS = 7
CONSTANT_DOUBLE = 6
CONSTANT_FIELDREF = 9
CONSTANT_FLOAT = 4
CONSTANT_INTEGER = 3
CONSTANT_INTERFACE_METHODREF = 11
CONSTANT_INVOKE_DYNAMIC = 18
CONSTANT_LONG = 5
CONSTANT_METHOD_HANDLE = 15
CONSTANT_METHOD_TYPE = 16
CONSTANT_METHODREF = 10
CONSTANT_NAME_AND_TYPE = 12
CONSTANT_STRING = 8
CONSTANT_UTF8 = 1


class ConstantPoolEntry(BaseEntry):
    def __init__(self, tag, f):
        super().__init__(f)
        self.tag = tag
        self.pos -= 1

    def init(self, constant_pool):
        return True

    def value(self):
        return None


class ConstantUnusable(ConstantPoolEntry):
    def __init__(self, tag, f):
        super().__init__(tag, f)


class ConstantRefInfo(ConstantPoolEntry):
    def __init__(self, tag, f):
        super().__init__(tag, f)
        self.class_index = f.read_u2()
        self.name_and_type_index = f.read_u2()


class Constant4BytesNumeric(ConstantPoolEntry):
    def __init__(self, tag, f):
        super().__init__(tag, f)
        self.bytes = f.read_u4()


class Constant8BytesNumeric(ConstantPoolEntry):
    def __init__(self, tag, f):
        super().__init__(tag, f)
        self.high_bytes = f.read_u4()
        self.low_bytes = f.read_u4()


class ConstantClassInfo(ConstantPoolEntry):
    def __init__(self, f):
        super().__init__(CONSTANT_CLASS, f)
        self.name_index = f.read_u2()
        self._name = None
        self._unqualified_name = None

    def init(self, constant_pool):
        try:
            name = constant_pool.get_utf8(self.name_index)
            if not check_binary_name(name):
                self.append_error('invalid class\' binary name {}'.format(self.name), self.pos)
            self._name = name_from_binary_name(name)
            self._unqualified_name = unqualify_name(self._name)
        except ValueError as e:
            self.append_error(str(e), self.pos + 1)

    def name(self):
        return self._name

    def unqualified_name(self):
        return self._unqualified_name


class ConstantFieldrefInfo(ConstantRefInfo):
    def __init__(self, f):
        super().__init__(CONSTANT_FIELDREF, f)


class ConstantMethodrefInfo(ConstantRefInfo):
    def __init__(self, f):
        super().__init__(CONSTANT_METHODREF, f)


class ConstantInterfaceMethodrefInfo(ConstantRefInfo):
    def __init__(self, f):
        super().__init__(CONSTANT_INTERFACE_METHODREF, f)


class ConstantStringInfo(ConstantPoolEntry):
    def __init__(self, f):
        super().__init__(CONSTANT_STRING, f)
        self.string_index = f.read_u2()


class ConstantIntegerInfo(Constant4BytesNumeric):
    def __init__(self, f):
        super().__init__(CONSTANT_INTEGER, f)


class ConstantFloatInfo(Constant4BytesNumeric):
    def __init__(self, f):
        super().__init__(CONSTANT_FLOAT, f)


class ConstantLongInfo(Constant8BytesNumeric):
    def __init__(self, f):
        super().__init__(CONSTANT_LONG, f)


class ConstantDoubleInfo(Constant8BytesNumeric):
    def __init__(self, f):
        super().__init__(CONSTANT_DOUBLE, f)


class ConstantNameAndTypeInfo(ConstantPoolEntry):
    def __init__(self, f):
        super().__init__(CONSTANT_NAME_AND_TYPE, f)
        self.name_index = f.read_u2()
        self.descriptor_index = f.read_u2()


class ConstantUtf8_Info(ConstantPoolEntry):
    def __init__(self, f):
        super().__init__(CONSTANT_UTF8, f)
        self.length = f.read_u2()
        self.bytes = f.read_buffer(self.length)
        self._value = ''

    def init(self, constant_pool):
        i = 0
        while i < self.length:
            c = self.bytes[i]
            i += 1
            if c == 0:
                self._set_error(c, i)
            elif c < 0x80:
                self._value += chr(c)
            elif c < 0xc0:
                self._set_error(c, i)
            elif c < 0xe0:
                c2 = self.bytes[i]
                i += 1
                if c2 < 0x80 or c2 >= 0xc0:
                    self._set_error(c2, i)
                else:
                    self._value += chr(((c & 0x1f) << 6) + (c2 & 0x3f))
            elif c < 0xf0:
                c2 = self.bytes[i]
                i += 1
                if c2 < 0x80 or c2 >= 0xc0:
                    self._set_error(c2, i)
                else:
                    c3 = self.bytes[i]
                    i += 1
                    if c3 < 0x80 or c3 >= 0xc0:
                        self._set_error(c3, i)
                    else:
                        self._value += chr(((c & 0xf) << 12) + ((c2 & 0x3f) << 6) + (c3 & 0x3f))
            else:
                self._set_error(c, i)
        return not self.errors

    def value(self):
        return self._value

    def _set_error(self, c, i):
        self.append_error('invalid byte 0x{:2x}'.format(c), self.pos + 3 + i)


class ConstantMethodHandleInfo(ConstantPoolEntry):
    def __init__(self, f):
        super().__init__(CONSTANT_METHOD_HANDLE, f)
        self.reference_kind = f.read_u2()
        self.reference_index = f.read_u2()


class ConstantMethodTypeInfo(ConstantPoolEntry):
    def __init__(self, f):
        super().__init__(CONSTANT_METHOD_TYPE, f)
        self.descriptor_index = f.read_u2()


class ConstantInvokeDynamicInfo(ConstantPoolEntry):
    def __init__(self, f):
        super().__init__(CONSTANT_INVOKE_DYNAMIC, f)
        self.bootstrap_method_attr_index = f.read_u2()
        self.name_and_type_index = f.read_u2()


class ConstantPool(BaseEntry):
    def __init__(self, f):
        super().__init__(f)
        self.constant_pool_count = f.read_u2()
        self.constant_pool = []
        self.class_indexes = []
        self.invoke_dynamic_indexes = []
        self.method_handle_indexes = []
        self.method_type_indexes = []
        self.name_and_type_indexes = []
        self.numeric_indexes = []
        self.ref_indexes = []
        self.utf8_indexes = []
        self.string_indexes = []
        index = 1
        while index < self.constant_pool_count:
            tag = f.read_u1()
            if tag == CONSTANT_CLASS:
                self.constant_pool.append(ConstantClassInfo(f))
                self.class_indexes.append(index)
            elif tag == CONSTANT_FIELDREF:
                self.constant_pool.append(ConstantFieldrefInfo(f))
                self.ref_indexes.append(index)
            elif tag == CONSTANT_METHODREF:
                self.constant_pool.append(ConstantMethodrefInfo(f))
                self.ref_indexes.append(index)
            elif tag == CONSTANT_INTERFACE_METHODREF:
                self.constant_pool.append(ConstantInterfaceMethodrefInfo(f))
                self.ref_indexes.append(index)
            elif tag == CONSTANT_STRING:
                self.constant_pool.append(ConstantStringInfo(f))
                self.string_indexes.append(index)
            elif tag == CONSTANT_INTEGER:
                self.constant_pool.append(ConstantIntegerInfo(f))
                self.numeric_indexes.append(index)
            elif tag == CONSTANT_FLOAT:
                self.constant_pool.append(ConstantFloatInfo(f))
                self.numeric_indexes.append(index)
            elif tag == CONSTANT_LONG:
                self.constant_pool.append(ConstantLongInfo(f))
                self.constant_pool.append(ConstantUnusable(tag, f))
                self.numeric_indexes.append(index)
            elif tag == CONSTANT_DOUBLE:
                self.constant_pool.append(ConstantDoubleInfo(f))
                self.constant_pool.append(ConstantUnusable(tag, f))
                self.numeric_indexes.append(index)
            elif tag == CONSTANT_NAME_AND_TYPE:
                self.constant_pool.append(ConstantNameAndTypeInfo(f))
                self.name_and_type_indexes.append(index)
            elif tag == CONSTANT_UTF8:
                self.constant_pool.append(ConstantUtf8_Info(f))
                self.utf8_indexes.append(index)
            elif tag == CONSTANT_METHOD_HANDLE:
                self.constant_pool.append(ConstantMethodHandleInfo(f))
                self.method_handle_indexes.append(index)
            elif tag == CONSTANT_METHOD_TYPE:
                self.constant_pool.append(ConstantMethodTypeInfo(f))
                self.method_type_indexes.append(index)
            elif tag == CONSTANT_INVOKE_DYNAMIC:
                self.constant_pool.append(ConstantInvokeDynamicInfo(f))
                self.invoke_dynamic_indexes.append(index)
            else:
                self.append_error('invalid constant pool tag {}'.format(tag), f.tell() - 1)
            index = len(self.constant_pool) + 1
        self._init_indexes(self.numeric_indexes)
        self._init_indexes(self.utf8_indexes)
        self._init_indexes(self.class_indexes)
        self._init_indexes(self.method_type_indexes)
        self._init_indexes(self.name_and_type_indexes)
        self._init_indexes(self.ref_indexes)
        self._init_indexes(self.string_indexes)
        self._init_indexes(self.invoke_dynamic_indexes)
        self._init_indexes(self.method_handle_indexes)

    def __len__(self):
        return self.constant_pool_count - 1

    def at(self, index):
        if index < 1 or index >= self.constant_pool_count:
            raise IndexError()
        return self.constant_pool[index - 1]

    def get_class_name(self, index):
        if index not in self.class_indexes:
            return ValueError('index {} not refers a constant class entry'.format(index))
        return self.at(index).name()

    def get_utf8(self, index):
        if index not in self.utf8_indexes:
            raise ValueError('index {} not refers a constant utf8 entry'.format(index))
        return self.at(index).value()

    def _init_indexes(self, indexes):
        for index in indexes:
            entry = self.at(index)
            if not entry.init(self):
                self.add_errors(entry.errors)
