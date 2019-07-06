"""This script prompts the user for the name of an output file produced by
the SSTP program and writes the file's data to a JSON file.
"""

import os
import csv
import json
#import argparse

def read_csv(csv_file_name):
    lines_list = []
    with open(csv_file_name, 'r') as fin:
        for line in fin.readlines():
            lines_list.append(line)
    return lines_list

def create_output(lines):
    # TODO: fix this entire method.

    output = {}
    output['ae1'] = lines[9][5:-1]
    output['ae3'] = lines[10][5:-1]
    output['%nuc_at_start'] = lines[11][22:-1]
    output['%nuc_at_finish'] = lines[12][23:-1]
    output['astm'] = lines[14][30:-1]
    output['diameter'] = lines[15][27:-4]

    ttt_ferrite_nuc_time = []
    ttt_ferrite_nuc_temp = []
    ttt_ferrite_comp_time = []
    ttt_ferrite_comp_temp = []
    ttt_pearlite_nuc_time = []
    ttt_pearlite_nuc_temp = []
    ttt_pearlite_comp_time = []
    ttt_pearlite_comp_temp = []
    ttt_bainite_nuc_time = []
    ttt_bainite_nuc_temp = []
    ttt_bainite_comp_time = []
    ttt_bainite_comp_temp = []
    ttt_martensite_nuc_time = []
    ttt_martensite_nuc_temp = []

    line_num = 24
    while lines[line_num][0] != ' ':
        line = lines[line_num].split(", ")
        ttt_ferrite_nuc_time.append(line[0])
        ttt_ferrite_nuc_temp.append(line[1])
        ttt_ferrite_comp_time.append(line[2])
        ttt_ferrite_comp_temp.append(line[3])
        ttt_pearlite_nuc_time.append(line[4])
        ttt_pearlite_nuc_temp.append(line[5])
        ttt_pearlite_comp_time.append(line[6])
        ttt_pearlite_comp_temp.append(line[7])
        ttt_bainite_nuc_time.append(line[8])
        ttt_bainite_nuc_temp.append(line[9])
        ttt_bainite_comp_time.append(line[10])
        ttt_bainite_comp_temp.append(line[11])
        ttt_martensite_nuc_time.append(line[12])
        ttt_martensite_nuc_temp.append(line[13][:-1])
        line_num += 1

    output['ttt_ferrite_nuc_time'] = ttt_ferrite_nuc_time
    output['ttt_ferrite_nuc_temp'] = ttt_ferrite_nuc_temp
    output['ttt_ferrite_comp_temp'] = ttt_ferrite_comp_temp
    output['ttt_ferrite_comp_time'] = ttt_ferrite_comp_time
    output['ttt_pearlite_nuc_time'] = ttt_pearlite_nuc_time
    output['ttt_pearlite_nuc_temp'] = ttt_pearlite_nuc_temp
    output['ttt_pearlite_comp_time'] = ttt_pearlite_comp_time
    output['ttt_pearlite_comp_temp'] = ttt_pearlite_comp_temp
    output['ttt_bainite_nuc_time'] = ttt_bainite_nuc_time
    output['ttt_bainite_nuc_temp'] = ttt_bainite_nuc_temp
    output['ttt_bainite_comp_time'] = ttt_bainite_comp_time
    output['ttt_bainite_comp_temp'] = ttt_bainite_comp_temp
    output['ttt_martensite_nuc_time'] = ttt_martensite_nuc_time
    output['ttt_martensite_nuc_temp'] = ttt_martensite_nuc_temp

    cct_ferrite_nuc_time = []
    cct_ferrite_nuc_temp = []
    cct_ferrite_comp_time = []
    cct_ferrite_comp_temp = []
    cct_pearlite_nuc_time = []
    cct_pearlite_nuc_temp = []
    cct_pearlite_comp_time = []
    cct_pearlite_comp_temp = []
    cct_bainite_nuc_time = []
    cct_bainite_nuc_temp = []
    cct_bainite_comp_time = []
    cct_bainite_comp_temp = []
    cct_martensite_nuc_time = []
    cct_martensite_nuc_temp = []

    line_num += 6

    while lines[line_num][0] != ' ' and line_num < (len(lines)-1):
        line = lines[line_num].split(", ")
        cct_ferrite_nuc_time.append(line[0])
        cct_ferrite_nuc_temp.append(line[1])
        cct_ferrite_comp_time.append(line[2])
        cct_ferrite_comp_temp.append(line[3])
        cct_pearlite_nuc_time.append(line[4])
        cct_pearlite_nuc_temp.append(line[5])
        cct_pearlite_comp_time.append(line[6])
        cct_pearlite_comp_temp.append(line[7])
        cct_bainite_nuc_time.append(line[8])
        cct_bainite_nuc_temp.append(line[9])
        cct_bainite_comp_time.append(line[10])
        cct_bainite_comp_temp.append(line[11])
        cct_martensite_nuc_time.append(line[12])
        cct_martensite_nuc_temp.append(line[13][:-1])
        line_num += 1

    output['cct_ferrite_nuc_time'] = cct_ferrite_nuc_time
    output['cct_ferrite_nuc_temp'] = cct_ferrite_nuc_temp
    output['cct_ferrite_comp_temp'] = cct_ferrite_comp_temp
    output['cct_ferrite_comp_time'] = cct_ferrite_comp_time
    output['cct_pearlite_nuc_time'] = cct_pearlite_nuc_time
    output['cct_pearlite_nuc_temp'] = cct_pearlite_nuc_temp
    output['cct_pearlite_comp_time'] = cct_pearlite_comp_time
    output['cct_pearlite_comp_temp'] = cct_pearlite_comp_temp
    output['cct_bainite_nuc_time'] = cct_bainite_nuc_time
    output['cct_bainite_nuc_temp'] = cct_bainite_nuc_temp
    output['cct_bainite_comp_time'] = cct_bainite_comp_time
    output['cct_bainite_comp_temp'] = cct_bainite_comp_temp
    output['cct_martensite_nuc_time'] = cct_martensite_nuc_time
    output['cct_martensite_nuc_temp'] = cct_martensite_nuc_temp

    return output

def write_json(output, file_name):
    with open(file_name, 'w') as fout:
        json.dump(output, fout)

def main():
    # TODO: Add code to take in file name through arguments
    #csv_file_name = input("Enter file name: ")
    csv_file_name = "TTT and CCT results.csv"
    lines = read_csv(csv_file_name)
    output = create_output(lines)
    write_json(output, 'TTT and CCT2.json')

if __name__ == '__main__':
    main()