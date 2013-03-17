class Parser:
    def __init__(self, filename):
        self.asm_file = [line for line in open(filename)]
        self.index = 0

    def hasMoreCommands(self):
        return self.index < len(self.asm_file)

    def advance(self):
        self.index += 1

        if self.index == len(self.asm_file):
            return

        self.command = self.asm_file[self.index]
        self.command = self.removeCommentsAndSpaces(self.command)

        if not self.command:
            self.advance()

    def removeCommentsAndSpaces(self, command):
        if '//' in command:
            position = command.find('//')
            command = command[:position]

        return command.strip()

    def commandType(self):
        if self.command in ['add', 'sub', 'and', 'or', 'neg', 'not', 'gt', 'lt', 'eq']:
            return 'C_ARITHMETIC'
        elif self.command == 'return':
            return 'C_RETURN'

        first_word = self.command.split()[0]

        if first_word == 'push':
            return 'C_PUSH'
        elif first_word == 'pop':
            return 'C_POP'
        elif first_word == 'label':
            return 'C_LABEL'
        elif first_word == 'if-goto':
            return 'C_IF'
        elif first_word == 'goto':
            return 'C_GOTO'
        elif first_word == 'function':
            return 'C_FUNCTION'
        elif first_word == 'call':
            return 'C_CALL'

    def arg1(self):
        words = self.command.split()

        if len(words) == 1:
            return self.command
        else:
            return words[1]

    def arg2(self):
        words = self.command.split()

        if len(words) > 2:
            return words[2]

class CodeWriter:
    def __init__(self, filename):
        self.output = open(filename, 'w')
        self.comp_count = 0

    def setFileName(self, filename):
        self.filename = filename

    def writeArithmetic(self, command):
        binary_operations = {'add': '+', 'sub': '-', 'and': '&', 'or': '|'}
        unary_operations = {'neg': '-', 'not': '!'}
        comparison_operations = {'lt': 'JLT', 'gt': 'JGT', 'eq': 'JEQ'}

        if command in binary_operations:
            options = binary_operations
            assembly = '@SP\nM=M-1\nA=M\nD=M\n@SP\nA=M-1\nM=M%sD\n'
        elif command in unary_operations:
            options = unary_operations
            assembly = '@SP\nA=M-1\nM=%sM\n'
        elif command in comparison_operations:
            options = comparison_operations
            label = 'COMP%s' % self.comp_count
            end_label = 'ENDCOMP%s' % self.comp_count

            assembly = '@SP\nM=M-1\nA=M\nD=M\n@SP\nA=M-1\nD=M-D\n@%s\n' % label
            assembly += 'D;%s\n@SP\nA=M-1\nM=0\n'
            assembly += '@%s\n0;JMP\n' % end_label
            assembly += '(%s)\n@SP\nA=M-1\nM=-1\n(%s)\n' % (label, end_label)
            self.comp_count += 1

        text = assembly % options[command]
        self.output.write('//%s\n' % command)
        self.output.write(text)

    def writePushPop(self, command, segment, index):
        if command == 'C_PUSH':
            self.writePush(segment, index)
        elif command == 'C_POP':
            self.writePop(segment, index)

    def writePop(self, segment, index):
        SEGS = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that':
                'THAT'}

        POINTERS = {'temp': '5', 'pointer': '3'}

        if segment in SEGS:
            pointer = SEGS[segment]
            text = '@%s\n' % pointer
            text += 'D=M\n@%s\n' % index
            text += 'D=D+A\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n'
        elif segment in POINTERS:
            text = '@%s\n' % POINTERS[segment]
            text += 'D=A\n@%s\n' % index
            text += 'D=D+A\n@R13\nM=D\n@SP\nM=M-1\nA=M\nD=M\n@R13\nA=M\nM=D\n'
        elif segment == 'static':
            text = '@SP\nM=M-1\nA=M\nD=M\n@%s.%s\nM=D\n' % (self.filename, index)

        self.output.write('//%s %s %s\n' % ('POP', segment, index))
        self.output.write(text)

    def writePush(self, segment, index):
        SEGS = {'local': 'LCL', 'argument': 'ARG', 'this': 'THIS', 'that':
                'THAT'}

        POINTERS = {'temp': '5', 'pointer': '3'}

        if segment == 'constant':
            text = '@%s\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n' % index
        elif segment in SEGS:
            pointer = SEGS[segment]
            text = '@%s\n' % pointer
            text += 'D=M\n@%s\n' % index
            text += 'A=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
        elif segment in POINTERS:
            text = '@%s\n' % POINTERS[segment]
            text += 'D=A\n@%s\n' % index
            text += 'A=A+D\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
        elif segment == 'static':
            text = '@%s.%s\n' % (self.filename, index)
            text += 'D=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'

        self.output.write('//%s %s %s\n' % ('PUSH', segment, index))
        self.output.write(text)

    def writeGoto(self, label):
        text = '@%s\n0;JMP\n' % label
        self.output.write('// goto ' + label + '\n')
        self.output.write(text)

    def writeIf(self, label):
        self.output.write('// if-goto ' + label + '\n')
        text = '@SP\nM=M-1\nA=M\nD=M\n@%s\nD;JNE\n' % label
        self.output.write(text)

    def writeLabel(self, label):
        text = '(%s)\n' % label
        self.output.write('// label ' + label + '\n')
        self.output.write(text)

    def writeFunction(self, function, localVars):
        self.output.write('// function ' + function + '\n')
        self.output.write('(%s)\n' % function)

        for i in range(int(localVars)):
            self.writePush('constant', 0)
            self.writePop('local', i)

    def writeReturn(self):
        text = '//(R13)FRAME = LCL\n@LCL\nD=M\n@R13\nM=D\n'
        text += '//(R14)RET=*(FRAME-5)\n@5\nA=D-A\nD=M\n@R14\nM=D\n'
        text += '//*ARG = result\n@SP\nA=M-1\nD=M\n@ARG\nA=M\nM=D\n'
        text += '//SP=ARG+1\n@ARG\nD=M+1\n@SP\nM=D\n'
        text += '//THAT=*(FRAME-1)\n@1\nD=A\n@R13\nA=M-D\nD=M\n@THAT\nM=D\n'
        text += '//THIS=*(FRAME-2)\n@2\nD=A\n@R13\nA=M-D\nD=M\n@THIS\nM=D\n'
        text += '//ARG=*(FRAME-3)\n@3\nD=A\n@R13\nA=M-D\nD=M\n@ARG\nM=D\n'
        text += '//LCL=*(FRAME-4)\n@4\nD=A\n@R13\nA=M-D\nD=M\n@LCL\nM=D\n'
        text += '//goto RET\n@R14\nA=M\n0;JMP\n'

        self.output.write(text)

    def writeCall(self, function, numArgs):
        PUSH_ADDR = '@%s\nD=A\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
        PUSH = '@%s\nD=M\n@SP\nA=M\nM=D\n@SP\nM=M+1\n'
        return_addr = 'return_%s_%s' % (function, self.comp_count)
        self.comp_count += 1

        self.output.write('// call ' + function + '\n')
        self.output.write(PUSH_ADDR % return_addr)
        self.output.write(PUSH % 'LCL')
        self.output.write(PUSH % 'ARG')
        self.output.write(PUSH % 'THIS')
        self.output.write(PUSH % 'THAT')
        self.output.write('@SP\nD=M\n@%s\nD=D-A\n@5\nD=D-A\n@ARG\nM=D\n' % numArgs)
        self.output.write('@SP\nD=M\n@LCL\nM=D\n')
        self.writeGoto(function)
        self.output.write('(%s)\n' % return_addr)

    def writeInit(self):
        self.output.write('@256\nD=A\n@SP\nM=D\n')
        self.writeCall('Sys.init', 0)

    def close(self):
        self.output.close()

