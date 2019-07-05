from ..exceptions import LoadingError
import numpy as np

class Sample:

	def __init__(self, identifier: str, num_loci: int, population=None, known: bool = True):
		self._identifier = str(identifier)
		self._population = population
		self._known = known
		self._num_loci = num_loci

	@property
	def identifier(self):
		return self._identifier

	@property
	def num_loci(self):
		return self._num_loci

	@property
	def population(self):
		return self._population

	@property
	def flag(self):
		return self._known


class Dataset:

	def __init__(self, file_path, diploid: bool = True, is_str: bool = True):

		self._file_path = file_path
		self._diploid = diploid
		self._is_str = is_str
		self._samples = []
		self._num_loci = None

	def _iterator(self):
		return []

	@property
	def iterator(self):
		return self._iterator

	def _add_sample(self, sample: Sample):

		if self._num_loci is None:
			self._num_loci = sample.num_loci
		elif self._num_loci != sample.num_loci and self._num_loci is not None:
			raise LoadingError('Mismatch in the number of loci.')

		self._samples.append(sample)

	def load(self):
		self._samples = []

		for sample, genotype in self._iterator():
			self._add_sample(sample)

		self.statistics()

	def statistics(self):
		print('Loaded {0} samples with {1} loci.'.format(self.num_samples, self.num_loci))


	@property
	def num_samples(self):
		return len(self._samples)

	@property
	def num_loci(self):
		return self._num_loci

	@property
	def haploid(self):
		return not self._diploid

	@property
	def diploid(self):
		return self._diploid

	@property
	def is_str(self):
		return self._is_str

	@property
	def populations(self):
		return [sample.population for sample in self._samples]

	@property
	def identifiers(self):
		return [sample.identifier for sample in self._samples]

	@property
	def flags(self):
		return [sample.flag for sample in self._samples]

	def setSamplePopulation(self, index, population):
		self._samples[index]._population = population

	def _microsatellite_distances(self):
		matrix = np.array([x[1] for x in self._iterator()])
		distances = np.zeros([matrix.shape[0]]*2)

		for i in range(matrix.shape[0]):
			for j in range(matrix.shape[0]):
				vals = [1 if a != b else 0 for a, b in zip(matrix[i], matrix[j])
						if a != '-9' and b != '-9' and a != '000' and b != '000']
				distances[i, j] = sum(vals)/len(vals) if len(vals) != 0 else 0

		return distances
