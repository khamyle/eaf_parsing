"""
For my Bachelor - Thesis (Cognitive Computing), WS 21/ 22
This code extract Annotation Values, counting them and specific Tiers from .eaf-files into .csv files as a table

Written by: Kha My Le
Date: 07.01.2022
"""

import xml.etree.ElementTree as ET
import csv
import numpy as np

FILES_NAMES = ['26_Anno_Done/26-3.eaf',
               '48_Anno_Done/48-3.eaf'] # '29_Anno_Done/29-3.eaf',

TOTAL_NUM_OF_DIALOGS = len(FILES_NAMES)


def get_xml_data(filename):
    tree = ET.parse(filename)
    root = tree.getroot()
    return root


def parse_time(root, time_id):
    for time_order in root.findall('TIME_ORDER'):
        for slot in time_order:
            id = slot.attrib['TIME_SLOT_ID']
            if time_id == id:
                value = slot.attrib['TIME_VALUE']  # Value in miliseconds
                return value


def parse_tier(root, target_tier):
    a_annotations = [[]]
    b_annotations = [[]]
    d_annotations = [[]]

    for tier in root.findall('TIER'):  # check which tier in file
        if target_tier in tier.attrib['TIER_ID']:
            tier_name = tier.attrib['TIER_ID']
            if 'A' in tier_name:
                a_annotations[0] = get_annotation_values(tier, a_annotations, target_tier)
            elif 'B' in tier_name:
                b_annotations[0] = get_annotation_values(tier, b_annotations, target_tier)
            elif 'D' in tier_name:
                d_annotations[0] = get_annotation_values(tier, d_annotations, target_tier)

    return a_annotations, b_annotations, d_annotations


def get_annotation_values(current_tier, list_name, target_tier):
    tier_name = current_tier.attrib['TIER_ID']
    for annotation in current_tier:
        for align_annotation in annotation:
            if target_tier == 'Detail':
                annotation_id = align_annotation.attrib['ANNOTATION_REF']
            else:
                annotation_id = align_annotation.attrib['ANNOTATION_ID']
            for value in align_annotation:  # value: annotation values in current tier
                annotation_value = value.text
                list_name.append([annotation_id, annotation_value])

    return tier_name


def get_time_values(root, annotation_id):
    time_value1 = []
    time_value2 = []

    if isinstance(annotation_id, str):
        length = 1
    else:
        length = len(annotation_id)

    i = 0
    while i < length:
        if length == 1:
            id = annotation_id
        else:
            id = annotation_id[i]
        for tier in root.findall('TIER'):  # check which tier in file
            for annotation in tier:
                for align_annotation in annotation:
                    if id == align_annotation.attrib['ANNOTATION_ID']:
                        ts_ref1 = align_annotation.attrib['TIME_SLOT_REF1']
                        ts_ref2 = align_annotation.attrib['TIME_SLOT_REF2']
                        t_val1 = parse_time(root, ts_ref1)
                        t_val2 = parse_time(root, ts_ref2)
                        time_value1.append(t_val1)
                        time_value2.append(t_val2)
        i += 1

    return time_value1, time_value2


def convert_to_csv(toWrite, name):
    file = open("Auswertung/" + str(name) + ".csv", 'w')
    with file:
        writer = csv.writer(file)
        for row in toWrite:
            writer.writerow(row)


def filter_annotation(tier_list):
    new_list = [tier_list[0]]
    i = 1
    while i < len(tier_list):
        annotation = tier_list[i][1]
        # if annotation == 'L':
        #     new_list.append(tier_list[i])
        # if annotation is not None:
        #     if 'V-' in annotation:
        #         new_list.append(tier_list[i])
        if annotation is not None:
            if 'AttL-' in annotation:
                new_list.append(tier_list[i])

        i += 1

    return new_list


def get_annotation_form(root, annotations_list, detail_list):
    new_list = [annotations_list[0]]
    i = 1
    while i < len(detail_list):
        annotation_ref = detail_list[i][0]  # annotation ref
        j = 1
        while j < len(annotations_list):
            if annotation_ref == annotations_list[j][0]:  # annotation id
                time_value1, time_value2 = get_time_values(root, annotation_ref)
                new_list.append([annotations_list[j][1], time_value1[0], time_value2[0]]) # detail_list[0][0] + '-' +
            j += 1
        i += 1

    return new_list


def get_relevant_annotation(practice_tier, annotation_list):  # relevant annotation reference to practice
    new_list = []

    i = 1
    while i < len(practice_tier):
        time_stamp1 = practice_tier[i][2]
        time_stamp2 = practice_tier[i][3]
        j = 1
        words = []
        while j < len(annotation_list):
            ts1 = annotation_list[j][1]
            ts2 = annotation_list[j][2]

            if int(ts1) >= int(time_stamp1) and int(ts2) <= int(time_stamp2):
                words.append(annotation_list[j][0])

            j += 1

        if len(words) != 0:
            new_list.append([annotation_list[0][0], practice_tier[i][1],
                             time_stamp1, time_stamp2, words])

        i += 1

    return new_list


