# -*- coding:utf-8 -*-
import os,sys
import fileinput
import time

class DependencyItem(object):
    extern_file = ''
    source_file = ''

#build module and files relationship 
#key:module_name value:file_list
def get_file_relation_map(path):
    if path.endswith('/'):
        path = path[:-1]
    file_map = {}
    for dirName, subdirList, fileList in os.walk(path):
        for fname in fileList:
            if fname.endswith('.h') or fname.endswith('.m') or fname.endswith('.mm'):
                module_name = dirName.split(path)[1]
                if dirName != path:
                    module_name = dirName.split(path + '/')[1]
                if len(module_name) == 0:
                    module_name = path.split('/')[-1]
                if '/' in module_name:
                    module_name = module_name.split('/')[0]

                list = []
                if file_map.has_key(module_name):
                    list = file_map[module_name]
                full_path = '%s/%s' % (dirName,fname)
                if full_path not in list:
                    list.append(full_path)
                file_map[module_name] = list
    return file_map

#get import list from source_file
def get_import_files(source_file):
    import_files = []
    for line in fileinput.input(source_file):
        if '#import' in line and '//' not in line:
            file = line.split('#import')[1]
            if '<' in file:
                file = file.split('<')[1].split('>')[0]
                if '/' in file:
                    file = file.split('/')[1]
            elif '"' in file:
                file = file.split('"')[1]
            import_files.append(file)
    return import_files

#check if is system import
def is_system_module(module_name):
    list = ['UI','CG','NS','AVFoundation','Foundation']
    for system_prefix in list:
        if module_name.startswith(system_prefix):
            return True
    return False

def get_dependency_map_list(file_map,check_map):
    result_map_list = []
    for index in range(len(file_map)):
        module_name = file_map.keys()[index]
        inner_map = {}
        inner_list = []
        if inner_map.has_key(module_name):
            inner_list = inner_map[module_name]
        inner_map[module_name] = inner_list

        inner_map1 = {}

        module_files = file_map[module_name]
        for module_file in module_files:
            import_files = get_import_files(module_file)
            for import_file in import_files:
                if not is_system_module(import_file):
                    extern_module = ''
                    extern_file = ''
                    if len(check_map) > 0:
                        for check_key in check_map.keys():
                            check_list = check_map[check_key]
                            for check_file in check_list:
                                if check_file.split('/')[-1] == import_file:
                                    extern_module = check_key
                                    extern_file = check_file
                                    break
                            if len(extern_module) > 0 and len(extern_file) > 0:
                                break
                    else:
                        for index2 in range(len(file_map)):
                            module_name2 = file_map.keys()[index2]
                            if module_name == module_name2:
                                continue
                            module_files2 = file_map[module_name2]
                            for module_file2 in module_files2:
                                if module_file2.split('/')[-1] == import_file:
                                    extern_module = module_name2
                                    extern_file = module_file2
                                    break
                            if len(extern_module) > 0 and len(extern_file) > 0:
                                break

                        # if len(extern_module) == 0 and len(extern_file) == 0:
                        #     if import_file.split('.')[0] != module_file.split('/')[-1].split('.')[0]:
                        #         list_a = file_map[module_name]
                        #         is_same_module = 0
                        #         for file_a in list_a:
                        #             if file_a.split('/')[-1] == import_file:
                        #                 is_same_module = 1
                        #         if is_same_module == 0:
                        #             extern_module = 'Other Modules'
                        #             extern_file = import_file

                    if len(extern_module) > 0 and len(extern_file) > 0:
                        item = DependencyItem()
                        item.extern_file = extern_file
                        item.source_file = module_file

                        inner_list1 = []
                        if inner_map1.has_key(extern_module):
                            inner_list1 = inner_map1[extern_module]
                        inner_list1.append(item)
                        inner_map1[extern_module] = inner_list1

        if len(inner_map1) > 0:
            inner_list.append(inner_map1)
        if len(inner_list) > 0:
            result_map_list.append(inner_map)
    return result_map_list

def print_format_map_result(result_map_list):
    for result_map in result_map_list:
        for index in range(len(result_map)):
            module = result_map.keys()[index]
            module_map = result_map.values()[index]
            if len(module_map) > 0:
                print('-模块:%s'%(module))
            for ele_map in module_map:
                for index2 in range(len(ele_map)):
                    extern_module = ele_map.keys()[index2]
                    print('    -跨模块引用了:%s'%(extern_module))
                    extern_list = ele_map.values()[index2]
                    for item in extern_list:
                        extern_file = item.extern_file
                        source_file = item.source_file
                        
                        extern_file = extern_file.split('/')[-1]
                        source_file = source_file.split('/')[-1]
                        print('        -%s <--- %s'%(extern_file,source_file))


def analyse_dependency(source_path,check_path):
    if len(check_path) > 0:
        file_map = get_file_relation_map(source_path)
        check_map = get_file_relation_map(check_path)
        result_map_list = get_dependency_map_list(file_map,check_map)
    else:
        file_map = get_file_relation_map(source_path)
        result_map_list = get_dependency_map_list(file_map,'')
    print_format_map_result(result_map_list)

def start_analyse():
    source_path = ''
    check_path = ''
    if len(sys.argv) > 1:
        source_path = sys.argv[1]
    if len(sys.argv) > 2:
        check_path = sys.argv[2]
    if len(source_path) == 0:
        print("error! source_path can not be empty")
    
    analyse_dependency(source_path, check_path)

start_analyse()


    


