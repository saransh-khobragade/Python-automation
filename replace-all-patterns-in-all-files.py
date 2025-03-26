import os
import fnmatch

import re

def track_and_replace_pattern(filePath,linetracker,pattern,replacementString):
    with open(filePath, 'r+') as file:

        lines = file.readlines()
        
        for i in range(len(lines)):
            # linetracker = r'@atlaskit'
            # pattern = r'\^\d+\.\d+\.\d+'
            match = re.search(linetracker, lines[i])

            if match:
                newline = re.sub(pattern, replacementString, lines[i])
                lines[i] = newline
            
        file.seek(0)
        file.truncate()
        for x in range(len(lines)):
            file.write(lines[x])
        file.close

def find_all_files(directory,fileType):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames,fileType ):
            matches.append(os.path.join(root, filename))
    return matches

def find_all_files_and_replace_patterns(directory):
    files = find_all_files(directory,'package.json')
    pattern1 = r'ts-jest'
    pattern2 = r'\^\d+\.\d+\.\d+'
    replacementString = "^29.1.2"

    for x in files:
        track_and_replace_pattern(x,pattern1,pattern2,replacementString)

find_all_files_and_replace_patterns('/Users/skhobragade/atlassian/css-xp/packages')