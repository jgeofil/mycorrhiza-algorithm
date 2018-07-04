from mycorrhiza.dataset import Myco
from mycorrhiza.analysis import CrossValidate
from mycorrhiza.plotting import mixture_plot

from mycorrhiza.settings import const

const['__SPLITSTREE_PATH__'] = 'SplitsTree'

myco = Myco(file_path='data/gipsy.myc')
myco.load()

cv = CrossValidate(dataset=myco, out_path='data/')
cv.run(n_partitions=1, n_loci=0, n_splits=5, n_estimators=60, n_cores=1)

mixture_plot(cv)