import os
import numpy as np
from collections import Counter

from sklearn.ensemble import RandomForestClassifier 
from sklearn.model_selection import StratifiedKFold

from mycorrhiza.analysis import Result
from mycorrhiza.dataset import Myco
from mycorrhiza.dataset.helpers import _partition
from mycorrhiza.ml import Model
from mycorrhiza.plotting import mixture_plot
from mycorrhiza.settings import const

def main():
	myco = Myco(file_path='examples/data/gipsy.myc')
	myco.load()
	populations = np.array(myco.populations)
	out_path = 'data/'
	n_splits = 5
	n_estimators, n_jobs = 60, 1 # RandomForestClassifier parameters
	n_partitions, n_loci = 1, 0 # _partitions parameters

	# Check if population can be split in @n_splits splits
	counts = Counter(populations)
	for key in counts:
		if counts[key] < n_splits:
			raise ValueError("Population {0} has less samples ({1}) than the number of splits ({2}).".format(key, counts[key], num_splits))

	predicted_origin_out, mixture_estimate_out, ordering_out = [], [], []
	# As a alternative - use shortcut: Model(...)._get_partition(...)
	partitions = _partition(myco, out_path, n_partitions, n_loci, n_jobs)

	# Splits dataset with @n_splits splits where each 
	kf = StratifiedKFold(n_splits=n_splits, shuffle=True)

	# Each train/test set is near balanced split of data (label-wise)
	for train, test in kf.split(partitions[0], y=populations):
		mixture_estimates_per_partition = []
		model = Model(RandomForestClassifier, out_path,
				n_estimators=n_estimators, verbose=True,
				n_jobs=n_jobs)
		for part in partitions:
			# Train
			model.fit(partitions=part, populations=populations, include_indices=train)
			# Predict probabilities for observed classes
			mixture = model.predict_proba(partitions=part, include_indices=test)
			mixture_estimates_per_partition.append(mixture)
		
		# average the results among different trials and find predicted origins
		mixture_estimate = np.mean(mixture_estimates_per_partition, axis=0)
		predicted_origin = [model.classes_[ind] for ind in np.argmax(mixture_estimate, axis=1)]
		
		# accumulate the results
		predicted_origin_out.extend(predicted_origin)
		mixture_estimate_out.extend(mixture_estimate.tolist())
		ordering_out.extend(test.tolist())

	# find indices for smart sorting
	indices = np.argsort(ordering_out)

	# sort results according to the 
	pred_pops = np.array(predicted_origin_out)[indices]
	q = np.array(mixture_estimate_out)[indices]
	q_pops = sorted(set(populations))

	# Save data to the Result object and output data to the @out_path
	result = Result(dataset=myco, out_path=out_path)
	result.set_pred_pops(pred_pops)
	result.set_q(q, q_pops)
	result.output_q()
	result.output_accuracy()

	# Plot the results
	mixture_plot(result)

if __name__ == '__main__':
    main()
