#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

import argparse


from common import *
from constant_pool import ConstantPool
from this_class import ThisClassInfo

__author__ = 'Gonzalo Matamala'
__date__ = ''
__version__ = '0.1.0'


class ClassFileError(Exception):
    def __init__(self, message='invalid class format'):
        super().__init__(message=message)


class InvalidClassFileVersion(ClassFileError):
    def __init__(self, major_version, minor_version):
        self.major_version = major_version
        self.minor_version = minor_version
        super().__init__('invalid versions {}.{}'.format(major_version, minor_version))


class ClassFile:
    def __init__(self, class_file, ignore_invalid_format=False):
        self.errors = []

        if isinstance(class_file, JavaFile):
            self._f = class_file
        else:
            self._f = JavaFile(class_file)
        self.magic = self._f.read_u4()
        if self.magic != 0xcafebabe:
            self._append_error('invalid magic value 0x{:8X}'.format(self.magic))
        self.minor_version = self._f.read_u2()
        self.major_version = self._f.read_u2()
        if self.major_version < 45:
            self._append_error('invalid version {}.{}'.format(self.major_version, self.minor_version))
        self.constant_pool = ConstantPool(self._f)
        self.this_class = ThisClassInfo(self._f)
        if not self.this_class.init(self.constant_pool):
            self._add_errors(self.this_class.errors)

    def _append_error(self, message):
        self.errors.append((message, self._f.tell_prev()))

    def _add_errors(self, errors):
        self.errors += errors


def list_methods(class_file):
    for method in class_file.methods:
        # print(method.access_flags, method.name(), method.descriptor())
        print('\t' + method.signature())


def list_this(class_file):
    print(class_file.signature_of('this'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('class_file', type=argparse.FileType('rb'))
    parser.add_argument('-C', '--check', action='store_true')
    parser.add_argument('-S', '--signature', action='store_true')

    args = parser.parse_args()
    class_file = ClassFile(args.class_file)
    if args.check:
        for error in class_file.errors:
            print('{}: {}'.format(error(1), error(2)))
    if args.signature:
        print(class_file.this_class.signature())
