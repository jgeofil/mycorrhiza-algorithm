import os
import numpy as np

from sklearn.ensemble import RandomForestClassifier 

from mycorrhiza.dataset import Myco
from mycorrhiza.analysis import Result
from mycorrhiza.plotting import mixture_plot
from mycorrhiza.ml import Model
from mycorrhiza.settings import const


def main():
	myco = Myco(file_path='data/gipsy.myc')
	myco.load()

	out_path = 'data/'
	n_estimators, n_jobs = 60, 1

	result = Result(dataset=myco, out_path=out_path)

	model = Model(RandomForestClassifier, out_path, n_estimators=n_estimators, verbose=True, n_jobs=n_jobs)
	partition = model._get_partition(myco, n_cores=n_jobs)
	test_indices = [1,23,45,12]

	model.fit(partitions=partitions, populations=myco.populations, exclude_indices=test_indices)
	probabilities = model.predict_proba(partitions=partitions, include_indices=test_indices)

	classes = model.classes_
	top_class_ids = np.argmax(probabilities, axis=1)
	top_probabilities = np.max(probabilities, axis=1)
	predicted_origin = [classes[class_id] for class_id in top_class_ids]

	result.set_q_pred_pops_params(predicted_origin, top_probabilities, classes, test_indices=test_indices)
	result.output_q()

	mixture_plot(result)