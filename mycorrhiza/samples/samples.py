
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



