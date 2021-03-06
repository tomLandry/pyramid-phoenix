import unittest

from phoenix.geoform.form import BBoxValidator


def invalid_exc(func, *arg, **kw):
    from colander import Invalid
    try:
        func(*arg, **kw)
    except Invalid as e:
        return e
    else:
        raise AssertionError('Invalid not raised') # pragma: no cover


class TestBBoxValidator(unittest.TestCase):
    def test_default(self):
        validator = BBoxValidator()
        self.assertEqual(validator(None, "-180,-90,180,90"), None)

    def test_minx(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "-181,-90,180,90")
        self.assertEqual(e.msg, 'MinX out of range [-180, 180].')

    def test_miny(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "0,-91,180,90")
        self.assertEqual(e.msg, 'MinY out of range [-90, 90].')

    def test_maxx(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "0,-90,181,90")
        self.assertEqual(e.msg, 'MaxX out of range [-180, 180].')

    def test_maxy(self):
        validator = BBoxValidator()
        e = invalid_exc(validator, None, "0,-90,180,91")
        self.assertEqual(e.msg, 'MaxY out of range [-90, 90].')
