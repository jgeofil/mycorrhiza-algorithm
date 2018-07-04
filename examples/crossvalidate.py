from mycorrhiza.dataset import Myco
from mycorrhiza.analysis import CrossValidate
from mycorrhiza.plotting import mixture_plot

from mycorrhiza.settings import const

const['__SPLITSTREE_PATH__'] = ''

myco = Myco('examples/gipsy.myc')
myco.load()

cv = CrossValidate(myco, 'examples/').run(n_partitions=1, n_loci=0, n_cores=4)

mixture_plot(cv)