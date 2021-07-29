class Parser:
    file = None
    position = None
    size = None
    current_command = None

    def __init__(self, fileName):
        with open(fileName, 'r') as file:
            self.file = file.readlines()
        self.position = -1
        self.size = len(self.file)

    def advance(self):
        self.position += 1
        self.current_command = self.file[self.position]
        if self.current_command.startswith("//") or self.current_command.startswith("\n"):
            self.advance()

    def hasMoreCommands(self):
        return self.position < self.size -1

    def commandType(self):
        for clause in ["add", "sub", "eq", "gt", "lt", "and", "or", "not", "neg"]:
            if self.current_command.startswith(clause):
                return "C_ARITHMETIC"

        if self.current_command.startswith("push"):
            return "C_PUSH"

        if self.current_command.startswith("pop"):
            return "C_POP"

    def arg1(self):
        command = self.current_command.split(' ')
        if len(command) == 1:
            return command[0][:-1]
        else:
            return ' '.join(command[:-1])

    def arg2(self):
        split_command = self.current_command.split(' ')
        last_component = split_command[-1]
        wo_newline = last_component[:-1]
        return wo_newline



class CodeWriter:
    dst = None
    linesWritten = 0
    
    def __init__(self, fileName):
        self.dst = open(fileName, 'w')

    def write(self, assembly):
        self.dst.write(assembly+'\n')
        self.linesWritten += 1

    def close(self):
        self.dst.close()

    def comment(self, command):
        self.dst.write('\n' + "//" + command)

    def writeArithmetic(self, command):
        #self.comment(command)
        if command in ("add", "sub"):
            self.writeAddSubtract(command)
        elif command in ("gt", "lt", "eq"):
            self.writeComparision(command)
        elif command in ("and", "or"):
            self.writeAndOr(command)
        elif command == "not":
            self.writeNot()
        elif command == "neg":
            self.writeNegate()

    def writePushPop(self, command, segment, index):
        if command.startswith("push"):
            self.writePushConstant(index)
            

    def decrementSP(self):
        self.write("@SP")
        self.write("M=M-1")

    def incrementSP(self):
        self.write("@SP")
        self.write("M=M+1")

    def stackpointerToD(self):
        self.decrementSP()
        self.write("A=M")
        self.write("D=M")

    def writeAddSubtract(self, command):
        self.stackpointerToD()
        self.decrementSP()
        self.write("A=M")
        if command == "add":
            self.write("D=M+D")
        else:
            self.write("D=M-D")
        self.write("@SP")
        self.write("A=M")
        self.write("M=D")
        self.incrementSP()

    def writeComparision(self, command):
        self.stackpointerToD()
        self.decrementSP()
        self.write("A=M")
        self.write("D=M-D")
        self.write("@SP")
        self.write("A=M")
        self.write("M=-1")
        self.write("@" + str(self.linesWritten + 5))
        self.write("D;J" + command.upper())
        self.write("@SP")
        self.write("A=M")
        self.write("M=0")
        self.incrementSP()

    def writeAndOr(self, command):
        self.stackpointerToD()
        self.decrementSP()
        self.write("A=M")
        if command == "and":
            self.write("M=M&D")
        else:
            self.write("M=M|D")
        self.incrementSP()

    def writeNot(self):
        self.decrementSP()
        self.write("A=M")
        self.write("M=!M")
        self.incrementSP()

    def writeNegate(self):
        self.decrementSP()
        self.write("A=M")
        self.write("M=-M")
        self.incrementSP()

    def writePushConstant(self, constant):
        self.write("@" + str(constant))
        self.write("D=A")
        self.write("@SP")
        self.write("A=M")
        self.write("M=D")
        self.incrementSP()


if __name__ == "__main__":
    srcFile = "StackArithmetic/StackTest/StackTest.vm"
    dstFile = srcFile.replace(".vm", ".asm")
    parser = Parser(srcFile)
    writer = CodeWriter(dstFile)

    try:
        while parser.hasMoreCommands():
            parser.advance()
            writer.comment(parser.current_command)

            if parser.commandType() == "C_ARITHMETIC":
                writer.writeArithmetic(parser.arg1())

            if parser.commandType() in ["C_PUSH", "C_POP"]:
                command, segment = parser.arg1().split(' ')
                writer.writePushPop(command, segment, parser.arg2())
    except:
        writer.close()
        raise
    
    writer.close()
