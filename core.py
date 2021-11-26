import subprocess
import ctypes
import os
from .errors import ProcessFailedError

def gen_options(d):
	opt_list = []
	for key,value in d.items():
		opt_list.append(f'-{key} {value} ')
	return ''.join(opt_list)

def load_asm(spath,exported_data,assembler_options={'f':'elf64','o':'pyaw_lib.o'},compiler_options={'o':'pyaw_lib.so','shared':''},clear=True,cpp_file_path='pyaw_bind.cpp',compiler='g++',assembler='nasm'):
	'''
	generate a binding file 
	:spath: assembly (uses nasm ) file to compile
	:nasm_options: dictionary that contains options for nasm
	:exported_data: data about functions exported from {spath}
		- [[name,argtypes,return_type]]
			- argtypes ['int']
	'''
	# does the assembler_options and compiler_options work?
	# please document this code
	# make a python package for this
	# test EVERYTHING
	
	nasm_exec_command = f'{assembler} {gen_options(assembler_options)} {spath}'

	c_contents_start = 'extern "C" {'
	c_contents_end = '}' 
	c_functions = []

	for item in exported_data:
		name = item[0]
		argtypes = item[1]
		returntype = item[2]

		if argtypes == []:
			c_functions.append(f'{returntype} {name}();')
		else:
			arg_input = []
			for i in range(len(argtypes)):
				arg_input.append(f'{argtypes[i]} arg{i},')
			arg_input = ''.join(arg_input)
			arg_input = arg_input[:-1]
			c_functions.append(f'{returntype} {name}({arg_input});')

	c_functions = ''.join(c_functions)
	c_code = f'{c_contents_start}{c_functions}{c_contents_end}'
	cpp_exec_command = f'{compiler} {gen_options(compiler_options)} {cpp_file_path} {assembler_options["o"]}'
	
	with open(cpp_file_path,'w') as f:
		f.write(c_code)

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
		getattr(clib,func_name).argtypes = [type_map[i] for i in info[1]]
	if clear:
		for file in [assembler_options['o'],compiler_options['o'],'pyaw_bind.cpp']:
			os.remove(file)
	return clib