import csv
import json
import math
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
            mapping[name]["term"] = row[4]
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
    strings = []
    for c in ans:
        pre_req = class_map[c]
        lst1 = []
        for a in pre_req:
            lst2 = []
            for b in a:
                level3 = " and ".join(b)
                if len(b) > 1:
                    level3 = "(" + level3 + ")"
                lst2.append(level3)
            level2 = " or ".join(lst2)
            if len(a) > 1:
                level2 = "(" + level2 + ")"
            lst1.append(level2)
        pre_req_string = " and ".join(lst1)
        pre_req_string = "The pre-req for " + c + " is: " + pre_req_string
        strings.append(pre_req_string)
    res = ""
    if ans:
        for itm in ans:
            res += itm + " and "
        return "You have not completed prerequisite class for " + res[:-5] + ".\n" + "\n".join(strings)
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


def has_time_conflict(lst, class_map):
    lst = [l for l in lst if l != "COMP"]
    res = []
    errorlst = []
    for itm in lst:
        flag = True
        for key, val in class_map[itm]["time"].items():
            for currect_class in res:
                for key2, val2 in class_map[currect_class]["time"].items():
                    if flag and key == key2 and val[0] <= val2[0] <= val[1] or val[0] <= val2[1] <= val[1] or val2[0] <= \
                            val[0] <= val2[1] or val2[0] <= val[1] <= val2[1]:
                        if (itm, currect_class) not in errorlst:
                            errorlst.append((itm, currect_class))
                            flag = False
        if flag and itm not in res:
            res.append(itm)
    return len(errorlst) > 0


def check_valid(lst, m, term):
    for itm in lst:
        if itm not in m.keys():
            return False, 1
        else:
            if term == m[itm]["term"]:
                return False, 0
    return True, 0


def get_msg2send(msg, m, m2, course_taken):
    courses_to_take = get_courses_from_input(msg)
    res = ""
    res += check_workload(courses_to_take, m, 10, 15)
    res += check_prereq(courses_to_take, m2, course_taken)
    res += check_schedule(courses_to_take, m)
    reminder = "You can use keywords like ADD and REMOVE to add/remove courses from your course list"
    all_course_str = ""
    for course in courses_to_take:
        all_course_str += course + ", "
    if all_course_str != "":
        all_course_str = all_course_str[:-2]
    if res.strip() != "":
        return "Your current courses are " + all_course_str + ".\n" + reminder + ".\n\n" + res
    return "Your current courses are " + all_course_str + ".\n" + reminder + ".\n\n" + "Your course selection seems good!\n"


def get_msg2send_from_list(lst, m, m2, course_taken):
    res = ""
    res += check_workload(lst, m, 10, 15)
    res += check_prereq(lst, m2, course_taken)
    res += check_schedule(lst, m)
    reminder = "You can use keywords like ADD and REMOVE to add/remove courses from your course list"
    all_course_str = ""
    for course in lst:
        all_course_str += course + ", "
    if all_course_str != "":
        all_course_str = all_course_str[:-2]
    if res.strip() != "":
        return "Your current courses are " + all_course_str + ".\n" + reminder + ".\n\n" + res
    return "Your current courses are " + all_course_str + ".\n" + reminder + ".\n\n" + "Your course selection seems good!\n"


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
    rank_num_dict = defaultdict(list)
    for key, value in cat_rank_dict.items():
        rank_num_dict[value].append(key)
    val_list = [v for v in rank_num_dict.keys()]
    val_list.sort()
    cat_rank_list = []
    for v in val_list:
        cat_rank_list += rank_num_dict[v]
    # Filtered the course that does not
    first_choice = cat_rank_list[-1]
    first_course_list = reverse_course_cat[first_choice]
    if len(cat_rank_dict) == 1:
        return (first_choice, first_course_list), ()
    second_choice = cat_rank_list[-2]
    second_course_list = reverse_course_cat[second_choice]
    return (first_choice, first_course_list), (second_choice, second_course_list)


def check_major_pre_req(lst, pre_req, courses_taken):
    major_req = readin_json("cs_bs_req.json")
    new_req = []
    correct_cur = 0
    for cross_list in major_req:
        cross_list = [l.replace(" ", "") for l in cross_list]
        no_pre_req = report_prereq(cross_list, pre_req, courses_taken)
        new_list = [c for c in cross_list if c not in no_pre_req]
        for grp in new_list:
            if grp in new_list:
                correct_cur += 1
                break
        satisfied = False
        for c in courses_taken + lst:
            satisfied = satisfied or c in new_list
        if not satisfied:
            new_req.append(new_list)
    if correct_cur == len(lst):
        return "All of the courses you are taking are major requirements!"
    all_empty = True
    for lst in new_req:
        all_empty = all_empty and (lst == [])
    if all_empty:
        return "There is no more major requirements that you can take now."
    big_string = "You can consider take the following course to satisfy the major requirement:\n"
    for lst in new_req:
        if len(lst) > 0:
            cur_string = " or ".join(lst) + "\n"
            big_string += cur_string
    return big_string


