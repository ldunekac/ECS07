"""
Luke Dunekacke
ECS07
Python version 3.2.3
DUE: 4 March 2013
This program takes hack VM and translate it to assembly
"""

import sys
from vmParser import VMParser
from jackparser import Parser

def parseFile(inputFile):
    commentParser = Parser(inputFile)
    outputFile = inputFile.split('.')[0] + ".hack"
    vmParser = VMParser(outputFile)
    
    while commentParser.hasMoreCommands():
        commentParser.advance()
        line = commentParser.output()
        vmParser.translate(line)


def main():
    if len(sys.argv) < 2:
        print("Sorry more agrs needed")
    else:
        parseFile(sys.argv[1])
	
if __name__ == '__main__':
    main()