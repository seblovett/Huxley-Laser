import fileinput
import argparse
import re

def file_replace(filename, search, replace):
    with fileinput.FileInput(filename, inplace=True, backup='.bak') as file:
        for line in file:
            print(line.replace(search, replace), end='')

def regex_replace(filename, search, replace):
    regex = re.compile(search)
    outlines=list()
    with fileinput.FileInput(filename) as file:
        for line in file:
            outlines.append(re.sub(regex, replace, line))
    f=open(filename,'w')
    f.write("".join(outlines))
    f.close()

def repeat_cuts(filename, count, height=0, step = 0):
    #repetitions, everything between M3 and M5
    #check there is only one M3 and one M5
    #collect all codes between them
    if count:
        repeated_lines = list()
        if step:
            repeated_lines.append("STEP PLACEHOLDER")
        is_cut = False
        M3_count = 0
        M5_count = 0

        with fileinput.FileInput(filename) as file:
            for line in file:
                if is_cut:
                    repeated_lines.append(line)
                if line == "M3\n":
                    M3_count = M3_count + 1
                    is_cut = True
                elif line == "M5\n":
                    M5_count = M5_count + 1
                    is_cut = False
        if (M3_count != 1) or (M5_count != 1):
            print(M3_count)
            print(M5_count)
            print("Error - multiple starts and stops not supported")
            return 
        for i in range(count):
            if step:
                repeated_lines[0] = "G1 Z %.4f\n" % (height-step*(i+1))
            regex_replace(filename, "M5", "".join(repeated_lines))

if "__main__" == __name__:
    parser = argparse.ArgumentParser(description='Post process a G-Code file to work on a Huxley Laser')
    parser.add_argument('infile', type=str,
                        help='file to process')
    parser.add_argument('-height', type=float, default=0.0, dest="height",
                        help='Height of material cutting')
    parser.add_argument('-focal', "-f", type=float, default=0.0, dest="focal",
                        help='Focal distance of the laser')
    parser.add_argument('-repeat', "-r", type=int, default=0, dest="repeat",
                        help='Number of repetitions of the program')
    parser.add_argument('-step', "-s", type=float, default=0.0, dest="step",
                        help='Downward step distance between each repeat')
    args = parser.parse_args()

    strs = (
    (".*Penetrate.*", "M600"), 
    ("G00 Z 5.0000", "M601"),
    ("Z -1.0000", ""),
    ("G21", ""),
    ("M3", "G28 X Y\nG0 Z %.4f\nM3" % (args.height + args.focal)),
    ("F [+-]?([0-9]*[.])?[0-9]+", ""), #remove feed rate
    (r"\(([^)]+)\)", ""), #remove comments
    (r"\%", ""), #remove % signs
    (r'^(?:[\t ]*(?:\r?\n|\r))+', "") #multiple new lines
    )
    for s in strs:
        regex_replace(args.infile, s[0], s[1])
    repeat_cuts(args.infile, args.repeat, args.height + args.focal, args.step)
