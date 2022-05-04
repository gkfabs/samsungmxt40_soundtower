import unittest

from samsungmxt40 import SamsungMXT40

class SamsungMXT40TestCase(unittest.TestCase):

    def test_rshift(self):
        """Test rshift 10 >> 2"""
        result = SamsungMXT40.rshift(10, 2)
        self.assertEqual(result, 2)

    def test_print2HexString(self):
        """Test print2HexString 10 2"""
        result = SamsungMXT40.print2HexString(10, 2)
        self.assertEqual(result, "00A2")

    def test_printHexString(self):
        """Test printHexString 10, 5, 12, 4"""
        result = SamsungMXT40.printHexString([10, 5, 12, 4])
        self.assertEqual(result, ['0A', '05', '0C', '04'])

    def test_getCheckSum(self):
        """Test getCheckSum 10, 3, 5, 6, [45, 54, 20]"""
        result = SamsungMXT40.getCheckSum(10, 3, 5, 6, [45, 54, 20])
        self.assertEqual(result, -113)

    def test_byteToInt(self):
        """Test byteToInt 23,48"""
        result = SamsungMXT40.byteToInt(23, 48)
        self.assertEqual(result, 5936)

    def test_getPayloadData(self):
        """Test getPayloadData [10, 2, 1, 7, 78, 12, 32, 85]"""
        result = SamsungMXT40.getPayloadData([10, 2, 1, 7, 78, 12, 32, 85])
        self.assertEqual(result, [32, 85])

    def test_splitCommand(self):
        """Test splitCommand []"""
        result = SamsungMXT40.splitCommand([45, 87, 35])
        self.assertEqual(result, [[45, 87, 35]])


if __name__ == '__main__':
    unittest.main()
