import argparse
import os
from numpy import random
from shutil import copyfile
#Randomly extract n files form a folder. This assumes a flat structure for now (TODO: recursive)

parser = argparse.ArgumentParser()
parser.add_argument("--source", type = str, help = "path to the folder from which files will be sampled")
parser.add_argument("--destination", type = str, help = "path to the folder where the data will be extracted")
parser.add_argument("--sample_size", type = int, help = "Number of images to extract")
parser.add_argument("--replace", nargs='?', type = bool, default = False, help = "Sample with or without replacement")
args = parser.parse_args()


files = [f for f in os.listdir(args.source) if os.path.isfile(os.path.join(args.source, f))]
if len(files) < args.sample_size:
    raise ValueError("Cannot extract more files than in source folder. %s contains %s files" % (args.source,len(files)))

extract_indices = random.choice(len(files),args.sample_size, replace = args.replace)

if not os.path.isdir(args.destination):
    os.makedirs(args.destination)

for i in extract_indices:
    copyfile(os.path.join(args.source,files[i]), os.path.join(args.destination,files[i]))
