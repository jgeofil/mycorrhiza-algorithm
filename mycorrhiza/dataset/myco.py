from .dataset import Sample
from ..exceptions import LoadingError
from .dataset import Dataset

class Myco(Dataset):
	"""Mycorrhiza formatted file reader.

	Args:
		file_path (str): Path to the file containing the data.
		diploid (bool): Dilpoid genotypes occupy 2 rows.
	"""

	def __init__(self, file_path, diploid: bool=True):

		super().__init__(file_path, diploid)

	def _iterator(self):
		with open(self._file_path) as fin:
			for line in fin:

				line_a = line.strip().split()

				if self._diploid:
					line_b = fin.readline().strip().split()
					if len(line_a) != len(line_b):
						raise LoadingError('Diploid loci count ({0},{1}) mismatch for sample {2}.'
										   .format(len(line_a), len(line_b), line_a[0]))

				geno_a = line_a[3:]
				geno_b = line_b[3:] if self._diploid else []

				yield Sample(line_a[0], len(geno_a), population=line_a[1], known=bool(line_a[2])), geno_a + geno_b


if __name__ == '__main__':
	pass