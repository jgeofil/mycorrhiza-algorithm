from ..samples.samples import Sample
from ..exceptions import LoadingError


class Loader:

	def __init__(self, file_path, diploid: bool=True):

		self._file_path = file_path
		self._diploid = diploid
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
	def populations(self):
		return [sample.population for sample in self._samples]


