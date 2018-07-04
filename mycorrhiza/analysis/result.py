import numpy as np
from typing import List
from ..dataset.dataset import Dataset


class Result:

	def __init__(self, dataset: Dataset, out_path):

		self._out_path = out_path
		self._q_matrix = None
		self._q_pops = None
		self._dataset = dataset
		self._pred_populations = None

	@property
	def q_matrix(self):
		return self._q_matrix

	@property
	def q_populations(self):
		return self._q_pops

	@property
	def pred_populations(self):
		return self._pred_populations

	@property
	def real_populations(self):
		return self._dataset.populations

	@property
	def identifiers(self):
		return self._dataset.identifiers

	def set_pred_pops(self, pops: List):
		self._pred_populations = pops

	def set_q(self, q: List[List]):
		self._q_matrix = np.array(q)

	def set_q_pops(self, pops: List):
		self._q_pops = pops
