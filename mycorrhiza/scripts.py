
import argparse
from mycorrhiza.dataset import Myco, Structure
from mycorrhiza.analysis import CrossValidate
from mycorrhiza.plotting import mixture_plot

from mycorrhiza.settings import const


def crossvalidate():
	parser = argparse.ArgumentParser()
	parser.add_argument('-i', '--in-file', type=str, required=True, help='Path to the input data file.')
	parser.add_argument('-o', '--out', type=str, required=True, help='Path to the output folder.')
	parser.add_argument('-P', '--partitions', type=int, default=1, help='The number of partitions (default 1).')
	parser.add_argument('-M', '--loci', type=int, default=0, help='The number of randomly selected loci (0 for all).')
	parser.add_argument('-s', '--splits', type=int, default=5, help='The number of cross-validation splits (default 5).')
	parser.add_argument('-e', '--estimators', type=int, default=60, help='Number of trees in the Random Forest classifier (default 60).')
	parser.add_argument('-c', '--cores', type=int, default=1, help='The number of cores (default 1).')
	parser.add_argument('-x', '--splitstree', type=str, default=None, help='Path to the SplitsTree executable (default PATH).')
	parser.add_argument('-f', '--format', type=str, default='myco', choices=['myco', 'struct'], help='Data file format (default myco).')

	args = parser.parse_args()
	if args.splitstree is not None:
		const['__SPLITSTREE_PATH__'] = args.splitstree

	if args.format == 'myco':
		myco = Myco(file_path=args.in_file)
	elif args.format == 'struct':
		myco = Structure(file_path=args.in_file)
	else:
		raise ValueError('Invalid format.')
	myco.load()

	cv = CrossValidate(dataset=myco, out_path=args.out)
	cv.run(n_partitions=args.partitions, n_loci=args.loci, n_splits=args.splits, n_estimators=args.estimators, n_cores=args.cores)

	mixture_plot(cv)