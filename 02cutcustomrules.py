import os, sys

dirsep = os.path.sep
folder = sys.path[0] + dirsep

if len(sys.argv) > 1:
	a = open(folder + '/temp/custom_' + sys.argv[1] + '.rsc','w')
	with open(folder + '/temp/' + sys.argv[1]) as fp:
		line = fp.readline()
		while line:
			if line.find('CUSTOM') > 0:
				print(line)
				a.write(line)
			line = fp.readline()
a.close
fp.close
