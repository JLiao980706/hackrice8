import csv
import json
from collections import defaultdict


def to_time_interval(timestr):
    times = timestr.split("-")
    begin = (10 * int(times[0][0]) + int(times[0][1])) * 60 + 10 * int(times[0][3]) + int(times[0][4])
    end = (10 * int(times[1][0]) + int(times[1][1])) * 60 + 10 * int(times[1][3]) + int(times[1][4])
    return begin, end


def get_course_info():
    mapping = {}
    with open('courses_general_info.csv') as csvfile:
        readCSV = csv.reader(csvfile, delimiter=',')
        first = next(readCSV)
        for row in readCSV:
            # print(row)
            name = row[0].replace(" ", "").upper()
            mapping[name] = {}
            mapping[name]["workload"] = float(row[2].replace(" ", ""))
            # mapping[name]["preReq"] = row[3].split(" ")
            timelst = row[1].replace("\"", "").replace(" ", "").split("/")
            # print(timelst)
            mapping[name]["time"] = {}
            for i in range(0, len(timelst), 2):
                for itm in timelst[i+1]:
                    mapping[name]["time"][itm] = to_time_interval(timelst[i])
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


def readin_json(name):
    f = open(name)
    rows = [l for l in f]
    data = json.loads("\n".join(rows))
    return data


def get_pre_req():
    return readin_json("pre_req.json")


def get_courses_from_input(input_string):
    return input_string.strip().replace(" ", "").upper().split(",")


def check_workload(lst, class_map, min_workload, max_workload):
    workload = 0
    for itm in lst:
        workload += class_map[itm]["workload"]
    if workload < min_workload:
        return "Want me to recommend you some course? Type 'Course Recommendation' to learn more.\n\n"
    if workload > max_workload:
        return "Caution: Heavy workload!\n\n"
    return ""


def report_prereq(lst, class_map, courses_taken):
    ans = []
    for itm in lst:
        if itm not in class_map.keys():
            continue
        this_pr = class_map[itm]
        sat = True
        for and1 in this_pr:
            itm_or = False
            for or1 in and1:
                itm_and = True
                for cname in or1:
                    itm_and = itm_and and (cname in courses_taken)
                itm_or = itm_or or itm_and
            sat = sat and itm_or
        if not sat:
            ans.append(itm)
    return ans


def check_prereq(lst, class_map, courses_taken):
    ans = report_prereq(lst, class_map, courses_taken)
    res = ""
    if ans:
        for itm in ans:
            res += itm + " and "
        return "You have not completed prerequisite class for " + res[:-5] + ".\n\n"
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


def check_valid(lst, m):
    for itm in lst:
        if itm not in m.keys():
            return False
    return True


def get_msg2send(msg, m, m2):
    courses_to_take = get_courses_from_input(msg)
    res = ""
    res += check_workload(courses_to_take, m, 4, 8)
    res += check_prereq(courses_to_take, m2, [])
    res += check_schedule(courses_to_take, m)
    all_course_str = ""
    for course in courses_to_take:
        all_course_str += course + ", "
    if all_course_str != "":
        all_course_str = all_course_str[:-2]
    if res.strip() != "":
        return "Your current courses are " + all_course_str + ".\n\n" + res
    return "Your current courses are " + all_course_str + ".\n\n" + "Your course selection seems good!\n"


def get_msg2send_from_list(lst, m, m2):
    res = ""
    res += check_workload(lst, m, 4, 8)
    res += check_prereq(lst, m2, [])
    res += check_schedule(lst, m)
    all_course_str = ""
    for course in lst:
        all_course_str += course + ", "
    if all_course_str != "":
        all_course_str = all_course_str[:-2]
    if res.strip() != "":
        return "Your current courses are " + all_course_str + ".\n\n" + res
    return "Your current courses are " + all_course_str + ".\n\n" + "Your course selection seems good!\n"


def course_recommandation(lst, class_map, courses_taken, course_graph, course_catergory):
    sum_courses = lst + courses_taken
    useful_courses = []
    for course in sum_courses:
        if course in course_graph.keys():
            useful_courses.append(course)

    reverse_course_cat = defaultdict(list)
    if len(useful_courses) == 0:
        return (), ()
    for key, value in course_catergory.items():
        if key not in sum_courses:
            reverse_course_cat[value].append(key)
    del_list = []
    for key, value in reverse_course_cat.items():
        no_pre_req = report_prereq(value, class_map, courses_taken)
        nlist = [c for c in value if c not in no_pre_req]
        # if len(nlist) == 0:
        #     del_list.append(key)
        # else:
        #     reverse_course_cat[key] = nlist
        reverse_course_cat[key] = nlist
    # for k in del_list:
    #     del reverse_course_cat[k]

    cat_rank_dict = defaultdict(int)
    for c in useful_courses:
        if course_catergory[c] in reverse_course_cat.keys():
            cat_rank_dict[course_catergory[c]] += 1
    print(cat_rank_dict)
    rank_num_dict = defaultdict(list)
    for key, value in cat_rank_dict.items():
        rank_num_dict[value].append(key)
    print(rank_num_dict)
    val_list = [v for v in rank_num_dict.keys()]
    val_list.sort()
    cat_rank_list = []
    for v in val_list:
        cat_rank_list += rank_num_dict[v]
    print(val_list)
    # Filtered the course that does not
    first_choice = cat_rank_list[-1]
    first_course_list = reverse_course_cat[first_choice]
    if len(cat_rank_dict) == 1:
        return (first_choice, first_course_list), ()
    second_choice = cat_rank_list[-2]
    second_course_list = reverse_course_cat[second_choice]
    return (first_choice, first_course_list), (second_choice, second_course_list)


print(get_course_info())
print(course_recommandation([], get_pre_req(), ["COMP140", "COMP215", "MATH354", "COMP321", "COMP326", "COMP447", "COMP441"], readin_json("course_graph.json"), readin_json("course_cat.json")))




# msg_out = get_msg2send("Comp 215, math101, ECON100", get_course_info(), get_pre_req())
# print(msg_out)


# test cases
# m = get_course_info()
# m2 = get_pre_req()
# courses_to_take_1 = get_courses_from_input("Comp 140, math101, ECON100")
# courses_to_take_2 = get_courses_from_input("Comp 215, comp140, ECON100")
# courses_to_take_3 = get_courses_from_input("Comp 215, math101")
# print(check_workload(courses_to_take_1, m, 4, 8))
# print(check_workload(courses_to_take_2, m, 4, 16))
# print(check_prereq(courses_to_take_1, m2, []))
# print(check_prereq(courses_to_take_2, m2, []))
# print(check_schedule(courses_to_take_3, m))
# print(check_schedule(courses_to_take_3, m))
# print(check_schedule(courses_to_take_1, m))
# print(check_schedule(courses_to_take_1, m))