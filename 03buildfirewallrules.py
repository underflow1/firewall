import os, sys

dirsep = os.path.sep
folder = sys.path[0] + dirsep

if len(sys.argv) > 1:
	filenames = [folder + '/firewall_base.rsc', folder + '/temp/custom_' + sys.argv[1] + '.rsc', folder + '/temp/matrix_' + sys.argv[1] + '.rsc']
	for filename in filenames:
		if os.path.exists(filename):
			print(f'filename {filename} exists')
		else:
			print(f'ERROR! filename {filename} is not exist')
			sys.exit(0)

	with open(folder + '/temp/ready_' + sys.argv[1] + '.rsc', 'w') as outfile:
		for fname in filenames:
			with open(fname) as infile:
				for line in infile:
					outfile.write(line)
			infile.close
	outfile.close
			