# Import
from matplotlib import pyplot as plt


# Global Variable initialization
ISA = {
    "A": {"00000", "00001", "00110", "01010", "01011", "01100"},
    "B": {"00010", "01000", "01001"},
    "C": {"00011", "00111", "01101", "01110"},
    "D": {"00100", "00101"},
    "E": {"01111", "10000", "10001", "10010"},
    "F": {"10011"}
}
regi = {
    "000": 0.,
    "001": 0.,
    "010": 0.,
    "011": 0.,
    "100": 0.,
    "101": 0.,
    "110": 0.,
    "111": 0.,
}
memory_adder = {}
Program_counter = 0
Cycle = -1
x_coord = []
y_coord = []
Commands = []
temp = []

# Utility function to get the 16 bit value from the register
def get16bit(k):
    return '{0:016b}'.format(k)

# Utility function to get the 8 bit value from the register
def get8bit(k):
    return '{0:08b}'.format(k)

# Dump all values of the registers
def register_log():
    for each in regi.keys():
        print(get16bit(regi[each]), end=" ")

def flagReset():
    regi["111"] = 0


def getOut(cmd):
    op_code = cmd[:5]

    if op_code in ISA["A"]:
        reg1 = cmd[7:10]
        reg2 = cmd[10:13]
        reg3 = cmd[13:]

        if(op_code == "00000"):
            add(reg1, reg2, reg3)
        elif(op_code == "00001"):
            sub(reg1, reg2, reg3)
        elif(op_code == "00110"):
            mul(reg1, reg2, reg3)
        elif(op_code == "01010"):
            XOR(reg1, reg2, reg3)
        elif(op_code == "01011"):
            OR(reg1, reg2, reg3)
        elif(op_code == "01100"):
            AND(reg1, reg2, reg3)

    elif op_code in ISA["B"]:
        reg = cmd[5:8]
        IM = int(cmd[8:], 2)

        if(op_code == "00010"):
            movI(reg, IM)
        elif(op_code == "01000"):
            RS(reg, IM)
        elif(op_code == "01001"):
            LS(reg, IM)

    elif op_code in ISA["C"]:
        reg1 = cmd[10:13]
        reg2 = cmd[13:]

        if(op_code == "00011"):
            movR(reg1, reg2)
        elif(op_code == "00111"):
            div(reg1, reg2)
        elif(op_code == "01101"):
            NOT(reg1, reg2)
        elif(op_code == "01110"):
            CMP(reg1, reg2)

    elif op_code in ISA["D"]:
        reg = cmd[5:8]
        mem = cmd[8:]

        if(op_code == "00100"):
            load(reg, mem)
        elif(op_code == "00101"):
            store(reg, mem)

    print()


def add(r1, r2, r3):
    regi[r1] = regi[r2] + regi[r3]
    flagReset()
    register_log()


def sub(r1, r2, r3):
    regi[r1] = regi[r2] - regi[r3]
    flagReset()
    register_log()


def mul(r1, r2, r3):
    regi[r1] = regi[r2] * regi[r3]
    flagReset()
    register_log()


def OR(r1, r2, r3):
    regi[r1] = regi[r2] | regi[r3]
    flagReset()
    register_log()


def XOR(r1, r2, r3):
    regi[r1] = regi[r2] ^ regi[r3]
    flagReset()
    register_log()


def AND(r1, r2, r3):
    regi[r1] = regi[r2] & regi[r3]
    flagReset()
    register_log()


def movI(r, im):
    regi[r] = im
    flagReset()
    register_log()


def RS(r, im):
    regi[r] = regi[r] >> im
    flagReset()
    register_log()


def LS(r, im):
    regi[r] = regi[r] << im
    flagReset()
    register_log()


def movR(reg1, reg2):
    regi[reg1] = regi[reg2]
    flagReset()
    register_log()


def div(reg1, reg2):
    regi["000"] = regi[reg1] // regi[reg2]
    regi["001"] = regi[reg1] % regi[reg2]
    flagReset()
    register_log()


def NOT(reg1, reg2):
    regi[reg1] = 65535 ^ regi[reg2]
    flagReset()
    register_log()


def CMP(reg1, reg2):
    flagReset()
    if(regi[reg1] > regi[reg2]):
        regi["111"] = 2

    if(regi[reg1] < regi[reg2]):
        regi["111"] = 4

    if(regi[reg1] == regi[reg2]):
        regi["111"] = 1
    register_log()


def load(reg, mem):
    if(mem not in memory_adder.keys()):
        memory_adder[mem] = 0
    regi[reg] = memory_adder[mem]
    flagReset()
    register_log()


def store(reg, mem):
    memory_adder[mem] = regi[reg]
    flagReset()
    register_log()

# Bonus Q1  - Plot the graph of the program
def plot():
    plt.style.use('seaborn')
    plt.scatter(x_coord, y_coord, cmap='hot',
               edgecolor='black', linewidth=1, alpha=0.75)
    plt.title('Memory accessed Vs Cycles')
    plt.xlabel('Cycle number')
    plt.ylabel('Memory address')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":

    while True:
        try:
            line = input()
            Commands.append(line)

        except EOFError:
            break

    while(Commands[Program_counter] != "1001100000000000"):
        Cycle += 1
        op_code = Commands[Program_counter][:5]

        print(get8bit(Program_counter), end=" ")

        # For the graphical representation of the memory
        x_coord.append(Cycle)
        y_coord.append(Program_counter)

        # For non jump OPs
        if(op_code in ISA["A"] or op_code in ISA["B"] or op_code in ISA["C"]):
            getOut(Commands[Program_counter])
            Program_counter += 1

        elif (op_code in ISA["D"]):
            getOut(Commands[Program_counter])
            mem = int(Commands[Program_counter][8:], 2)
            y_coord.append(mem)
            x_coord.append(Cycle)
            Program_counter += 1

        # For jump OPs
        else:
            mem = int(Commands[Program_counter][8:], 2)
            # jmp
            if op_code == "01111":
                Program_counter = mem

            # jlt
            if op_code == "10000":
                if(regi["111"] == 4):
                    Program_counter = mem
                else:
                    Program_counter += 1

            # jgt
            if op_code == "10001":
                if(regi["111"] == 2):
                    Program_counter = mem
                else:
                    Program_counter += 1

            # jge
            if op_code == "10010":
                if(regi["111"] == 1):
                    Program_counter = mem
                else:
                    Program_counter += 1

            flagReset()
            register_log()
            print()


    flagReset()

    print(get8bit(Program_counter), end=" ")

    register_log()
    print()

    y_coord.append(Program_counter)
    Cycle += 1
    x_coord.append(Cycle)
    Program_counter += 1

    for i in range(0, 256):
        if(i < len(Commands)):
            print(Commands[i])
        else:
            if(get8bit(i) in memory_adder.keys()):
                print(get16bit(memory_adder[get8bit(i)]))
            else:
                print("0000000000000000")


    plot()
