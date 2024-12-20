
#!/usr/bin/python3

def import_or_install(package):
    try:
        __import__(package)
    except ImportError:
        pip.main(['install', package])


import pysam
import collections
from pathlib import Path
import os
import argparse


parser = argparse.ArgumentParser(description='Process window params', allow_abbrev=False)
parser.add_argument('--chr', help='chromosome')
parser.add_argument('--start', help='start of window')
parser.add_argument('--end', help='end of window')
parser.add_argument('--strandness', help='0 if unstranded, 1 if forward')
parser.add_argument('--givenstrand', help='strand of gene')
parser.add_argument('--bam', help='path to bam file')
parser.add_argument('--out', help='path to output dir')
parser.add_argument('--everyPos', help='count every read position from start to end')

args = vars(parser.parse_args())
#print(args)

clippedchr = args['chr'][3:]

samfile = pysam.AlignmentFile(args['bam'], "rb")

bamreads = {}

def countReadsToPositions(pos):
	if int(args['strandness']) == 0:
		if pos not in bamreads:
			bamreads[pos] = 1
		else:
			bamreads[pos] = bamreads[pos]+1
	elif int(args['strandness']) == 1:
		strand = '+' if not r.is_reverse else '-'
		if strand == str(args['givenstrand']):
			if pos not in bamreads:
				bamreads[pos] = 1
		else:
			bamreads[pos] = bamreads[pos]+1
	elif int(args['strandness']) == 2:
		strand = '+' if not r.is_reverse else '-'
		if strand != str(args['givenstrand']):
			if pos not in bamreads:
				bamreads[pos] = 1
			else:
				bamreads[pos] = bamreads[pos]+1


reads = samfile.fetch(args['chr'], int(args['start']), int(args['end'])+1)
for r in reads:
	ar = str(r).split()
	if args['everyPos'] == "true":
		read_positions = r.get_reference_positions()
		for rp in read_positions:
			countReadsToPositions(rp)
	else:
		pos = int(ar[3])
		countReadsToPositions(pos)
    

for n in range(int(args['start']), int(args['end'])+1):
	if n not in bamreads.keys():
		bamreads[n] = 0



samfile.close()


bamname = Path(args['bam']).stem + ".counts"
of = os.path.join(str(args['out']), "counts", bamname)
if not os.path.exists(os.path.join(str(args['out']), "counts")):
	os.makedirs(os.path.join(str(args['out']), "counts"))




out = open(of, "w")
for key in sorted(bamreads):
	if key >= int(args['start']) and key <= int(args['end']):
		out.write(str(key) + "\t" + str(bamreads[key]) + "\n")
out.close()