def readin_semester():
    f = open("courses_general_info.csv")
    d = {}
    header = True
    for row in f:
        if header:
            header = False
            continue
        itms = row.split(",")
        c = itms[0].replace(" ", "")
        sms = itms[-1][0]
        if c in d.keys():
            d[c] = "FS"
        else:
            d[c] = sms
    return d


def predict_grad_wrapper(lst, courses_taken, sms):
    result = predict_grad(lst, courses_taken, sms)
    string = "Graduation Check: \n"
    if result[0] == 0:
        return string + "You will graduate on time!"
    else:
        elective_string = ""
        if "COMP" in result[1]:
            elective_string = "There may also be other elective/capstone courses that you cannot take."
        strings = []
        for k in result[1]:
            if "COMP" in k:
                elective_string = ".\nThere may also be other elective/capstone courses that you cannot take."
            substring = " or ".join([m for m in k if m != "COMP"])
            if len(k) > 1:
                substring = "(" + substring + ")"
            if substring != "":
                strings.append(substring)
        mystring = ", ".join(strings)
        return string + "You will not be able to graduate on time. The courses that you are not able to take are: " + mystring + elective_string


def predict_grad(lst, courses_taken, sms):
    major_req = readin_json("cs_bs_req.json")
    min_miss = float("inf")
    miss = []
    all_courses = lst + courses_taken
    if sms == 8:
        for itm in major_req:
            taken = False
            for idx in all_courses:
                if idx in itm:
                    taken = True
                    break
            if not taken:
                miss.append(itm)
        elective_count = 0
        for c in all_courses:
            if c == "COMP":
                elective_count += 1
        for i in range(5 - elective_count):
            miss.append(["COMP"])
        return len(miss), miss

    for state in generate_states(all_courses, sms + 1):
        result = predict_grad(state, all_courses, sms + 1)
        if result[0] == 0:
            return 0, []
        if result[0] <= min_miss:
            min_miss = result[0]
            miss = result[1]
    return min_miss, miss


def generate_states(courses_taken, sms):
    major_req = readin_json("cs_bs_req.json")
    pre_req = readin_json("pre_req.json")
    pos_major = []
    for itm in major_req:
        no_pre_req = report_prereq(itm, pre_req, courses_taken)
        satisfied = False
        for c in courses_taken:
            if c in itm:
                satisfied = True
                break
        if satisfied:
            continue
        nitm = [l for l in itm if l not in no_pre_req]
        if len(nitm) > 0:
            pos_major.append(nitm)
    return do_generate(pos_major, [], sms)


def do_generate(pos_major, cur, sms):
    sms_data = readin_semester()
    class_map = get_course_info()
    if len(pos_major) == 0 or len(cur) == 5:
        return [cur]
    result = do_generate(pos_major[1:], cur, sms)
    for itm in pos_major[0]:
        if itm not in class_map.keys() and itm != "COMP":
            continue
        k = "S"
        if math.floor(sms / 2) * 2 < sms:
            k = "F"
        if k not in sms_data[itm]:
            continue
        cp_cur = list(cur)
        cp_cur.append(itm)
        if not has_time_conflict(cp_cur, class_map):
            result = do_generate(pos_major[1:], cp_cur, sms) + result
    max_len = max([len(c) for c in result])
    new_result = [l for l in result if len(l) == max_len]
    for itm1 in new_result:
        for i in range(5 - max_len):
            itm1.append("COMP")
    return new_result

# print(predict_grad_wrapper(["COMP322", "COMP310", "NEUR416", "PSYC362", "PSYC461"], ["COMP140", "COMP182", "COMP215", "MATH222", "MATH221", "MATH101", "MATH102", "MATH354", "PHYS101", "PHYS102"], 7))

# print(check_major_pre_req([], get_pre_req(), ["COMP140", "COMP215", "MATH354", "COMP321", "COMP326", "COMP447", "COMP441"]))
# print(get_course_info())
# print(course_recommandation([], get_pre_req(), ["COMP140", "COMP215", "MATH354", "COMP321", "COMP326", "COMP447", "COMP441"], readin_json("course_graph.json"), readin_json("course_cat.json")))




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