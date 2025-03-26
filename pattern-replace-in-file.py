import re

def track_and_replace_pattern(filePath,linetracker,pattern,replacementString):
    with open(filePath, 'r+') as file:

        lines = file.readlines()
        
        for i in range(len(lines)):
            match = re.search(linetracker, lines[i])

            if match:
                newline = re.sub(pattern, replacementString, lines[i])
                lines[i] = newline
            
        file.seek(0)
        file.truncate()
        for x in range(len(lines)):
            file.write(lines[x])
        file.close

pattern1 = r'ts-jest'
pattern2 = r'\^\d+\.\d+\.\d+'
replacementString = "^26.5.3"
track_and_replace_pattern('/Users/skhobragade/atlassian/css-xp/packages/apps/cassi/package.json',pattern1,pattern2,replacementString)