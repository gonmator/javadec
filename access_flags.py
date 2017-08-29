#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

__author__ = 'Gonzalo Matamala'
__date__ = ''
__version__ = '0.1.0'


ACC_PUBLIC = 0x0001
ACC_PRIVATE = 0x0002
ACC_PROTECTED = 0x0004
ACC_STATIC = 0x0008
ACC_FINAL = 0x0010
ACC_SUPER = 0x0020
ACC_SYNCHRONIZED = 0x0020
ACC_BRIDGE = 0x0040
ACC_VOLATILE = 0x0040
ACC_TRANSIENT = 0x0080
ACC_VARARSGS = 0x0080
ACC_NATIVE = 0x0100
ACC_INTERFACE = 0x0200
ACC_ABSTRACT = 0x0400
ACC_STRICT = 0x0800
ACC_SYNTHETIC = 0x1000
ACC_ANNOTATION = 0x2000
ACC_ENUM = 0x4000


_ACC_FLAGS = { 'ACC_PUBLIC': 'public', 'ACC_PRIVATE': 'private', 'ACC_PROTECTED': 'protected', 'ACC_STATIC': 'static',
               'ACC_FINAL': 'final', 'ACC_SUPER': 'super', 'ACC_SYNCHRONIZED': 'synchronized', 'ACC_BRIDGE': 'bridge',
               'ACC_VOLATILE': 'volatile', 'ACC_TRANSIENT': 'transient', 'ACC_VARARSGS': 'vararsgs',
               'ACC_NATIVE': 'native', 'ACC_INTERFACE': 'interface', 'ACC_ABSTRACT': 'abstract', 'ACC_STRICT': 'strict',
               'ACC_SYNTHETIC': 'synthetic', 'ACC_ANNOTATION': 'annotation', 'ACC_ENUM': 'enum' }


class InvalidFlags(Exception):
    def __init__(self, message, flags):
        super().__init__(message=message, flags=flags, descriptor='{:4x}'.format(flags))


class AccessFlags:
    def __init__(self, f, flag_map):
        self.flags = f.read_u2()
        self.flag_map = flag_map
        self._signature = None

    def init(self):
        pass

    def signature(self):
        if self._signature is None:
            self._calc_signature()
        return self._signature

    def _calc_signature(self):
        return

    def _check_exclusive_flags(self, exclusive_flags):
        for i, flag_i in enumerate(exclusive_flags):
            for flag_j in exclusive_flags[i+1:]:
                if (self.flags & flag_i) and (self.flags & flag_j):
                    raise InvalidFlags('{} and {} simultaneous flags is invalid'.format(self.flag_map[flag_i],
                                                                                        self.flag_map[flag_j]),
                                       self.flags)

    def _check_implied_flags(self, implying_flag, implied_flags):
        for flag in implied_flags:
            if (self.flags & implying_flag) and not (self.flags & flag):
                raise InvalidFlags('{} flag present but not {} flag'.format(self.flag_map[implying_flag],
                                                                            self.flag_map[flag]),
                                   self.flags)

    def _check_implied_not_flags(self, implying_not_flag, implied_not_flags):
        for flag in implied_not_flags:
            if (self.flags & implying_not_flag) and (self.flags & flag):
                raise InvalidFlags('{} flag not compatible with {} flag'.format(self.flag_map[implying_not_flag],
                                                                                self.flag_map[flag]),
                                   self.flags)

    def _check_incompatible_flags(self, flag_tocheck, incompatible_flags):
        for flag in incompatible_flags:
            if (self.flags & flag_tocheck) and (self.flags & flag):
                raise InvalidFlags('{} flag is incompatible with {} flag'.format(self.flag_map[flag],
                                                                                 self.flag_map[flag_tocheck]),
                                   self.flags)

    def _check_mandatory_flags(self, flags):
        for flag in flags:
            if not (self.flags & flag):
                raise InvalidFlags('{} flag is mandatory'.format(self.flag_map[flag]))

    def _check_not_allowed_flags(self, no_flags):
        for flag in no_flags:
            if self.flags & flag:
                raise InvalidFlags('{} flag is not allowed'.format(self.flag_map[flag]))

    def _get_signatures(self, mask=0xffff):
        flag_signatures = []
        for flag in self.flag_map:
            if self.flags & mask & flag:
                flag_signatures.append(_ACC_FLAGS[self.flag_map[flag]])
        return flag_signatures

    def _is_annotation(self):
        return self.flags & ACC_ANNOTATION

    def _is_abstract(self):
        return self.flags & ACC_ABSTRACT

    def _is_bridge(self):
        return self.flags & ACC_BRIDGE

    def _is_enum(self):
        return self.flags & ACC_ENUM

    def _is_final(self):
        return self.flags & ACC_FINAL

    def _is_interface(self):
        return self.flags & ACC_INTERFACE

    def _is_native(self):
        return self.flags & ACC_NATIVE

    def _is_public(self):
        return self.flags & ACC_PUBLIC

    def _is_private(self):
        return self.flags & ACC_PRIVATE

    def _is_protected(self):
        return self.flags & ACC_PROTECTED

    def _is_static(self):
        return self.flags & ACC_STATIC

    def _is_strict(self):
        return self.flags & ACC_STRICT

    def _is_super(self):
        return self.flags & ACC_SUPER

    def _is_synchronized(self):
        return self.flags & ACC_SYNCHRONIZED

    def _is_synthetic(self):
        return self.flags & ACC_SYNTHETIC

    def _is_transient(self):
        return self.flags & ACC_TRANSIENT

    def _is_varargs(self):
        return self.flags & ACC_VARARSGS

    def _is_volatile(self):
        return self.flags & ACC_VOLATILE

    def _set_signature(self, mask):
        self._signature = ' '.join(self._get_signatures(mask))


