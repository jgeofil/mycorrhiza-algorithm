from mycorrhiza.dataset import vcf_to_structure
from mycorrhiza.helper import file_to_list

vcf_to_structure('data/gipsy.vcf', 'data/gipsy.vcf.str', file_to_list('data/gipsy.pop'))