if __name__ == '__main__':
    import sys
    import os

    if len(sys.argv) == 1:
        print 'Need filename or directory'
        sys.exit(-1)

    filepath = sys.argv[1]
    files = [filepath]
    outputfile = filepath.replace('.vm', '.asm')

    if os.path.isdir(filepath):
        files = [filepath + f for f in os.listdir(filepath) if f[-3:] == '.vm']
        outputfile = filepath + filepath.strip('/').split('/')[-1] +'.asm'

    code = CodeWriter(outputfile)
    code.writeInit()

    for vmfile in files:
        parser = Parser(vmfile)
        parser.advance()

        filename = os.path.split(vmfile)[-1]
        code.setFileName(filename.replace('.vm', ''))

        while parser.hasMoreCommands():
            cmd_type = parser.commandType()

            if cmd_type == 'C_ARITHMETIC':
                code.writeArithmetic(parser.arg1())
            elif cmd_type in ['C_POP', 'C_PUSH']:
                code.writePushPop(cmd_type, parser.arg1(), parser.arg2())
            elif cmd_type == 'C_LABEL':
                code.writeLabel(parser.arg1())
            elif cmd_type == 'C_GOTO':
                code.writeGoto(parser.arg1())
            elif cmd_type == 'C_IF':
                code.writeIf(parser.arg1())
            elif cmd_type == 'C_FUNCTION':
                code.writeFunction(parser.arg1(), parser.arg2())
            elif cmd_type == 'C_RETURN':
                code.writeReturn()
            elif cmd_type == 'C_CALL':
                code.writeCall(parser.arg1(), parser.arg2())

            parser.advance()

    code.close()