class ClassAccessFlags(AccessFlags):
    _FLAG_MAP = {0x0001: 'ACC_PUBLIC', 0x0010: 'ACC_FINAL', 0x0020: 'ACC_SUPER', 0x0200: 'ACC_INTERFACE',
                 0x0400: 'ACC_ABSTRACT', 0x1000: 'ACC_SYNTHETIC', 0x2000: 'ACC_ANNOTATION', 0x4000: 'ACC_ENUM'}

    def __init__(self, f):
        super().__init__(f, ClassAccessFlags._FLAG_MAP)

    def init(self):
        self._check_implied_flags(ACC_INTERFACE, [ACC_ABSTRACT])
        self._check_implied_not_flags(ACC_INTERFACE, [ACC_FINAL, ACC_SUPER, ACC_ENUM])
        self._check_implied_flags(ACC_ANNOTATION, [ACC_INTERFACE])
        self._check_exclusive_flags([ACC_FINAL, ACC_ABSTRACT])

    def is_class(self):
        return not self._is_interface()

    def is_interface(self):
        return self._is_interface()

    def _calc_signature(self):
        self._set_signature(0x4411)
        if self._is_interface():
            self._signature += ' interface'
        else:
            self._signature += ' class'


class FieldAccessFlags(AccessFlags):
    _FLAG_MAP = {0x0001: 'ACC_PUBLIC', 0x0002: 'ACC_PRIVATE', 0x0004: 'ACC_PROTECTED', 0x0008: 'ACC_STATIC',
                 0x0010: 'ACC_FINAL', 0x0040: 'ACC_VOLATILE', 0x0080: 'ACC_TRANSIENT', 0x1000: 'ACC_SYNTHETIC',
                 0x4000: 'ACC_ENUM'}

    def __init__(self, f):
        super().__init__(f, FieldAccessFlags._FLAG_MAP)

    def init(self, is_interface):
        self._check_exclusive_flags([ACC_PUBLIC, ACC_PRIVATE, ACC_PROTECTED])
        self._check_exclusive_flags([ACC_FINAL, ACC_VOLATILE])
        if is_interface:
            self._check_mandatory_flags([ACC_PUBLIC, ACC_STATIC, ACC_FINAL])
            self._check_not_allowed_flags([ACC_PRIVATE, ACC_PROTECTED, ACC_VOLATILE, ACC_ENUM])

    def _calc_signature(self):
        self._set_signature(0x50df)


class MethodAccessFlags(AccessFlags):
    _FLAG_MAP = {0x0001: 'ACC_PUBLIC', 0x0002: 'ACC_PRIVATE', 0x0004: 'ACC_PROTECTED', 0x0008: 'ACC_STATIC',
                 0x0010: 'ACC_FINAL', 0x0020: 'ACC_SYNCHRONIZED', 0x0040: 'ACC_BRIDGE', 0x0080: 'ACC_VARARSGS',
                 0x0100: 'ACC_NATIVE', 0x0400: 'ACC_ABSTRACT', 0x0800: 'ACC_STRICT', 0x1000: 'ACC_SYNTHETIC'}

    def __init__(self, f):
        super().__init__(f, MethodAccessFlags._FLAG_MAP)

    def init(self, is_interface, is_initialization):
        self._check_exclusive_flags([ACC_PUBLIC, ACC_PRIVATE, ACC_PROTECTED])
        if is_interface:
            self._check_not_allowed_flags([ACC_PROTECTED, ACC_FINAL, ACC_SYNCHRONIZED, ACC_NATIVE])
        self._check_implied_not_flags(ACC_ABSTRACT,
                                      [ACC_PRIVATE, ACC_STATIC, ACC_FINAL, ACC_SYNCHRONIZED, ACC_NATIVE, ACC_STRICT])
        if is_initialization:
            self._check_not_allowed_flags([ACC_FINAL, ACC_SYNCHRONIZED, ACC_BRIDGE, ACC_NATIVE, ACC_ABSTRACT])

    def _calc_signature(self):
        self._set_signature(0x1d3f)
