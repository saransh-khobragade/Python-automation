import os
import glob

files = glob.glob('/Users/skhobragade/atlassian/css-xp/packages/*')
for f in files:
    os.remove(f)