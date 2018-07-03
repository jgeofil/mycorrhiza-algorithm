
from mycorrhiza.mycorrhiza.load.myco import Myco
from mycorrhiza.mycorrhiza.analysis.crossvalidate import CrossValidate
from mycorrhiza.mycorrhiza.plotting.plotting import mixture_plot

myco = Myco('examples/gipsy.myc')
myco.load()

cv = CrossValidate(myco, 'examples/').run(n_partitions=1, n_loci=0, n_cores=4)

mixture_plot(cv)