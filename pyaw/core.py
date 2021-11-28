# made by @ninjamar (https://github.com/ninjamar)
import subprocess
import ctypes
import os
from .errors import ProcessFailedError

def gen_options(d:dict) -> str:
    """

    :param d:dict: 

    """
    opt_list = []
    for key,value in d.items():
        opt_list.append(f'-{key} {value} ')
    return ''.join(opt_list)

def load_asm(
    spath:str,
    exported_data:list,
    assembler_options:dict={'f':'elf64','o':'pyaw_lib.o'},
    compiler_options:dict={'o':'pyaw_lib.so','shared':''},
    clear:bool=True,
    cpp_file_path:str=f'{os.getcwd()}/pyaw_bind.cpp',
    compiler:str='g++',
    assembler:str='nasm'
) -> ctypes.CDLL:
    """
    :param spath:str: 
    :param exported_data:list: 
    :param assembler_options:dict:  (Default value = {'f':'elf64')
    :param 'o':'pyaw_lib.o'}: 
    :param compiler_options:dict:  (Default value = {'o':'pyaw_lib.so')
    :param 'shared':''}: 
    :param clear:bool:  (Default value = True)
    :param cpp_file_path:str:  (Default value = f'{os.getcwd()}/pyaw_bind.cpp')
    :param compiler:str:  (Default value = 'g++')
    :param assembler:str:  (Default value = 'nasm')

    """
    
    nasm_exec_command = f'{assembler} {gen_options(assembler_options)} {spath}'

    cpp_contents_start = 'extern "C" {'
    cpp_contents_end = '}' 
    cpp_functions = []

    for item in exported_data:
        name = item[0]
        argtypes = item[1]
        returntype = item[2]

        if argtypes == []:
            cpp_functions.append(f'{returntype} {name}();')
        else:
            arg_input = []
            for i in range(len(argtypes)):
                arg_input.append(f'{argtypes[i]} arg{i},')
            arg_input = ''.join(arg_input)
            arg_input = arg_input[:-1]
            cpp_functions.append(f'{returntype} {name}({arg_input});')

    cpp_functions = ''.join(cpp_functions)
    cpp_code = f'{cpp_contents_start}{cpp_functions}{cpp_contents_end}'
    cpp_exec_command = f'{compiler} {gen_options(compiler_options)} {cpp_file_path} {assembler_options["o"]}'
    
    with open(cpp_file_path,'w') as f:
        f.write(cpp_code)

    p = subprocess.Popen(
        '/bin/bash',
        shell=True,
        stdout=subprocess.PIPE,
        stdin=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    p.stdin.write(f'{nasm_exec_command}\n'.encode('utf-8'))
    
    p.stdin.write(f'{cpp_exec_command}\n'.encode('utf-8'))
    
    out,err = p.communicate()

    if p.returncode != 0:
        raise ProcessFailedError(f'Process failed: "{err.decode("utf-8")}"')
    
    clib = ctypes.CDLL(f'{os.getcwd()}/pyaw_lib.so')
    type_map = {'int':ctypes.c_int}
    for info in exported_data:
        func_name = info[0]
        return_type = info[2]
        getattr(clib,func_name).argtypes = [type_map[i] for i in info[1]]
        getattr(clib,func_name).restype = type_map[return_type]
    if clear:
        for file in [assembler_options['o'],compiler_options['o'],'pyaw_bind.cpp']:
            os.remove(file)
    return clib
