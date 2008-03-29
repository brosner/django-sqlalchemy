import re
import unittest
from nose import tools
from nose.tools import *

__all__ = ['assert_instance_of', 'assert_not_instance_of', 'assert_none', 'assert_not_none'] + tools.__all__

def assert_instance_of(expected, actual, msg=None):
    """Verify that object is an instance of expected """
    assert isinstance(actual, expected), msg

def assert_not_instance_of(expected, actual, msg=None):
    """Verify that object is not an instance of expected """
    assert not isinstance(actual, expected, msg)
    
def assert_none(actual, msg=None):
    """verify that item is None"""
    assert_equal(None, actual, msg)

def assert_not_none(actual, msg=None):
    """verify that item is None"""
    assert_not_equal(None, actual, msg)