#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-
from io import SEEK_SET, SEEK_CUR, SEEK_END

__author__ = 'Gonzalo Matamala'
__date__ = ''
__version__ = '0.1.0'


class BufferFile:
    def __init__(self, buffer, pos=0):
        self._b = buffer
        self._prev = self._p = pos

    def read_buffer(self, length):
        rv = self._b[self._p:self._p + length]
        self._prev = self._p
        self._p += length
        return rv

    def read_u1(self):
        r = self.read_buffer(1)
        rv = ord(r[0])
        return rv

    def read_u2(self):
        r = self.read_buffer(2)
        rv = ord(r[0] << 8 | r[1])
        return rv

    def read_u4(self):
        r = self.read_buffer(4)
        rv = ord(r[0] << 24 | r[1] << 16 | r[2] << 8 | r[3])
        return rv

    def seek(self, offset, whence):
        if whence == SEEK_SET:
            self._prev = self._p
            self._p = offset
        elif whence == SEEK_CUR:
            self._prev = self._p
            self._p += offset
        elif whence == SEEK_END:
            raise NotImplemented()
        else:
            raise ValueError()
        return self._p

    def tell(self):
        return self._p

    def tell_prev(self):
        return self._prev


class JavaFile:
    def __init__(self, file):
        self._f = file
        self._prev = self._f.tell()

    def read_buffer(self, length):
        self._prev = self._f.tell()
        return self._f.read(length)

    def read_u1(self):
        self._prev = self._f.tell()
        return ord(self._f.read(1))

    def read_u2(self):
        self._prev = self._f.tell()
        return ord(self._f.read(1)) << 8 | ord(self._f.read(1))

    def read_u4(self):
        self._prev = self._f.tell()
        return ord(self._f.read(1)) << 24 | ord(self._f.read(1)) << 16 | ord(self._f.read(1)) << 8 | ord(self._f.read(1))

    def seek(self, offset, whence):
        self._prev = self._f.tell()
        return self._f.seek(offset, whence)

    def tell(self):
        return self._f.tell()

    def tell_prev(self):
        return self._prev


class BaseEntry:
    def __init__(self, f=None):
        if f:
            self.pos = f.tell()
        else:
            self.pos = None
        self.errors = []

    def add_errors(self, errors):
        self.errors += errors

    def append_error(self, message, pos):
        self.errors.append((message, pos))


class ListEntry(BaseEntry):
    def __init__(self, EntryType, f):
        super().__init__(f)
        self.count = f.read_u2()
        self.entries = []
        for i in range(self.count):
            self.entries.append(EntryType(f))

    def init(self, constant_pool):
        for entry in self.entries:
            if not entry.init(constant_pool):
                self.add_errors(entry.errors)
        return not self.errors

    def at(self, index):
        return self.entries[index]
