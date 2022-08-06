import sys

PC = 0
Commands = []
lineArr = []
linNum = 0

ISA = {"add"    : ("10000", "A",),
        "sub"   : ("10001", "A"),
        "mov"   : ("10010", "Z",),
        "ld"    : ("10100", "D"),
        "st"    : ("10101", "D"),
        "mul"   : ("10110", "A"),
        "div"   : ("10111", "C"),
        "rs"    : ("11000", "B"),
        "ls"    : ("11001", "B"),
        "xor"   : ("11010", "A"),
        "or"    : ("11011", "A"),
        "and"   : ("11100", "A"),
        "not"   : ("11101", "C"),
        "cmp"   : ("11110", "C"),
        "jmp"   : ("11111", "E"),
        "jlt"   : ("01100", "E"),
        "jgt"   : ("01101", "E"),
        "je"    : ("01111", "E"),
        "hlt"   : ("01010", "F") }

reg = { "R0": "000",
        "R1": "001",
        "R2": "010",
        "R3": "011",
        "R4": "100",
        "R5": "101",
        "R6": "110",
        "FLAGS": "111",}

Symbol = {}
label = {}

def get8bit (k):
    return '{0:08b}'.format(k)

def get_encoding(command):
    openrand = command[0]
    encoding = ''

    if openrand == "add" or openrand == "sub" or openrand == "mul" or openrand == "xor" or openrand == "or" or openrand == "and":
        encoding = ISA[openrand][0] + '00' + reg[command[1]] + reg[command[2]] + reg[command[3]]

    if(openrand == "mov"):
        if(command[-1][0] == '$'):
            k = int(command[-1][1:])
            encoding = "10010" + reg[command[1]] + get8bit(k)
        else :
            encoding = "10011" + "00000" + reg[command[1]] + reg[command[2]]

    if(openrand == 'ld' or openrand == 'st'):
        k = Symbol[command[-1]]
        tempS = get8bit(k)
        encoding = ISA[openrand][0] + reg[command[1]] + tempS

    if(openrand == "cmp" or openrand == "div" or openrand == "not" ):
        if(openrand == "not"):
            k = int(command[-1][1:])
        encoding = ISA[openrand][0] + '00000' + reg[command[1]] + reg[command[2]]

    if(openrand == "jmp" or openrand == "jlt" or openrand == "jgt" or openrand == "je"):
        encoding = ISA[openrand][0] + '000' + label[command[1]]

    if(openrand == "hlt"):
        encoding = ISA[openrand][0] + '00000000000'

    if(openrand ==  "rs" or openrand == "ls"):
        k = int(command[-1][1:])
        encoding = ISA[openrand][0] + reg[command[1]] + get8bit(k)

    return encoding

# Handle Mov seperately
def iscommandvalid(command):
    openrand = command[0]
    if openrand not in ISA.keys():
        print("Invalid openrand Code ")
        return False
        
    t = ISA[openrand][1]
    
    if(openrand == "mov"):
        if(len(command) != 3):
            print("Invalid syntax ")
            return False

        if(command[2][0] == '$'):
            if(((command[1] not in reg.keys() or command[1] == "FLAGS"))):
                print(command[1] + " cannot be used as a Register ")
                return False
            im = command[2][1:]
            if(im.isdigit() == False):
                print("Invalid immediate value ")
                return False
            im = int(im)
            if(im not in range(0, 256)):
                print("Imm vaue not in range ")
                return False
            return True

        elif(command[2] in reg.keys()):
            if(command[1] in reg.keys() and command[1] != "FLAGS"):
                return True
            print("Invalid register ")
            return False

        else:
            print("Invalid syntax ")
            return False

    elif(t == 'A'):
        if(len(command) != 4):
            print("Invalid syntax ")
            return False

        r1 = command[1]
        r2 = command[2]
        r3 = command[3]

        if((r1 not in reg.keys() or r1 == "FLAGS") or (r2 not in reg.keys() or r2 == "FLAGS") or (r3 not in reg.keys() or r3 == "FLAGS")):
            print("Invalid register names ")
            return False
        return True
    

    elif(t == 'B'):
        if(len(command) != 3):
            print("Invalid syntax ")
            return False
        r = command[1]
        if(command[2][0] != '$'):
            print("Invalid syntax ")
            return False

        im = command[2][1:]
        if(im.isdigit() == False):
            print("Invalid immediate value ")
            return False
        im = int(im)
        if((r not in reg.keys() or r == "FLAGS")):
            print("Invalid register names ")
            return False
        if im not in range (0, 256):
            print("Imm value not in range ")
            return False
        return True


    elif(t == 'C'):
        if(len(command) != 3):
            print("Invalid syntax ")
            return False
        r1 = command[1]
        r2 = command[2]
        if((r1 not in reg.keys() or r1 == "FLAGS") or (r2 not in reg.keys() or r2 == "FLAGS")):
            print("Invalid register usage ")
            return False
        return True
    

    elif(t == 'D'):
        if(len(command) != 3):
            print("Invalid syntax ")
            return False
        r = command[1]
        var = command[2]
        if((r not in reg.keys() or r == "FLAGS")):
            print("Invalid register names ")
            return False
        if var not in Symbol.keys() or var in label.keys():
            print("Invalid use of variables ")
            return False
        return True


    elif(t == 'E'):
        if(len(command) != 2):
            print("Invalid syntax ")
            return False
        var = command[1]
        if(var not in label.keys() or var in Symbol.keys()):
            print("Invalid use of label ")
            return False
        return True

    else:
        print("Invalid syntax ")
        return False
    
    
