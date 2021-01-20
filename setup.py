from setuptools import setup
import glob
import os

with open('requirements.txt') as f:
    required = [x for x in f.read().splitlines() if not x.startswith("#")]

from podracer import __version__, _program

setup(name=_program,
      version=__version__,
      packages=['podracer'],
      description='Skeleton commandline python project',
      url='https://github.com/Squarles2007/podracer',
      author='F. Davis Quarles',
      author_email='f.davis.quarles@gmail.com',
      license='MIT',
      entry_points="""
      [console_scripts]
      {program} = podracer.command:main
      """.format(program = _program),
      keywords=[],
      tests_require=['pytest', 'coveralls'],
      zip_safe=False)
