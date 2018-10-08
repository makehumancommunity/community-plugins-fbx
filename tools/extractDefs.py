#!/usr/bin/python3

import sys
import os
import re

print(sys.argv)

if len(sys.argv) < 3:
    print("USAGE: extractDefs <sourcefile> <targetdirectory>\n")
    sys.exit(1)

sourcefile = sys.argv[1]
destdir = sys.argv[2]

if not os.path.exists(sourcefile):
    print("Source file " + sourcefile + " does not exist")
    sys.exit(1)

if not os.path.exists(destdir):
    print("Target directory " + destdir + " does not exist")
    sys.exist(1)

with open(sourcefile) as f:
    lines = f.readlines()

currentDefName = None
currentDefContents = ""
currentIndentation = -1
lineNumber = 0;

def findFunctionName(inputString):
    currentIndentation = indentation
    functionpart = re.sub(r'^\s+','',line)
    functionpart = functionpart.replace("def ","")
    functionname = re.sub(r'\(.*','',functionpart).strip()
    return functionname


for line in lines:
    lineNumber = lineNumber + 1
    trimmedLine = line.strip()

    if len(trimmedLine) == 0:
        currentDefContents = currentDefContents + "\n"
    else:
        indentation = -1
        m = re.search(r'[^\s]', line)
        if m:
            indentation = m.start()
        #print(str(indentation) + " " + line, end='')

        if currentDefName is None:
            if trimmedLine.startswith("def "):
                currentDefName = findFunctionName(line)
                currentIndentation = indentation
                currentDefContents = line
        else:
            if indentation > currentIndentation:
                currentDefContents = currentDefContents + line
            else:
                outName = os.path.join(destdir,currentDefName + ".py")
                with open(outName,'w') as f:
                    f.write(currentDefContents)
                if trimmedLine.startswith("def "):
                    currentDefName = findFunctionName(line)
                    currentIndentation = indentation
                    currentDefContents = line
                else:
                    currentDefName = None


if not currentDefName is None:
    outName = os.path.join(destdir,currentDefName + ".py")
    with open(outName,'w') as f:
        f.write(currentDefContents)

