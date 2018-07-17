from ..dataset.dataset import Dataset
from .analysis import Result, _partition, _sup_r_forests
import numpy as np
from typing import List


class Supervised(Result):

	def __init__(self, dataset: Dataset, out_path: str):
		"""Runs Mycorrhiza with k-fold cross-validation.

		Args:
			dataset (Dataset): Dataset on which to run the analysis.
			out_path (str): Path to output folder.
		"""
		super().__init__(dataset, out_path)

	def run(self, train: List[int]=None, test: List[int]=None, n_partitions: int=1, n_loci: int=0, n_estimators: int=60, n_cores: int=1) -> Result:
		"""Run the analysis with specified parameters.

		Args:
			train (list[int]): Indices of training samples.
			test (list[int]): Indices of testing samples.
			n_partitions (int): Number of partitions in which to divide the loci sequentially.
			n_loci (int): Number of randomly selected loci to use (0 for all loci).
			n_estimators (int): Number of trees in the Random Forest classifier.
			n_cores (int): Number of cores.
		"""
		if train is None and test is None:
			train = [i for i, flag in enumerate(self._dataset.flags) if flag is True]
			test = [i for i, flag in enumerate(self._dataset.flags) if flag is False]
		elif train is not None:
			test = [i for i in range(self._dataset.num_samples) if i not in train]
		elif test is not None:
			train = [i for i in range(self._dataset.num_samples) if i not in test]

		print(train, test)

		parts = _partition(self._dataset, self._out_path, n_partitions, n_loci, n_cores)
		pred_pops, q, q_pops = _sup_r_forests(train, test, parts, self._dataset.populations, n_estimators, n_cores)

		self.set_pred_pops(pred_pops)
		self.set_q(q, q_pops)

		self.output_q()

		return self

