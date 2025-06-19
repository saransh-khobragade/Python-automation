import fnmatch
import os
import json

def findAllFiles(directory,fileType):
    matches = []
    for root, dirnames, filenames in os.walk(directory):
        for filename in fnmatch.filter(filenames,fileType ):
            matches.append(os.path.join(root, filename))
    return matches

def findAllFileWithPattern(directory):
    files = findAllFiles(directory,'package.json')
    return files

def findVersionName(path):
    try:
        hmap={}
        if len(path)!=0:
            file = open(path)
            data = json.load(file)
        if type(data) is dict:
            if "name" in data.keys():
                if "version" in data.keys():
                    hmap["name"]=data["name"]
                    hmap["version"]=data["version"]
        return hmap
    except:
        pass
    
def GetFileDetails(src):
    files1=findAllFileWithPattern(src)

    files1 = [x for x in files1 if x.count("node_modules")==1]
    
    hmap1 = {}

    for x in files1:
        hmap=findVersionName(x)
        
        if hmap is not None and  "name" in hmap.keys():
            hmap1[hmap["name"]]={
                "version":hmap["version"],
                "path":x,
            }
    return hmap1

def rootPackageJsonDependencies():
    packageJsonPath = open('/Users/skhobragade/atlassian/css-xp/package.json')
    packageJson = json.load(packageJsonPath)

    depList = set()
    for x in packageJson["dependencies"].keys():
        depList.add(x)
    for x in packageJson["devDependencies"].keys():
        depList.add(x)
    
    return depList
    

def findDependenciesDifference():
    srcHmap = GetFileDetails('/Users/skhobragade/atlassian/bolt/css-xp/node_modules')
    desHmap = GetFileDetails('/Users/skhobragade/atlassian/css-xp/node_modules')
    
    rootDepList = rootPackageJsonDependencies()
    hmap={}
    hmapMajor = {}
    hmapMinor = {}
    hmapPatch = {}

    for x in rootDepList:
    # for x in rootDepList:
        if x in srcHmap and x in desHmap:
            if srcHmap[x]["version"]!=desHmap[x]["version"]:
                
                srcVersion = srcHmap[x]["version"].split(".")
                desVersion = desHmap[x]["version"].split(".")
                
                if srcVersion[0]!=desVersion[0]:
                    hmapMajor[x]={
                        "boltVersion":srcHmap[x]["version"],
                        "boltPath":srcHmap[x]["path"],
                        "yarn3Version":desHmap[x]["version"],
                        "yarnPath":desHmap[x]["path"]
                    }
                
                elif srcVersion[1]!=desVersion[1]:
                    hmapMinor[x]={
                        "boltVersion":srcHmap[x]["version"],
                        "boltPath":srcHmap[x]["path"],
                        "yarn3Version":desHmap[x]["version"],
                        "yarnPath":desHmap[x]["path"]
                    }

                elif srcVersion[2]!=desVersion[2]:
                    hmapPatch[x]={
                        "boltVersion":srcHmap[x]["version"],
                        "boltPath":srcHmap[x]["path"],
                        "yarn3Version":desHmap[x]["version"],
                        "yarnPath":desHmap[x]["path"]
                    }
                
    hmap = {
        "majorVersions":hmapMajor,
        "minorVersions":hmapMinor,
        "patchVersions":hmapPatch
    }
                
    json_object = json.dumps(hmap, indent=4)
 
    with open("automation/changedPackage.json", "w") as outfile:
        outfile.write(json_object)
        
findDependenciesDifference()

