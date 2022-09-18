import unittest

from .cover import IqtecCover


class TestTiltEncode(unittest.TestCase):
    def test_open(self):
        assert IqtecCover.encode_tilt(100) == 0

    def test_close(self):
        assert IqtecCover.encode_tilt(0) == 180

    def test_half(self):
        assert IqtecCover.encode_tilt(50) == 90


class TestTiltDecode(unittest.TestCase):
    def test_open(self):
        assert IqtecCover.decode_tilt(0) == 100

    def test_closed(self):
        assert IqtecCover.decode_tilt(180) == 0

    def test_half(self):
        assert IqtecCover.decode_tilt(90) == 50


class TestPositionEncode(unittest.TestCase):
    def test_open(self):
        assert IqtecCover.encode_position(100) == 0

    def test_close(self):
        assert IqtecCover.encode_position(0) == 1000

    def test_half(self):
        assert IqtecCover.encode_position(50) == 500


class TestPositionDecode(unittest.TestCase):
    def test_open(self):
        assert IqtecCover.decode_position(0) == 100

    def test_close(self):
        assert IqtecCover.decode_position(1000) == 0

    def test_half(self):
        assert IqtecCover.decode_position(500) == 50


if __name__ == '__main__':
    unittest.main()
