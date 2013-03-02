
import sys


def enum(**enums):
    return type('Enum',(), enums)

STATE = enum(START_STATE = 0, POSSIBLE_COMMENT = 1, LINE_COMMENT = 2, BLOCK_COMMENT = 3, END_BLOCK = 4 )

class Parser():

    def __init__(self, inputFileName=None):
        self.fileName = inputFileName
        if self.fileName == None:
            print("No file was given!")
            sys.exit()
        try:
            self.file = open(self.fileName, "r")
        except:
            raise IOError

        self.currentLine = ""
        self.lines = 0
        self.chars = 0
        self.blockComm = 0
        self.blockChars = 0
        self.EOLComm = 0
        self.EOLChars = 0
        self.state = STATE.START_STATE
        self.EOF = False

    def hasMoreCommands(self):
        """ Returns true if there are more lines to read in the file"""
        if self.EOF:
            self.file.close()
        return not self.EOF


    def advance(self):
        """ Assigns the next line of the file to the current line"""
        self.currentLine = self.file.readline()
        if not self.currentLine:
            self.EOF = True
        else:
            self.lines = self.lines + 1

    def output(self):
        """ returns the string that will be outputed to the file"""
        if self.EOF:
            return ""
        strippedLine = ""
        for char in self.currentLine:
            self.chars = self.chars + 1
            strippedLine += self.parseChar(char)
        return strippedLine

    def parseChar(self, char):
        if self.state == STATE.START_STATE:
            return self.parseStartState(char)
        elif self.state == STATE.POSSIBLE_COMMENT:
            return self.parsePossibleComment(char)
        elif self.state == STATE.LINE_COMMENT:
            return self.parseLineComment(char)
        elif self.state == STATE.BLOCK_COMMENT:
            return self.parseBlockComment(char)
        elif self.state == STATE.END_BLOCK:
            return self.parseEndBlock(char)
        else:
            print("self.STATE not Reconized")
            sys.exit()

    def parseStartState(self, char):
        if char == "/":
            self.state = STATE.POSSIBLE_COMMENT
            return ""
        else:
            return char

    def parsePossibleComment(self, char):
        if char == "/":
            self.EOLComm = self.EOLComm + 1
            self.EOLChars = self.EOLChars + 2
            self.state = STATE.LINE_COMMENT
            return ""
        elif char == "*":
            self.blockComm = self.blockComm + 1
            self.blockChars = self.blockChars + 2
            self.state = STATE.BLOCK_COMMENT
            return ""
        else:
            self.state = STATE.START_STATE
            return "/" + char

    def parseLineComment(self, char):
        self.EOLChars = self.EOLChars + 1
        if char == "\n":
            self.state = STATE.START_STATE
            return "\n"
        else:
            return ""

    def parseBlockComment(self, char):
        self.blockChars = self.blockChars + 1
        if char == "*":
            self.state = STATE.END_BLOCK
        return ""

    def parseEndBlock(self, char):
        self.blockChars = self.blockChars + 1
        if char == "*":
            return ""
        elif char == "/":
            self.state = STATE.START_STATE
            return ""
        else:
            self.state = STATE.BLOCK_COMMENT
            return ""

    def stats(self):
        print ("File Name\t" + self.fileName)
        print ("Lines:\t\t" + str(self.lines))
        print ("Chars: \t\t" + str(self.chars))
        print ("Block Comments: " + str(self.blockComm))
        print ("   Chars: \t" + str(self.blockChars))
        print ("EOL Comments:\t" + str(self.EOLComm))
        print ("   EOL Chras:\t" + str(self.EOLChars))

