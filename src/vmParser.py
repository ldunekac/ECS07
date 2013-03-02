




class VMParser():

    def __init__(self, fileName):
        self.file = open(fileName, "w")
        self.setup()

    def setup(self):
        self.file.write("@256\nD=A\n@SP\nM=D")

    def translate(self, statement):
        if statement == "" or statement == "\n":
            return
        else:
            statement = statement.strip()
            argList = statement.split(" ")
            self.file.write(statement)