"""This script prompts the user for the name of an output file produced by
the SSTP program and writes the file's data to a JSON file."""

import json

INPUT_FILE_NAME = input('Enter input file name: ')
OUTPUT_FILE_NAME = input('Enter output file name: ')
#INPUT_FILE_NAME = 'TTT and CCT results.csv'
#OUTPUT_FILE_NAME = 'TTT and CCT.json'

with open(INPUT_FILE_NAME, 'r') as file_in:
    #skip header information
    for i in range(1, 11):
        line = file_in.readline()

    #Set Ae1
    ae1 = line[5:-1]

    #Read and Set Ae3
    line = file_in.readline()
    ae3 = line[5:-1]

    #Read and set nucleation at start
    line = file_in.readline()
    nucleation_at_start = line[22:-1]

    #Read and set nucleation at finish
    line = file_in.readline()
    nucleation_at_finish = line[23:-1]

    #Skip blank line
    file_in.readline()

    #Read and set ASTM median prior grain size
    line = file_in.readline()
    astm = line[30:-1]

    #Read and set Diameter prior grain size
    line = file_in.readline()
    diameter = line[27:-4]

    #Skip 2 blank lines
    file_in.readline()
    file_in.readline()

    #Read and set Initial CCT temperature
    line = file_in.readline()
    initial_cct_temp = line[25:-3]

    #Skip 5 lines
    for i in range(5):
        file_in.readline()

    #Create arrays
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

    #Read time/temp data
    line = file_in.readline()
    while len(line) > 5:
        line_split = line.split(', ')
        ttt_ferrite_nuc_time.append(line_split[0])
        ttt_ferrite_nuc_temp.append(line_split[1])
        ttt_ferrite_comp_time.append(line_split[2])
        ttt_ferrite_comp_temp.append(line_split[3])
        ttt_pearlite_nuc_time.append(line_split[4])
        ttt_pearlite_nuc_temp.append(line_split[5])
        ttt_pearlite_comp_time.append(line_split[6])
        ttt_pearlite_comp_temp.append(line_split[7])
        ttt_bainite_nuc_time.append(line_split[8])
        ttt_bainite_nuc_temp.append(line_split[9])
        ttt_bainite_comp_time.append(line_split[10])
        ttt_bainite_comp_temp.append(line_split[11])
        ttt_martensite_nuc_time.append(line_split[12])
        ttt_martensite_nuc_temp.append((line_split[13])[:-1])
        line = file_in.readline()

    # Skip 5 lines
    for i in range(5):
        file_in.readline()

    # Create arrays
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

    # Read time/temp data
    line = file_in.readline()
    while len(line) > 5:
        line_split = line.split(', ')

        cct_ferrite_nuc_time.append(line_split[0])
        cct_ferrite_nuc_temp.append(line_split[1])
        cct_ferrite_comp_time.append(line_split[2])
        cct_ferrite_comp_temp.append(line_split[3])
        cct_pearlite_nuc_time.append(line_split[4])
        cct_pearlite_nuc_temp.append(line_split[5])
        cct_pearlite_comp_time.append(line_split[6])
        cct_pearlite_comp_temp.append(line_split[7])
        cct_bainite_nuc_time.append(line_split[8])
        cct_bainite_nuc_temp.append(line_split[9])
        cct_bainite_comp_time.append(line_split[10])
        cct_bainite_comp_temp.append(line_split[11])
        cct_martensite_nuc_time.append(line_split[12])
        cct_martensite_nuc_temp.append((line_split[13])[:-1])
        line = file_in.readline()

    file_in.close()

with open(OUTPUT_FILE_NAME, 'w') as file_out:
    file_out.write('{\n')

    #Write Ae1
    file_out.write('\t"Ae1" : ')
    json.dump(ae1, file_out)
    file_out.write(',\n')

    #Write Ae3
    file_out.write('\t"Ae3" : ')
    json.dump(ae3, file_out)
    file_out.write(',\n')

    #Write %nucleation at start
    file_out.write('\t"% nucleation at start" : ')
    json.dump(nucleation_at_start, file_out)
    file_out.write(',\n')

    #Write %nucleation at finish
    file_out.write('\t"% nucleation at finish" : ')
    json.dump(nucleation_at_finish, file_out)
    file_out.write(',\n')

    #Write ASTM median prior grain size
    file_out.write('\t"ASTM mediam prior grain size" : ')
    json.dump(astm, file_out)
    file_out.write(',\n')

    #Write diameter prior grain size
    file_out.write('\t"Diameter prior grain size" : ')
    json.dump(diameter, file_out)
    file_out.write(',\n')

    #Write initial cct temp
    file_out.write('\t"Initial CCT temperature " : ')
    json.dump(initial_cct_temp, file_out)
    file_out.write(',\n')

    #Write TTT data
    file_out.write('\t"TTT Data" : {\n')

    #Write TTT ferrite-nuc
    file_out.write('\t\t"Ferrite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(ttt_ferrite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(ttt_ferrite_nuc_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write TTT ferrite-comp
    file_out.write('\t\t"Ferrite-comp" : {\n\t\t\t"temp" : ')
    json.dump(ttt_ferrite_comp_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(ttt_ferrite_comp_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write TTT pearlite-nuc
    file_out.write('\t\t"Pearlite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(ttt_pearlite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(ttt_pearlite_nuc_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write TTT pearlite-comp
    file_out.write('\t\t"Pearlite-comp" : {\n\t\t\t"temp" : ')
    json.dump(ttt_pearlite_comp_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(ttt_pearlite_comp_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write TTT bainite-nuc
    file_out.write('\t\t"Bainite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(ttt_bainite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(ttt_bainite_nuc_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write TTT bainite-comp
    file_out.write('\t\t"Bainite-comp" : {\n\t\t\t"temp" : ')
    json.dump(ttt_bainite_comp_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(ttt_bainite_comp_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write TTT martensite-nuc
    file_out.write('\t\t"Martensite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(ttt_martensite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(ttt_martensite_nuc_time, file_out)
    file_out.write('\n\t\t}\n')

    file_out.write('\t},\n')

    #Write CCT data
    file_out.write('\t"CCT Data" : {\n')

    #Write CCT ferrite-nuc
    file_out.write('\t\t"Ferrite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(cct_ferrite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(cct_ferrite_nuc_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write CCT ferrite-comp
    file_out.write('\t\t"Ferrite-comp" : {\n\t\t\t"temp" : ')
    json.dump(cct_ferrite_comp_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(cct_ferrite_comp_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write CCT pearlite-nuc
    file_out.write('\t\t"Pearlite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(cct_pearlite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(cct_pearlite_nuc_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write CCT pearlite-comp
    file_out.write('\t\t"Pearlite-comp" : {\n\t\t\t"temp" : ')
    json.dump(cct_pearlite_comp_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(cct_pearlite_comp_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write CCT bainite-nuc
    file_out.write('\t\t"Bainite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(cct_bainite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(cct_bainite_nuc_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write CCT bainite-comp
    file_out.write('\t\t"Bainite-comp" : {\n\t\t\t"temp" : ')
    json.dump(cct_bainite_comp_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(cct_bainite_comp_time, file_out)
    file_out.write('\n\t\t},\n')

    #Write CCT martensite-nuc
    file_out.write('\t\t"Martensite-nuc" : {\n\t\t\t"temp" : ')
    json.dump(cct_martensite_nuc_temp, file_out)
    file_out.write(',\n\t\t\t"time" : ')
    json.dump(cct_martensite_nuc_time, file_out)
    file_out.write('\n\t\t}\n')

    file_out.write('\t}\n}\n')

    file_out.close()
