import sys

if sys.version_info[:2] == (2, 6):
    # Compatibility layer for Python 2.6: try loading unittest2
    try:
        import unittest2
        sys.modules['unittest'] = unittest2
    except ImportError:
        raise Exception('The test suite requires unittest2 on Python 2.6')
