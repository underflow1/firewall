import sys
import os
dir = os.path.dirname(__file__)

if len(sys.argv) > 1:
	a = open(dir+'/temp/custom_'+sys.argv[1]+'.rsc','w')
	with open(dir+'/temp/'+sys.argv[1]) as fp:
		line = fp.readline()
		while line:
			if line.find('CUSTOM') > 0:
				print(line)
				a.write(line)
			line = fp.readline()
a.close
