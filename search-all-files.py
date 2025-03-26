import os
import fnmatch

def find_all_files(directory):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames, 'package.json'):
            matches.append(os.path.join(root, filename))
    return matches

# Example usage
directory = '/Users/skhobragade/atlassian/css-xp/packages'

files = find_all_files(directory)

for x in files:
    print(x)
