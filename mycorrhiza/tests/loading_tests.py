import unittest
from mycorrhiza.load.myco import Myco


class TestLoaderMyco(unittest.TestCase):

	def test_gipsy_file(self):

		myco = Myco('tests/examples/gipsy.myc')
		myco.load()
		self.assertEqual(myco.num_samples, 90)
		self.assertEqual(myco.num_loci, 2327)


if __name__ == '__main__':
	unittest.main()
