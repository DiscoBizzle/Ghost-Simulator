import re

def tidy_property(lines, start_line): # Make each property string into one list element
    #print lines[start_line]

    if lines[start_line][0]=="{":
        remaining_lines = lines[start_line:]

        for i, s in enumerate(remaining_lines):
            if "}" in s:
                remn_offset = i
                break

        end_line = start_line + remn_offset # Find line with next closing brace.
        #print end_line
        #print lines[end_line]
        #print lines[start_line:end_line+1]
        #print "\n".join(lines[start_line:end_line+1])
        return "\n".join(lines[start_line:end_line+1])
    else:
        print("Specified line is not a property line")

def load_map(map_filename): # Load a map from a map file

    map_f = open(map_filename, 'r')
    lines = map_f.readlines()
    lines_tmp = []

    for line in lines:
        if (line[0]=="#" or not line.strip()): # Throw away comments or blank lines.
            pass
        else:
            lines_tmp.append(line)

    lines = lines_tmp
    lines_tmp = []

    tidy_property(lines, 2)
    #for i, line in enumerate(lines):
    #    if (line[0]=="{"):
    #        lines_tmp.append(tidy_property(lines, i))

    #print lines_tmp
