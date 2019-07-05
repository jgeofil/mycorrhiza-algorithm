from mycorrhiza.dataset import Myco, Structure
from mycorrhiza.analysis import Supervised
from mycorrhiza.plotting import mixture_plot

from mycorrhiza.settings import const

const['__SPLITSTREE_PATH__'] = 'SplitsTree'


def main():
	myco = Myco(file_path='data/gipsy.myc')
	myco.load()

	cv = Supervised(dataset=myco, out_path='data/')
	cv.run(test=[1,23,45,12], n_partitions=1, n_loci=0, n_estimators=60, n_cores=1)

	mixture_plot(cv)


if __name__ == '__main__':
    main()