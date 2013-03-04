
actions = ['PUSH', 'POP', 'ADD', 'LABEL']
location = ['CONSTANT', 'THIS', 'THAT', 'ARGUMENT']

memoryMap = {'ARGUMENT':"2", 'LOCAL' : "1", 'THIS' : "3", 'THAT' : "4", \
            'TEMP': "5", 'POINTER':"3", 'STATIC':"6"}

class VMParser():

    def __init__(self, fileName):
        self.file = open(fileName, "w")
        self.setup()

    def setup(self):
        self.file.write("@510\nD=A\n@6\nM=D\n")

    def translate(self, statement):
        if statement == "" or statement == "\n":
            return
        else:
            statement = statement.strip()
            statement = statement.upper()
            argList = statement.split(" ")

            if argList[0] == 'PUSH':
                self.evalPush(argList)
            elif argList[0] == 'POP':
                self.evalPop(argList)
            elif argList[0] == 'ADD':
                self.evalAdd(argList)
            elif argList[0] == 'LABEL':
                self.evalLabel(argList)
            elif argList[0] == 'GOTO':
                self.evalGoTo(argList)
            elif argList[0] == 'EQ':
                self.evalEq(argList)
            elif argList[0] == 'GT':
                self.evalGt(argList)
            elif argList[0] == 'LT':
                self.evalLt(argList)
            elif argList[0] == 'SUB':
                self.evalSub(argList)
            elif argList[0] == 'NEG':
                self.evalNeg(argList)
            elif argList[0] == 'AND':
                self.evalAnd(argList)
            elif argList[0] == 'OR':
                self.evalOr(argList)

    def end(self):
        self.file.write("(INFINITE_LOOP)\n@INFINITE_LOOP\n0;JMP")

    def evalPush(self, argList):
        if argList[1] == 'CONSTANT':
            self.file.write("@" + argList[2] +"\nD=A\n@SP\nM=M+1\nA=M-1\nM=D\n")
        elif argList[1] == 'POINTER':
            self.file.write("@" + argList[2] +"\nD=A\n@"+ memoryMap[argList[1]]+"\nA=D+A\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")            
        else:
            self.file.write("@" + argList[2] +"\nD=A\n@"+ memoryMap[argList[1]]+"\nA=D+M\nD=M\n@SP\nM=M+1\nA=M-1\nM=D\n")

    def evalPop(self, argList):
        if argList[1] == 'POINTER':
             self.file.write("@" + argList[2] +"\nD=A\n@"+ memoryMap[argList[1]]+"\nD=A+D\n@R15\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R15\nA=M\nM=D\n") 
        else:
            self.file.write("@" + argList[2] +"\nD=A\n@"+ memoryMap[argList[1]]+"\nD=M+D\n@R15\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R15\nA=M\nM=D\n") 

    def evalAdd(self, argList):
        self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D+M\n")

    def evalLabel (self, argList):
        self.file.write("("+arglist[1]+")\n")

    def evalGoTo(self, arglist):
        self.file.write("@" + arglist[1] + "\n0;JMP\n")

    def evalSub(self, argList):
      self.file.write("@SP\nAM=M-1\nD=M\nA=A-1\nM=D-M\n") # bottom minus top
      self.evalNeg(argList)


    def evalEq(self, argList):
        self.file.write(
            "@SP\nAM=M-1\nA=A-1\nD=D-M\nM=D\n@EQ_SETFALSE\n"
            "D;JEQ\n@0\nD=A\n@SP\nA=M-1\nM=0\n"
            "@EQ_END\n0;JMP\n"
            "(EQ_SETFALSE)\n@SP\nA=M-1\nM=M-1\n(EQ_END)\n"
            )

    def evalLt(self, argList):
        self.file.write(
            "@SP\nAM=M-1\nA=A-1\nD=D-M\nM=D\n@LT_END\nD;JGE\n"
            "@SP\nA=M-1\nM=0\n(LT_END)\n" )
    
    def evalGt(self, argList):
        self.file.write(
        "@SP\nAM=M-1\nA=A-1\nD=D-M\nM=D\n@GT_END\nD;JLE\n"
            "@SP\nA=M-1\nM=0\n(GT_END)\n")

    def evalNeg(self, argList):
        self.file.write(
            "@SP\nA=M-1\nM=!M\nM=M+1\n"
            )

    def evalAnd(self, argList):
        self.file.write(
            "@SP\nAM=M-1\nD=M\nA=A-1\nM=D&M\n"
            )

    def evalOr(self, argList):
        self.file.write(
            "@SP\nAM=M-1\nD=M\nA=A-1\nM=D|M\n"
            )