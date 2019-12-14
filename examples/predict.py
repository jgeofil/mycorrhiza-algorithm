import os
import numpy as np

from sklearn.ensemble import RandomForestClassifier

from mycorrhiza.ml import Model
from mycorrhiza.dataset import vcf_to_structure, Structure
from mycorrhiza.helper import file_to_list
from mycorrhiza.settings import const

def main():
	'''
	Real world train-predict pipeline example.
	
	Note:
		Use the same file (as an example) for both source and test files.
		Ignore population for test file.
	'''
	vcf_filepath = 	"examples/data/gipsy.vcf"
	source_population_filepath = "examples/data/gipsy.pop"
	service_folder = "examples/data/gipsy"
	source_vcf_str_filepath = os.path.join(service_folder, "source.gipsy.str")
	populations = file_to_list(source_population_filepath)
	test_vcf_str_filepath = os.path.join(service_folder, "test.gipsy.str")
	result_filepath = os.path.join(service_folder, "prediction.csv")
	
	# create folder for structure files
	os.makedirs(service_folder, exist_ok = True)

	# create subfolder for internal myco processes (might be integrated into pipeline)
	temp_service_folder = os.path.join(service_folder, "temp")
	os.makedirs(temp_service_folder, exist_ok = True)

	# obtain structure files to work with
	vcf_to_structure(vcf_filepath, source_vcf_str_filepath, populations)
	vcf_to_structure(vcf_filepath, test_vcf_str_filepath)

	source_dataset = Structure(source_vcf_str_filepath)
	test_dataset = Structure(test_vcf_str_filepath)

	model = Model(RandomForestClassifier, temp_service_folder,
					n_estimators=60, verbose=True, n_jobs=4)

	# Generate partitions in advance
	source_partition = model._get_partition(source_dataset, n_cores = 4)
	test_partition = model._get_partition(test_dataset, n_cores = 4)
	# Train
	model.fit(partitions=source_partition, populations=populations )
	# Test
	probabilities = model.predict_proba(partitions=test_partition)
	classes = model.classes_

	top_class_ids = np.argmax(probabilities, axis=1)
	top_probabilities = np.max(probabilities, axis=1)
	top_classes = [classes[class_id] for class_id in top_class_ids]

	# Output prediction result as a csv file with samples in the same order as in test VCF file.
	# First line is reserved for Column headers: Label and Probability
	with open(result_filepath, 'w') as file:
		_=file.write("Label,Probability\n")
		for clazz, prob in zip(top_classes, top_probabilities):
			_=file.write( "{},{}\n".format(clazz, prob) )



if __name__ == '__main__':
    main()