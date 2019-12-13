import json
from collections import OrderedDict
import re
import sys

## Define helper functions

def isIntegerPatch(patch):
    try: 
        int(patch)
        return True
    except ValueError:
        return False

def replace_dependency(version):
    # takes a dependency that is in the form a.b.c and replaces it with a.b.*
    # so that the last patch is not locked
    pattern = "v?[0-9]+\.[0-9]+\.[0-9]+"
    if(re.match(pattern, version)):
        versionsMatch = re.split("\.", version)
        if isIntegerPatch(versionsMatch[2]):
            versionsMatch[2] = '*'
            version = '.'.join(versionsMatch)
    return version

## Open files

path = sys.argv[1]

try:
    print("Fetching the composer files at path " + path)
    with open(path + "/composer.json", "r") as read_file:
        composerJson = json.load(read_file, object_pairs_hook=OrderedDict)

    with open(path + "/composer.lock", "r") as read_file:
        composerLock = json.load(read_file)
except:
    print("Missing composer.json or composer.lock file, aborting ..")
    exit(1)


## Check files are correct

if 'require' not in composerJson:
    raise Exception('Your composer.json is not valid') 

if 'packages' not in composerLock:
    raise Exception('Your composer.lock is not valid') 

for package in composerLock['packages']:
    if package['name'] in composerJson['require']:
        composerJson['require'][package['name']] = replace_dependency(package['version'])

for package in composerLock['packages-dev']:
    if package['name'] in composerJson['require-dev']:
        composerJson['require-dev'][package['name']] = replace_dependency(package['version'])


# Rewrites composer.json file

with open("safran-optronics/composer.json", "w") as write_file:
    try:
        json.dump(composerJson, write_file, indent=4, separators=(',', ': '))
        print("composer.json file was successfully written !")
    except:
        print("An error occured.")