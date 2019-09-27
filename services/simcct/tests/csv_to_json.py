# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------------------------------------------------
# arclytics_sim
# middleware.py
#
# Attributions:
# [1]
# ----------------------------------------------------------------------------------------------------------------------
__author__ = ['David Matthews <@tree1004>']
__license__ = 'MIT'
__version__ = '0.1.0'
__status__ = 'development'
__date__ = '2019.07.06'
"""
This script prompts the user for the name of an output file produced by
the SSTP program and writes the file's data to a JSON file.
"""

import json
import argparse

parser = argparse.ArgumentParser(
    description='Convert SSTP results CSV to JSON'
)
parser.add_argument(
    '-i',
    dest='input_file',
    type=str,
    metavar='',
    help='Name of input SSTP CSV file'
)
parser.add_argument(
    '-o',
    dest='output_file',
    type=str,
    metavar='',
    help='Name of output JSON file'
)
args = parser.parse_args()


def read_csv(csv_file_name: str) -> str:
    """Read the SSTP csv file and return a list of the lines from the file."""
    with open(csv_file_name, 'r') as fin:
        return fin.readlines()


def create_output(lines: str) -> dict:
    """Read a list of lines from SSTP csv and create a dictionary
    to be dumped into json file.
    """
    # Create dictionary to hold output to be written to json file.
    output = {}

    # Set the values for Ae1, Ae3 ... in the dictionary
    output['ae1'] = lines[9][5:-1]
    output['ae3'] = lines[10][5:-1]
    output['%nuc_at_start'] = lines[11][22:-1]
    output['%nuc_at_finish'] = lines[12][23:-1]
    output['astm'] = lines[14][30:-1]
    output['diameter'] = lines[15][27:-4]
    output['initial_cct_temp'] = lines[18][25:-3]

    # Create dictionaries for ttt nuc/comp time/temp data
    # Initialise dictionaries as lists
    ttt_ferrite_nuc = {}
    ttt_ferrite_nuc['time'] = []
    ttt_ferrite_nuc['temp'] = []
    ttt_ferrite_comp = {}
    ttt_ferrite_comp['time'] = []
    ttt_ferrite_comp['temp'] = []
    ttt_pearlite_nuc = {}
    ttt_pearlite_nuc['time'] = []
    ttt_pearlite_nuc['temp'] = []
    ttt_pearlite_comp = {}
    ttt_pearlite_comp['time'] = []
    ttt_pearlite_comp['temp'] = []
    ttt_bainite_nuc = {}
    ttt_bainite_nuc['time'] = []
    ttt_bainite_nuc['temp'] = []
    ttt_bainite_comp = {}
    ttt_bainite_comp['time'] = []
    ttt_bainite_comp['temp'] = []
    ttt_martensite_nuc = {}
    ttt_martensite_nuc['time'] = []
    ttt_martensite_nuc['temp'] = []

    # Add all time/temp data to time/temp lists within ttt dictionaries
    line_num = 24
    while lines[line_num][0] != ' ':
        line = lines[line_num].split(", ")
        ttt_ferrite_nuc['time'].append(line[0])
        ttt_ferrite_nuc['temp'].append(line[1])
        ttt_ferrite_comp['time'].append(line[2])
        ttt_ferrite_comp['temp'].append(line[3])
        ttt_pearlite_nuc['time'].append(line[4])
        ttt_pearlite_nuc['temp'].append(line[5])
        ttt_pearlite_comp['time'].append(line[6])
        ttt_pearlite_comp['temp'].append(line[7])
        ttt_bainite_nuc['time'].append(line[8])
        ttt_bainite_nuc['temp'].append(line[9])
        ttt_bainite_comp['time'].append(line[10])
        ttt_bainite_comp['temp'].append(line[11])
        ttt_martensite_nuc['time'].append(line[12])
        ttt_martensite_nuc['temp'].append(line[13][:-1])
        line_num += 1

    # Put ttt dictionaries into main output dictionary
    output['ttt_ferrite_nuc'] = ttt_ferrite_nuc
    output['ttt_ferrite_comp'] = ttt_ferrite_comp
    output['ttt_pearlite_nuc'] = ttt_pearlite_nuc
    output['ttt_pearlite_comp'] = ttt_pearlite_comp
    output['ttt_bainite_nuc'] = ttt_bainite_nuc
    output['ttt_bainite_comp'] = ttt_bainite_comp
    output['ttt_martensite_nuc'] = ttt_martensite_nuc

    # Create dictionaries for cct nuc/comp time/temp data
    # Initialise dictionaries as lists
    cct_ferrite_nuc = {}
    cct_ferrite_nuc['time'] = []
    cct_ferrite_nuc['temp'] = []
    cct_ferrite_comp = {}
    cct_ferrite_comp['time'] = []
    cct_ferrite_comp['temp'] = []
    cct_pearlite_nuc = {}
    cct_pearlite_nuc['time'] = []
    cct_pearlite_nuc['temp'] = []
    cct_pearlite_comp = {}
    cct_pearlite_comp['time'] = []
    cct_pearlite_comp['temp'] = []
    cct_bainite_nuc = {}
    cct_bainite_nuc['time'] = []
    cct_bainite_nuc['temp'] = []
    cct_bainite_comp = {}
    cct_bainite_comp['time'] = []
    cct_bainite_comp['temp'] = []
    cct_martensite_nuc = {}
    cct_martensite_nuc['time'] = []
    cct_martensite_nuc['temp'] = []

    # Skip cct header
    line_num += 6

    # Add all time/temp data to time/temp lists within cct dictionaries
    while lines[line_num][0] != ' ' and line_num < (len(lines) - 1):
        line = lines[line_num].split(", ")
        cct_ferrite_nuc['time'].append(line[0])
        cct_ferrite_nuc['temp'].append(line[1])
        cct_ferrite_comp['time'].append(line[2])
        cct_ferrite_comp['temp'].append(line[3])
        cct_pearlite_nuc['time'].append(line[4])
        cct_pearlite_nuc['temp'].append(line[5])
        cct_pearlite_comp['time'].append(line[6])
        cct_pearlite_comp['temp'].append(line[7])
        cct_bainite_nuc['time'].append(line[8])
        cct_bainite_nuc['temp'].append(line[9])
        cct_bainite_comp['time'].append(line[10])
        cct_bainite_comp['temp'].append(line[11])
        cct_martensite_nuc['time'].append(line[12])
        cct_martensite_nuc['temp'].append(line[13][:-1])
        line_num += 1

    # Put cct dictionaries into main output dictionary
    output['cct_ferrite_nuc'] = cct_ferrite_nuc
    output['cct_ferrite_comp'] = cct_ferrite_comp
    output['cct_pearlite_nuc'] = cct_pearlite_nuc
    output['cct_pearlite_comp'] = cct_pearlite_comp
    output['cct_bainite_nuc'] = cct_bainite_nuc
    output['cct_bainite_comp'] = cct_bainite_comp
    output['cct_martensite_nuc'] = cct_martensite_nuc

    return output


def write_json(output: {}, file_name: str):
    """Dump data dictionary into output file in json format."""
    with open(file_name, 'w') as fout:
        json.dump(output, fout)


def main():
    if args.input_file:
        lines = read_csv(args.input_file)
    else:
        csv_file_name = input("Enter input file name: ")
        lines = read_csv(csv_file_name)
    output = create_output(lines)
    if args.output_file:
        write_json(output, args.output_file)
    else:
        json_file_name = input("Enter output file name: ")
        write_json(output, json_file_name)


if __name__ == '__main__':
    main()
