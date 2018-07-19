
import platform
os_name = platform.system()

linux_path = 'SplitsTree'
mac_path = '/Applications/SplitsTree/SplitsTree.app/Contents/MacOS/JavaApplicationStub'

if os_name is 'Linux':
	p = linux_path
elif os_name is 'Darwin':
	p = mac_path
else:
	p = linux_path

const = {
	'__SPLITSTREE_PATH__': p
}
