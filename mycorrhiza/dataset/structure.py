from .dataset import Sample
from ..exceptions import LoadingError
from .dataset import Dataset

DNA_INT = {'0': 'A'}

class Structure(Dataset):
	"""Structure formatted file reader.

		Args:
			file_path (str): Path to the file containing the data.
			diploid (bool): Dilpoid genotypes occupy 2 rows.
			n_optional_cols (int): Number of columns to ignore after the third column.
			missing: Representation of missing data.

	"""

	def __init__(self, file_path:str, diploid: bool=True, n_optional_cols: int=0, missing='-9'):

		super().__init__(file_path, diploid)

		if n_optional_cols < 0:
			raise ValueError('Number of optional columns must be greater than zero.')
		self._n_optional_cols = n_optional_cols

		self._alpha = {}

	def _iterator(self):
		with open(self._file_path) as fin:
			for line in fin:

				line_a = line.strip().split()

				if self._diploid:
					line_b = fin.readline().strip().split()
					if len(line_a) != len(line_b):
						raise LoadingError('Diploid loci count mismatch for sample {0}.'.format(line_a[0]))

				geno_a = self._replace_missing(line_a[3+self._n_optional_cols:])
				geno_b = self._replace_missing(line_b[3+self._n_optional_cols:]) if self._diploid else []

				yield Sample(line_a[0], len(geno_a), population=line_a[1], known=bool(line_a[2])), geno_a + geno_b

	def _replace_missing(self, l, f='N', t='-9'):
		return [f if x == t else ['A', 'T', 'G', 'C'][int(x)] for x in l]


if __name__ == '__main__':
	pass