def get_practice_time(root, practice_list):
    new_list = []

    i = 1
    while i < len(practice_list):
        annotation_ref = practice_list[i][0]
        time_value1, time_value2 = get_time_values(root, annotation_ref)
        new_list.append([practice_list[0][0], practice_list[i][1], time_value1[0], time_value2[0]])
        i += 1

    return new_list


def add_form_moretoref(form_tier, moretoref):
    print(form_tier)
    print(moretoref)
    new_form = [form_tier[0]]

    i = 1
    while i < len(form_tier):
        ts1 = form_tier[i][1]
        ts2 = form_tier[i][2]

        j = 1
        while j < len(moretoref):
            ts1_ = moretoref[j][1]
            ts2_ = moretoref[j][2]

            if ts1 == ts1_ and ts2 == ts2_:
                new_form.append([form_tier[i][0] + '-' + moretoref[j][0], ts1, ts2])
            j += 1
        i += 1

    return new_form


def get_time(root, moretoref):
    new_list = [moretoref[0]]
    i = 1
    while i < len(moretoref):
        annotation_id = moretoref[i][0]
        ts1, ts2 = get_time_values(root, annotation_id)
        new_list.append([moretoref[i][1], ts1[0], ts2[0]])
        i += 1
    return new_list


def get_landmark_annotations(filename):
    root = get_xml_data(filename)
    a_lm, b_lm, d_lm = parse_tier(root, 'Detail')
    a_form, b_form, d_form = parse_tier(root, 'Form')

    a_lm = filter_annotation(a_lm)
    b_lm = filter_annotation(b_lm)
    d_lm = filter_annotation(d_lm)
    new_a = get_annotation_form(root, a_form, a_lm)
    new_b = get_annotation_form(root, b_form, b_lm)
    new_d = get_annotation_form(root, d_form, d_lm)

    a_moretoref, b_moretoref, d_moretoref = get_moretoref(filename)
    a_moretoref = get_time(root, a_moretoref)
    b_moretoref = get_time(root, b_moretoref)
    d_moretoref = get_time(root, d_moretoref)

    new_a_ = add_form_moretoref(new_a, a_moretoref)
    new_b_ = add_form_moretoref(new_b, b_moretoref)
    new_d_ = add_form_moretoref(new_d, d_moretoref)

    return new_a_, new_b_, new_d_


def get_moretoref(filename):
    root = get_xml_data(filename)
    a_moretoref, b_moretoref, d_moretoref = parse_tier(root, 'MoreToRef')
    all_moretoref = [a_moretoref, b_moretoref, d_moretoref]
    all_new_list = []
    j = 0
    while j < len(all_moretoref):
        tier_list = all_moretoref[j]
        new_list = [tier_list[0]]
        i = 1
        while i < len(tier_list):
            annotation = tier_list[i][1]
            if annotation is not None:
                if 'L-' in annotation:
                    new_list.append(tier_list[i])
            i += 1
        all_new_list.append(new_list)
        j += 1

    return all_new_list


def get_practice(filename):
    root = get_xml_data(filename)
    a_practice, b_practice, d_practice = parse_tier(root, 'Practice')
    a_practice_time = get_practice_time(root, a_practice)
    b_practice_time = get_practice_time(root, b_practice)
    d_practice_time = get_practice_time(root, d_practice)
    return a_practice_time, b_practice_time, d_practice_time


def count_dialogs_containing_construct(all_practice_form, construction_practice_):
    number = 0
    i = 0
    while i < len(all_practice_form):
        practice_form_construction = extract_construction_from_practice_form(all_practice_form[i][1])
        counter = 0
        j = 1
        while j < len(practice_form_construction):
            if construction_practice_ in practice_form_construction[j]:
                counter += 1
            j += 1
        if counter != 0:
            number += 1
        i += 1

    return number


def check_annotation(val_list, anno_value):
    i = 0
    while i < len(val_list):
        if anno_value == val_list[i][0]:
            return False
        i += 1
    return True


def count_words_in_list(list, word):
    counter = 0
    i = 0
    while i < len(list):
        if word in list[i]:
            counter += 1
        i += 1
    return counter


def count_form_construct(form):
    frequency_construction_ = []
    i = 0
    while i < len(form):  # z.B. indexing-Kapelle
        j = 1
        while j < len(form[i]):
            frequency_construction_.append(form[i][j][0])
            j += 1
        i += 1

    frequency_construction = []
    k = 0
    while k < len(frequency_construction_):
        anno = frequency_construction_[k]
        if check_annotation(frequency_construction, anno):
            frequency_construction.append([frequency_construction_[k],
                                           count_words_in_list(frequency_construction_, frequency_construction_[k])])
        k += 1

    return frequency_construction


