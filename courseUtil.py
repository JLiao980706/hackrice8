def get_add_subtract_list(input_str, m):
    add_list = ["ADD", "ALTOGETHER", "PLUS", "GET", "TAKE", "ADDING", "GETTING", "TAKING"]
    remove_list = ["REMOVE", "SUBTRACT", "MOVE", "OFF", "NOT", "AWAY", "DROP", "DELETE", "DELETING",
                   "REMOVING", "DROPPING"]
    inputlist = input_str.replace(", ", " ").replace(",", " ").split(" ")
    out = [[], [], []]
    i = 0
    idx = 0
    while i < len(inputlist):
        if i == len(inputlist) - 1:
            if inputlist[i] in m.keys():
                out[idx].append(inputlist[i])
        elif i < len(inputlist) - 1 and (inputlist[i] in m.keys() or str(inputlist[i] + inputlist[i + 1]) in m.keys()):
            if inputlist[i] in m.keys():
                out[idx].append(inputlist[i])
            else:
                out[idx].append(inputlist[i] + inputlist[i + 1])
        elif inputlist[i] in add_list:
            idx = 1
        elif inputlist[i] in remove_list:
            idx = 2
        i += 1
    return out


