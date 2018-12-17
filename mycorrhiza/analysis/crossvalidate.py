from ..dataset.dataset import Dataset
from .analysis import Result, _partition, _r_forests


class CrossValidate(Result):

	def __init__(self, dataset: Dataset, out_path: str):
		"""Runs Mycorrhiza with k-fold cross-validation.

		Args:
			dataset (Dataset): Dataset on which to run the analysis.
			out_path (str): Path to output folder.
		"""
		super().__init__(dataset, out_path)

	def run(self, n_partitions: int=1, n_loci: int=0, n_splits: int=5, n_estimators: int=60, n_cores: int=1) -> Result:
		"""Run the analysis with specified parameters.

		Args:
			n_partitions (int): Number of partitions in which to divide the loci sequentially.
			n_loci (int): Number of randomly selected loci to use (0 for all loci).
			n_splits (int): Number of cross-validation splits.
			n_estimators (int): Number of trees in the Random Forest classifier.
			n_cores (int): Number of cores.
		"""

		parts = _partition(self._dataset, self._out_path, n_partitions, n_loci, n_cores)
		pred_pops, q, q_pops = _r_forests(parts, self._dataset.populations, n_splits, n_estimators, n_cores)

		self.set_pred_pops(pred_pops)
		self.set_q(q, q_pops)

		self.output_q()
		self.output_accuracy()

		return self


