**PY**thon **A**ssembly **W**rapper
## About PYAW
PYAW allows you to call assembly from python

## Installation
`pip install pyaw`
## Example

#### lib.asm
```nasm
global foo
foo:
	mov rax,100
	ret
```
#### main.py
```python3
import pyaw
lib = pyaw.load_asm(
	'lib.asm',
	[
		['foo',[],'int']
	]
)
print(lib.foo()) # this prints 100
```
* The first argument to `pyaw.load_asm` is the file <br>
* The second argument is a list which contains information about the exported function inside `lib.asm`
	* The first item is a list which follows the format of `[function_name,[argument types],returntype]`
		* The only type allowed currently is `int` which can be inputed as `"int"` rather than the class because it gets changed to `ctypes.c_int`
