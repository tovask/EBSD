#!/usr/bin/python3
#############
# Adjustable parameters:
#
# The absolute threshold for interpret a value as a misorientation
# (Beside 'absolute', it's can be compared 'relative' eg. to the average.)
thres_abs = 0.7
#
# The number of values should be skipped before find a new misorientation
skip_adjacent = 1
#
############

import glob, re, os, itertools

file_results = {} # parsed and examined values
all_x = {} # all the x values by directories
all_y = {} # all the y values by directories
out_result = {} # rendered values
dirs = []

#######
"Parsing the files and find misorientations"
files = sorted(glob.glob("**/*.txt")) # search for .txt files under directories
for file in files:
    # print('Parsing file:',file)
    with open(file) as csvfile:
        values = []
        for row in csvfile:
            # values delimited by a semicolon
            row = row.split(";")
            if len(row) < 3: # skip description rows (first 7)
                continue
            row = list(map(lambda i: i.strip(),row)) # clear whitespaces
            row = list(filter(lambda i: len(i) > 0,row)) # clear empty values (every line end)
            if len(row) < 3: # skip empty rows (last 3)
                continue
            if row[0] == 'Number': # last row, that contains the average
                # print('\tAvg from file:',float(row[1]),float(row[2]))
                continue
            try:
                row = list(map(lambda i: float(i),row)) # string to float
            except ValueError:
                print('\tValueError!!!',row)
                continue
            values.append(row)
        trans_values = list(map(list, zip(*values)))
        avg = [float(sum(l))/len(l) for l in trans_values][1:]
        # print('\tAvg calculated:',*avg)
        # print([float(sum([i for i in l if i>0]))/len([i for i in l if i>0]) for l in trans_values])
        # -----------
        # The important part:
        misorient = []
        n = 0
        prev_n = -10
        for i in values:
            n += 1
            if i[1] < thres_abs:
                continue
            if prev_n + skip_adjacent >= n:
                continue
            prev_n = n
            misorient.append(i)
        # print('\n'.join(map(lambda i: ', '.join(map(str,i)),misorient)))
        rel_distances = []
        prev_distance = 0
        for row in misorient:
            rel_distances.append([row[0]-prev_distance, row[1]])
            prev_distance = row[0]
        # for row in rel_distances:
        #     out = "; ".join( [str(round(row[0],9)), str(row[1])] )
        #     print(out)
        file_results[file] = rel_distances # save the result
    # end of processing one file

# print(file_results)



#########
"Link corresponding x and y directions"

x_file_re = re.compile(r'(.*_)x(\.txt)$')
y_file_re = re.compile(r'(.*_)y(\.txt)$')
file_number_re = re.compile(r'.*_(\d+)_(?:x|y)\.txt$')
directory_re = re.compile(r'(.*)/[^/]+$')

# error checking
y_files = sorted(list(filter(lambda f: y_file_re.search(f), file_results.keys())))
for y_file in y_files:
    x_file = y_file_re.sub('\\1x\\2',y_file)
    if not os.path.exists(x_file):
        print("Error: missing corresponding y file:", x_file)
        continue
    if x_file not in file_results:
        print("Error: missing corresponding y data:", x_file)
        continue

x_files = sorted(list(filter(lambda f: x_file_re.search(f), file_results.keys())), key = lambda s: int(file_number_re.search(s).group(1)))
for x_file in x_files:
    y_file = x_file_re.sub('\\1y\\2',x_file)
    if not os.path.exists(y_file):
        print("Error: missing corresponding y file:", y_file)
        continue
    if y_file not in file_results:
        print("Error: missing corresponding y data:", y_file)
        continue
    # print(x_file)
    file_number = file_number_re.search(x_file).group(1)
    print(int(file_number_re.search(x_file).group(1)))
    directory = directory_re.search(x_file).group(1)
    if not directory in dirs:
        dirs.append(directory)
    if not directory in out_result:
        out_result[directory] = "Number; Misorientation x; Relative Distance x; Misorientation y; Relative Distance y\n"
    if not directory in all_x:
        all_x[directory] = []
    if not directory in all_y:
        all_y[directory] = []
    out_result[directory] += file_number+'; ; ; ;\n'
    # place x and y results next to each other
    concated = list(itertools.zip_longest(file_results[x_file], file_results[y_file]))
    for row in concated:
        if row[0]:
            x_vals = list(map(lambda i: round(i, 9), row[0][::-1]))
            all_x[directory].append(x_vals)
        else:
            x_vals = ['','']
        if row[1]:
            y_vals = list(map(lambda i: round(i, 9), row[1][::-1]))
            all_y[directory].append(y_vals)
        else:
            y_vals = ['','']
        out_result[directory] += "; ".join(map(str,['']+x_vals+y_vals)) + '\n'

# write out the results
for dir in dirs:
    out_file = open(dir+'/'+'summary_'+dir+'.csv', 'w')
    out_file.write(out_result[dir])
    # transpose lists for caculate the average of each column
    all_x_trans = list(zip(*all_x[dir]))
    all_y_trans = list(zip(*all_y[dir]))
    out_sum = "; ".join(list(map(str,[''] + [float(sum(l))/len(l) for l in all_x_trans] + [float(sum(l))/len(l) for l in all_y_trans] )))
    out_file.write('\n')
    out_file.write(out_sum)
    out_file.close()

