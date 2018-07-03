
from mycorrhiza.load.myco import Myco
from mycorrhiza.analysis.crossvalidate import CrossValidate
from mycorrhiza.plotting.plotting import mixture_plot
'''
from mycorrhizaloc.mycorrhiza.load.myco import Myco
from mycorrhizaloc.mycorrhiza.analysis.crossvalidate import CrossValidate
from mycorrhizaloc.mycorrhiza.plotting.plotting import mixture_plot
'''


myco = Myco('examples/gipsy.myc')
myco.load()

cv = CrossValidate(myco, 'examples/').run(n_partitions=1, n_loci=0, n_cores=4)

mixture_plot(cv)