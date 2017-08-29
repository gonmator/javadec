#!/usr/bin/python3 -O
#  -*- coding:utf-8 -*-

import re

__author__ = 'Gonzalo Matamala'
__date__ = ''
__version__ = '0.1.0'


_CLASS_BINARY_NAME_RE = re.compile(r'([A-Za-z_$][\w$]*(?:/[A-Za-z_$][\w$]*)*)$')
_FIELD_DESCRIPTOR_RE = re.compile(r'([BCDFIJSZ])|L([\w$/]+);|\[([\w$/;[]+)$')
_METHOD_DESCRIPTOR_RE = re.compile(r'\(([\w$/;[]*)\)([\w;[/]*)$')
_PARAMETER_DESCRIPTOR_RE = re.compile(r'([BCDFIJSZ])|L([\w$/]+);|\[([\w$/;[]+)')
_RETURN_DESCRIPTOR_RE = re.compile(r'([BCDFIJSZV])|L([\w$/]+);|\[([\w$/;[]+)$')
_UNQUALIFIED_NAME_RE = re.compile(r'([A-Za-z_$][\w$]*)$')

_BASE_TYPE = {
    'B': 'byte', 'C': 'char', 'D': 'double', 'F': 'float', 'I': 'int', 'J': 'long', 'S': 'short', 'Z': 'boolean'}


class InvalidDescriptor(Exception):
    def __init__(self, message, descriptor):
        super().__init__(message=message, descriptor=descriptor)


def check_binary_name(name):
    return bool(_CLASS_BINARY_NAME_RE.match(name))


def check_field_descriptor(descriptor):
    m = _FIELD_DESCRIPTOR_RE.match(descriptor)
    if not m:
        return False
    if m.group(2):
        return check_binary_name(m.group(2))
    if m.group(3):
        return check_field_descriptor(m.group(3))
    return True


def check_parameters_descriptor(descriptor):
    m = _PARAMETER_DESCRIPTOR_RE.match(descriptor)
    while m:
        if m.group(2) and not check_binary_name(m.group(2)):
            return False
        if m.group(3) and not check_field_descriptor(m.group(3)):
            return False
        descriptor = descriptor[m.end(0):]
        m = _PARAMETER_DESCRIPTOR_RE.match(descriptor)
    return not descriptor


def check_return_descriptor(descriptor):
    m = _RETURN_DESCRIPTOR_RE.match(descriptor)
    if not m:
        return False
    if m.group(2):
        return check_binary_name(m.group(2))
    if m.group(3):
        return check_field_descriptor(m.group(3))
    return True


def check_method_descriptor(descriptor):
    m = _METHOD_DESCRIPTOR_RE.match(descriptor)
    if not m:
        return False
    return check_parameters_descriptor(m.group(1)) and check_return_descriptor(m.group(2))


def check_unqualified_name(name):
    return bool(_UNQUALIFIED_NAME_RE.match(name))


def name_from_binary_name(binary_name):
    return binary_name.replace('/', '.')


def parse_field_type_descriptor(descriptor):
    m = _FIELD_DESCRIPTOR_RE.match(descriptor)
    if not m:
        raise InvalidDescriptor('Invalid field type', descriptor)
    if m.group(1):
        return _BASE_TYPE[m.group(1)]
    if m.group(2):
        return name_from_binary_name(m.group(2))
    if m.group(3):
        return parse_field_type_descriptor(m.group(3)) + '[]'
    raise InvalidDescriptor('Invalid field type', descriptor)


def parse_parameters_descriptor(descriptor):
    parameters = []
    m = _PARAMETER_DESCRIPTOR_RE.match(descriptor)
    while m:
        if m.group(1):
            parameters.append(_BASE_TYPE[m.group(1)])
        elif m.group(2):
            parameters.append(name_from_binary_name(m.group(2)))
        elif m.group(3):
            parameters.append(parse_field_type_descriptor(m.group(3)) + '[]')
        else:
            raise InvalidDescriptor('invalid parameter', descriptor)
        descriptor = descriptor[m.end(0):]
        m = _PARAMETER_DESCRIPTOR_RE.match(descriptor)
    return '(' + ', '.join(parameters) + ')'


def parse_return_descriptor(descriptor):
    if descriptor == 'V':
        return 'void'
    return parse_field_type_descriptor(descriptor)


def parse_method_descriptor(descriptor):
    m = _METHOD_DESCRIPTOR_RE.match(descriptor)
    if not m:
        raise InvalidDescriptor('invalid MethodDescriptor', descriptor)
    parameters_sign = parse_parameters_descriptor(m.group(1))
    return_sign = parse_return_descriptor(m.group(2))
    return parameters_sign, return_sign


def unqualify_name(q_name):
    last_period = q_name.rfind('.')
    if last_period == -1:
        return q_name
    return q_name[last_period + 1:]
