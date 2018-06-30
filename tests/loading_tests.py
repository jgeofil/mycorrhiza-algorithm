import unittest
from mycorrhiza.mycorrhiza.load.myco import Myco
from mycorrhiza.mycorrhiza.analysis.crossvalidate import cross_validate

myco = Myco('examples/gipsy.myc')
myco.load()

pred_pop, mixture = cross_validate(myco, 'examples/', n_partitions=1, n_loci=0, n_cores=4)