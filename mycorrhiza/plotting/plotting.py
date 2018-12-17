from ..analysis import Result
import numpy as np
import os

import warnings
warnings.simplefilter(action='ignore', category=UserWarning)

import matplotlib as mpl
if os.environ.get('DISPLAY','') == '':
    print('no display found. Using non-interactive Agg backend')
    mpl.use('Agg')
import matplotlib.pyplot as plt

def mixture_plot(result: Result) -> None:


	q_matrix = np.array(result.q_matrix)

	colors = plt.cm.jet(np.linspace(0, 1.0, num=q_matrix.shape[1]))

	ind = np.arange(q_matrix.shape[0])  # the x locations for the groups
	width = 1

	btm = np.zeros(q_matrix.shape[0])

	fig = plt.figure(figsize=((0.1*q_matrix.shape[0])+2,5))

	ax = fig.add_axes([0.05, 0.1, 0.9, 0.7])

	for j, row in enumerate(q_matrix.T):
		ax.bar(ind, row, width, bottom=btm, color=colors[j], label=result.q_populations[j])
		btm += row

	last = result.real_populations[0]

	for k, pop in enumerate(result.real_populations):
		if pop != last:
			ax.axvline(k - 0.5, c='grey', linewidth=0.5)
		last = pop

	ax.set_xlim(-0.5, q_matrix.shape[0] - 0.5)
	ax.set_ylim(0, 1)

	ax.set_xticks(ind)
	ax.set_xticklabels(result.identifiers, rotation=90, fontsize=5)


	plt.legend(ncol=5,bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
			   mode="expand")

	ax.tick_params(axis='y', which='both', length=0)
	plt.setp(ax.get_yticklabels(), visible=False)



	#plt.show()


	plt.savefig(result._out_path+'/mixt.png', bbox_inches='tight')