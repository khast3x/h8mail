# -*- coding: utf-8 -*-
from .colors import colors as c
import json

def generate_source_arrays(pwned_data):
    data_array = []
    no_src = 0 # To check for data with no explicit source
    temp_array = []
    for i in range(len(pwned_data)):
        if len(pwned_data[i]) == 2:
            temp_array.append(pwned_data[i][0] + ":" + str(pwned_data[i][1]))
            no_src += 1
            if "SOURCE" in pwned_data[i][0]:
                data_array.append(temp_array)
                temp_array = []
                no_src = 0
    if no_src > 0:
        data_array.append(temp_array)
    return data_array



def save_results_json(dest_json, target_obj_list):
    data = {}
    data['targets'] = []
    for t in target_obj_list:
        current_target = {}
        current_target["target"] = t.target
        current_target["pwn_num"] = t.pwned
        current_target["data"] = generate_source_arrays(t.data)
        data['targets'].append(current_target)
    
    with open(dest_json, 'w') as outfile:
        json.dump(data, outfile)