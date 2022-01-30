"""
For my Bachelor - Thesis (Cognitive Computing), WS 21/ 22
This code extract Annotation Values, counting them and specific Tiers from .eaf-files into .csv files as a table

Written by: Kha My Le
Date: 07.01.2022
"""

import xml.etree.ElementTree as ET
import csv

FILES_NAMES = ['26_Anno_Done/29-3.eaf']
               # '29_Anno_Done/26-3.eaf',
               # '48_Anno_Done/48-3.eaf']

# missing filenames: '31_Anno_Done/26-3.eaf', '42_Anno_Done/26-3.eaf'


def parse(filename):
    """
    parsing values of annotation for .eaf-files in list and the names of tiers.
    inspired by: https://stackabuse.com/reading-and-writing-xml-files-in-python/
    :return: all_values: lif of all annotation values, tiers: list of tier names
    """
    tree = ET.parse(filename)
    root = tree.getroot()

    all_values, anno_values, tiers = [], [], []  # declaring lists

    for tier in root.findall('TIER'):  # check which tier in file
        if 'Speech' not in tier.attrib['TIER_ID']:
            if 'Form' not in tier.attrib['TIER_ID']:  # speech/ -form tier aren't annotation tiers I need
                if 'notes' not in tier.attrib['TIER_ID']:  # note tier is not necessary
                    tiers.append(tier.attrib['TIER_ID'])  # saving name of tiers in belonging list
                    for anno in tier:
                        for align_anno in anno:
                            for value in align_anno:  # value: annotation values in current tier
                                anno_values.append(value.text)  # add annotation values in temporary list
                    all_values.append(anno_values)  # add annotation values in belonging list
                    anno_values = []  # clear temporary list

    return all_values, tiers


def convert_matrix(old_matrix):
    """
    for correct format to convert to csv file
    :param old_matrix: list of values in old order
    :return: new_matrix: list of annotation values in 'correct'/ table order
    """
    # creating a 'matrix' of 'None's, this should be an empty matrix to append annotation values to a matrix later,
    # because of Index Out of Bounds/ Range problems
    new_matrix = [[None for c in range(5)] for r in range(200)]  # it's not really efficient

    print(old_matrix)

    i = 0  # declaring counter for loops

    while i < len(old_matrix):  # i: current tier
        j = 0
        while j < len(old_matrix[i]):  # goes through the elements/ annotation values of the tiers
            # matrix [0...][0] = matrix[0][0...]
            # matrix[][i] = matrix[i][0...]
            new_matrix[j][i] = old_matrix[i][j]
            j += 1
        i += 1

    actual_matrix = [[None for c in range(10)] for r in range(200)]

    k, l = 0, 0
    for m in new_matrix:
        for row in m:
            try:
                for value in row:
                    actual_matrix[k][l] = value
                    l += 1
            except TypeError:  # ignore None Types
                actual_matrix[k][l] = None
                actual_matrix[k][l + 1] = None
                l += 2
                pass
        k += 1
        l = 0

    return actual_matrix


def evaluation_annotation(anno_values, tiers):
    """
    'shaping' values of list for evaluation
    :param anno_values:
    :return:
    """

    pract_idx = []
    sent_idx = []
    det_idx = []
    ref_idx = []
    more_ref_idx = []

    i = 0
    while i < len(tiers):  # current tier
        if 'Practice' in tiers[i]:
            pract_idx.append(i)
        elif 'Sentence' in tiers[i]:
            sent_idx.append(i)
        elif 'Detail' in tiers[i]:
            det_idx.append(i)
        elif 'Referent' in tiers[i]:
            ref_idx.append(i)
        elif 'MoreToRef' in tiers[i]:
            more_ref_idx.append(i)
        i += 1

    # valuation lists
    practice = [['Practice-Tier', 'Quantity']] + create_evaluation_list(anno_values, pract_idx)
    sentence = [['Sentence-Tier', 'Quantity']] + create_evaluation_list(anno_values, sent_idx)
    detail = [['Detail-Tier', 'Quantity']] + create_evaluation_list(anno_values, det_idx)
    referent = [['Referent-Tier', 'Quantity']] + create_evaluation_list(anno_values, ref_idx)
    more_to_ref = [['MoreToRef-Tier', 'Quantity']] + create_evaluation_list(anno_values, more_ref_idx)

    all_evaluation_tiers = [practice] + [sentence] + [detail] + [referent] + [more_to_ref]
    return all_evaluation_tiers


def create_evaluation_list(anno_values, idx):
    """
    This method counts the quantity of one annotation value
    :param anno_values:
    :param idx:
    :return:
    """
    k = 0
    values = []
    while k < len(idx):
        values.append(anno_values[idx[k]])
        k += 1

    val = []
    i = 0
    while i < len(values):  # current tier
        j = 0
        while j < len(values[i]):
            anno = values[i][j]  # current annotation to count
            if anno is not None:
                if check_annotation(val, anno):
                    counter = count_words_in_list(values, anno)
                    val_tupel = [anno, counter]
                    val.append(val_tupel)
            j += 1
        i += 1
    return val


def check_annotation(val_list, anno_value):
    """
    Checking if given value already exists in list
    :param val_list:
    :param anno_value:
    :return:
    """
    i = 0
    while i < len(val_list):
        if anno_value == val_list[i][0]:
            return False
        i += 1
    return True


def count_words_in_list(list, word):
    """

    :param list:
    :param word:
    :return:
    """
    counter = 0
    i = 0
    while i < len(list):
        j = 0
        while j < len(list[i]):
            if word == list[i][j]:
                counter += 1
            j += 1
        i += 1
    return counter


def convert_to_csv(toWrite, name):
    """
    converting list to .csv file
    :param toWrite: file to convert to .csv
    :return: nothing
    """
    file = open(str(name) + ".csv", 'w')
    with file:
        writer = csv.writer(file)
        for row in toWrite:
            writer.writerow(row)


def convert_eaf_to_csv():
    """

    :return:
    """
    i = 0
    while i < len(FILES_NAMES):
        list_anno_values, tiers = parse(FILES_NAMES[i])
        eval_anno = evaluation_annotation(list_anno_values, tiers)
        matrix = convert_matrix(eval_anno)
        convert_to_csv(matrix, i)
        i += 1


if __name__ == "__main__":
    print("hi")
    #convert_eaf_to_csv()
