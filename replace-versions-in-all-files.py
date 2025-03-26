import os
import fnmatch
import json

import re

def track_and_replace_pattern(filePath,linetracker,version):
    with open(filePath, 'r+') as file:

        lines = file.readlines()
        versionPattern = r'\^\d+\.\d+\.\d+'
        
        for i in range(len(lines)):
            match = re.search(linetracker, lines[i])

            if match:
                newline = re.sub(versionPattern, version, lines[i])
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

def find_all_files_and_replace_versions(directory):
    files = find_all_files(directory,'package.json')
    files.append("/Users/skhobragade/atlassian/css-xp/package.json")
    
    file = open('automation/rootChangedPackage.json')
    data = json.load(file)

    # data={
    #     "minorVersions":{
    #         "type": {
    #             "boltVersion": "2.5.0",
    #             "boltPath": "/Users/skhobragade/atlassian/bolt/css-xp/node_modules/type/package.json",
    #             "yarn3Version": "2.7.2",
    #             "yarnPath": "/Users/skhobragade/atlassian/css-xp/node_modules/type/package.json"
    #         }
    #     },
    # }
  
    for x in data["minorVersions"]:
        pattern = r"\"" + re.escape(x) + r"\""
        print("changing version for",x,"to ",data["minorVersions"][x]["boltVersion"])
        for y in files:
            track_and_replace_pattern(y,pattern,data["minorVersions"][x]["boltVersion"])
    

find_all_files_and_replace_versions('/Users/skhobragade/atlassian/css-xp/packages')