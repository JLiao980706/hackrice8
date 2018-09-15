import csv


def to_time_interval(timestr):
    times = timestr.split("-")
    begin = (10 * int(times[0][0]) + int(times[0][1])) * 60 + 10 * int(times[0][3]) + int(times[0][4])
    end = (10 * int(times[1][0]) + int(times[1][1])) * 60 + 10 * int(times[1][3]) + int(times[1][4])
    return begin, end


def get_course_info():
    mapping = {}
    with open('COMP.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        first = next(readCSV)
        for row in readCSV:
            # print(row)
            mapping[row[0]] = {}
            mapping[row[0]]["workload"] = float(row[2])
            mapping[row[0]]["preReq"] = row[3].split(" ")
            timelst = row[1].split("/")
            # print(timelst)
            mapping[row[0]]["time"] = {}
            for i in range(0, len(timelst), 2):
                for itm in timelst[i+1]:
                    mapping[row[0]]["time"][itm] = to_time_interval(timelst[i])
            # timelst2 = row[4].split("/")
            # if timelst2 != "none":
            #     mapping[row[0]]["lab"] = []
            #     for i in range(0, len(timelst), 2):
            #         for itm in timelst[i+1]:
            #             mapping[row[0]]["lab"].append(itm, (to_time_interval(timelst2[i])))
            #     print([mapping[row[0]]["lab"]])
            # else:
            #     mapping[row[0]]["lab"] = []
    return mapping


def get_courses_from_input(input_string):
    return input_string.strip().replace(" ", "").upper().split(",")


def check_workload(lst, class_map, min_workload, max_workload):
    workload = 0
    for itm in lst:
        workload += class_map[itm]["workload"]
    if workload < min_workload:
        return "Maybe too easy for you?"
    if workload > max_workload:
        return "Too heavy workload"
    return ""


def check_prereq(lst, class_map, courses_taken):
    ans = []
    for itm in lst:
        for pre_req in class_map[itm]["preReq"]:
            if pre_req.lower() != "none" and pre_req not in courses_taken and itm not in ans:
                ans.append(itm)
    res = ""
    if ans:
        for itm in ans:
            res += itm + " and "
        return "You have not completed prerequisite class for " + res[:-5] + "."
    return res


def check_schedule(lst, class_map):
    time = {"1": [], "2": [], "3": [], "4": [], "5": []}
    res = []
    errorlst = []
    ans = ""
    # print(lst)
    for itm in lst:
        flag = True
        for key, val in class_map[itm]["time"].items():
            for currect_class in res:
                for key2, val2 in class_map[currect_class]["time"].items():
                    if flag and key == key2 and val[0] <= val2[0] <= val[1] or val[0] <= val2[1] <= val[1] or val2[0] <= val[0] <= val2[1] or val2[0] <= val[1] <= val2[1]:
                        if (itm, currect_class) not in errorlst:
                            errorlst.append((itm, currect_class))
                            flag = False
        if flag and itm not in res:
            res.append(itm)
    for itm in errorlst:
        ans += str("Oops, " + str(itm[0]) + " and " + str(itm[1]) + " have conflicting schedule.\n")
    if ans:
        return ans[:-2]
    return ans


def get_msg2send(msg):
    m = get_course_info()
    courses_to_take = get_courses_from_input(msg)
    res = ""
    res += check_workload(courses_to_take, m, 4, 8) + "\n"
    res += check_prereq(courses_to_take, m, []) + "\n"
    res += check_schedule(courses_to_take, m) + "\n"
    return res


msg_out = get_msg2send("Comp 215, math101, ECON100")
print(msg_out)






# test cases
# m = get_course_info()
# courses_to_take_1 = get_courses_from_input("Comp 140, math101, ECON100")
# courses_to_take_2 = get_courses_from_input("Comp 215, comp140, ECON100")
# courses_to_take_3 = get_courses_from_input("Comp 215, math101")
# print(check_workload(courses_to_take_1, m, 4, 8))
# print(check_workload(courses_to_take_2, m, 4, 16))
# print(check_prereq(courses_to_take_1, m, []))
# print(check_prereq(courses_to_take_2, m, []))
# print(check_schedule(courses_to_take_3, m))
# print(check_schedule(courses_to_take_3, m))
# print(check_schedule(courses_to_take_1, m))
# print(check_schedule(courses_to_take_1, m))