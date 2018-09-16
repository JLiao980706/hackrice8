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
    return out, idx


def tpt_to_output_string(tpt):
    if () in tpt:
        return "Sorry, maybe you should take more courses for me to generate recommended courses."
    itm1 = tpt[0]
    itm2 = tpt[1]
    course_field_1 = itm1[0]
    course_field_2 = itm2[0]
    courses_list_1 = itm1[1]
    courses_list_2 = itm2[1]
    res = "Based on courses you have taken and the courses you are taking this semester, I recommend you to take cour" \
          "ses in " + course_field_1 + " and " + course_field_2 + ".\n\n"
    ans1 = ""
    ans1 += course_field_1
    if not courses_list_1:
        ans1 = "Sorry we are not able to provide you any course in " + course_field_1 + " field.\n\n"
    else:
        ans1 += ": "
        for course in courses_list_1:
            ans1 += course + ", "
        ans1 = ans1[:-2] + ".\n\n"
    ans2 = ""
    ans2 += course_field_2
    if not courses_list_2:
        ans2 = "Sorry we are not able to provide you any course in " + course_field_2 + " field.\n\n"
    else:
        ans2 += ": "
        for course in courses_list_2:
            ans2 += course + ", "
        ans2 = ans2[:-2] + ".\n\n"
    res += ans1 + ans2
    return res

