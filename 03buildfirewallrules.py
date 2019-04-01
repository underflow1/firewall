import sys
import os
dir = os.path.dirname(__file__)

if len(sys.argv) > 1:
	filenames = [dir+'/firewall_base.rsc', dir+'/temp/custom_'+sys.argv[1]+'.rsc', dir+'/temp/matrix_'+sys.argv[1]+'.rsc']
	for filename in filenames:
		if os.path.exists(filename):
			print(f'filename {filename} exists')
		else:
			print(f'ERROR! filename {filename} is not exist')
			sys.exit(0)

	with open(dir+'/temp/ready_'+sys.argv[1]+'.rsc', 'w') as outfile:
		for fname in filenames:
			with open(fname) as infile:
				for line in infile:
					outfile.write(line)