# Assigns the Symbol/var none and returns bool to append the command
def valid(lst, i):
    if(lst[0] != 'var'):
        return True

    if(len(lst) == 1):
        print("Error: no variable name was mentioned during declaration at line " + str(i))
        sys.exit()

    elif(lst[1] in Symbol.keys()):
        print("Error: Redeclaration of a variable at line " + str(i))
        sys.exit()

    if(len(Commands) != 0):
        print("Error: Variable not declared at the beginning at line " + str(i))
        sys.exit()

    for char in lst[1]:
        if(not(char.isalnum() == True or char == "_")):
            print("Error: invalid varible name at line " + str(i))
            sys.exit()

    if(lst[1].isdigit()):
        print("Error: purely numberic variable name at line " + str(i))
        sys.exit()

    Symbol[lst[1]] = None
    return False


if __name__ == "__main__":
    while True:
        linNum += 1
        try:
            line = input().split()
            if(len(line) == 0):
                continue
            if(valid(line, linNum) == True):
                Commands.append(line)
                lineArr.append(linNum)

        except EOFError:
            break
        
    # Giving the values to the Symbols/var
    ctr = len(Commands)
    for k in Symbol.keys():
        Symbol[k] = ctr
        ctr += 1
        
    # Giving the values to the labels
    for i, command in enumerate(Commands):
        if((command[0][0:-1] and command[0]) not in (ISA.keys() or reg.keys())):
            l = command[0]
            if(l[-1] != ':'):
                print("Error: Typo at line " + str(lineArr[i]))
                sys.exit()
            l = l[0:-1]

            for char in l:
                if(not(char.isalnum() == True or char == '_')):
                    print("Error: invalid label in line " + str(lineArr[i]))
                    sys.exit()
            
            if(l.isdigit()):
                print("Error: invalid label in line " + str(lineArr[i]))
                sys.exit()
            
            if(command[0][0:-1] in label.keys()):
                print("Error: Redeclaration of a label in line " + str(lineArr[i]))
                sys.exit()   

            label[command[0][0:-1]] = get8bit(i)

    # check for lesser than 257 lines
    if(len(Commands) > 256):
        print("Error: More than 256 instuctions")
        sys.exit()

    for i,command in enumerate(Commands):
        # Strip for flags
        if(command[0][-1] == ':'):
            if(len(command) == 1):
                print("Error in line " + str(lineArr[i]))
                sys.exit()
            command = command[1:]

        # Check for hlts
        hltCheck = True
        if(command[0] == "hlt"):
            if(not(len(command) == 1 and i + 1 == len(Commands))):
                print("hlt error in line " + str(lineArr[i]))
                break
            else:
                print("1001100000000000")
                break
            
        #Checks for Syntax error
        flag = iscommandvalid(command)

        if(flag == False):
            print("Error in line at line " + str(lineArr[i]))
            break
        else:
            encoding = get_encoding(command)
            print(encoding)
            

        if(i == len(Commands) - 1 and command != "hlt"):
            print("Error: missing hlt line at line " + str(lineArr[i]))
            sys.exit()