def extract_construction_from_practice_form(practice_form):
    construction = []

    i = 0
    while i < len(practice_form):  # z.B. indexing-Kapelle
        j = 1
        while j < len(practice_form[i]):
            k = 0
            while k < len(practice_form[i][j][4]):
                construction_ = practice_form[i][j][1] + '-' + practice_form[i][j][4][k]
                construction.append([practice_form[i][j][0], construction_, practice_form[i][j][2],
                                     practice_form[i][j][3]])
                k += 1
            j += 1
        i += 1

    only_construction = []
    n = 0
    while n < len(construction):
        only_construction.append(construction[n][1])
        n += 1

    # count frequency
    m = 0
    while m < len(construction):
        word = construction[m][1]
        frequeny = count_words_in_list(only_construction, word)
        construction[m].append(frequeny)
        m += 1

    #print(construction)
    return construction


# tf(Indexing - Kapelle) = frequency_Indexing - Kapelle / frequency_Kapelle
# idf(Indexing - Kapelle) = log(1 + (Number_of_Dialogs_containing_Indexing_Kapelle / total_num_of_dialogs_used))
# tf - idf = tf * idf \ in [0, 1]
def calc_td_idf(all_practice_form, construction_practice_, frequency_practice_lm, frequency_lm):
    tf = float(frequency_practice_lm) / float(frequency_lm)

    num = count_dialogs_containing_construct(all_practice_form, construction_practice_)
    calc1 = 1 + (float(num) / float(TOTAL_NUM_OF_DIALOGS))
    idf = np.log(calc1)

    tf_idf_ = tf * idf
    tf_idf = np.linalg.norm(tf_idf_)  # in [0,1]

    return tf_idf


def calculation(form, practice_form):
    i = 0
    while i < len(form):
        construction_tf_idf = []
        frequency_form = count_form_construct(form[i][1])
        practice_form_construction = extract_construction_from_practice_form(practice_form[i][1])
        j = 0
        while j < len(practice_form_construction):
            construction_practice_lm = practice_form_construction[j][1]
            frequency_practice_lm = practice_form_construction[j][4]
            if frequency_practice_lm > 1:
                k = 0
                while k < len(frequency_form):
                    if frequency_form[k][0] in construction_practice_lm:
                        frequency_lm = frequency_form[k][1]
                        td_idf = calc_td_idf(practice_form, construction_practice_lm,
                                             frequency_practice_lm, frequency_lm)
                        construction_tf_idf.append([practice_form_construction[j][0],
                                                    construction_practice_lm,
                                                    practice_form_construction[j][2],
                                                    practice_form_construction[j][3], td_idf])
                        k = len(frequency_form)
                    k += 1
            j += 1
        i += 1

        print(construction_tf_idf)
        convert_to_csv(construction_tf_idf, i)


def get_verbs_time(root, verbs_list):
    new_list = [verbs_list[0]]
    i = 1
    while i < len(verbs_list):
        annotation_ref = verbs_list[i][0]
        time_value1, time_value2 = get_time_values(root, annotation_ref)
        new_list.append([verbs_list[i][1], time_value1[0], time_value2[0]])
        i += 1

    return new_list


def get_verbs(filename):
    root = get_xml_data(filename)
    a_moretoref, b_moretoref, d_moretoref = parse_tier(root, 'MoreToRef')

    a_moretoref = filter_annotation(a_moretoref)
    b_moretoref = filter_annotation(b_moretoref)
    d_moretoref = filter_annotation(d_moretoref)
    new_a = get_verbs_time(root, a_moretoref)
    new_b = get_verbs_time(root, b_moretoref)
    new_d = get_verbs_time(root, d_moretoref)

    return new_a, new_b, new_d


def get_from_all_dialogs():
    all_form = []
    all_practice_form = []

    i = 0
    while i < TOTAL_NUM_OF_DIALOGS:
        a_form, b_form, d_form = get_landmark_annotations(FILES_NAMES[i])
        form_tier = [a_form, b_form, d_form]
        all_form.append([i+1, form_tier])
        print(a_form)

        a_practice, b_practice, d_practice = get_practice(FILES_NAMES[i])
        a_practice_form = get_relevant_annotation(a_practice, a_form)
        b_practice_form = get_relevant_annotation(b_practice, b_form)
        d_practice_form = get_relevant_annotation(d_practice, d_form)
        practice_form_ = [a_practice_form, b_practice_form, d_practice_form]
        all_practice_form.append([i+1, practice_form_])

        i += 1

    calculation(all_form, all_practice_form)


if __name__ == "__main__":
    get_from_all_dialogs()
