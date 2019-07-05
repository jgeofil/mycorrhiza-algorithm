
import platform
from pathlib import Path
home = str(Path.home())
os_name = platform.system()
linux_path = home+'/splitstree4/SplitsTree'
mac_path = '/Applications/SplitsTree/SplitsTree.app/Contents/MacOS/JavaApplicationStub'
windows_path = r'cmd /c start C:\"Program Files"\SplitsTree\SplitsTree.exe'

if os_name == 'Linux':
	p = linux_path
elif os_name == 'Darwin':
	p = mac_path
elif os_name == 'Windows':
	p = windows_path
else:
	p = linux_path

const = {
	'__SPLITSTREE_PATH__': p
}
