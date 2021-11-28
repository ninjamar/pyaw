import setuptools

with open("README.md", "r") as f:
  long_description = f.read()

setuptools.setup(
	name='pyaw',
  	version='0.0.2',
  	description='Python Assembly Wrapper',
  	author='ninjamar',
  	url='https://github.com/ninjamar/pyaw',
  	packages=['pyaw'],
	long_description=long_description,
	long_description_content_type="text/markdown",
	license_files = ("LICENSE",),
	python_requires='>=3.7',  
)
