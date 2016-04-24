#!/usr/bin/env python

from setuptools import setup


setup(name='AquaponicsModeler',
      version='0.1',
      description='A modelling application for aquaponics systems.',
      author='Dolf Andringa',
      author_email='dolfandringa@gmail.com',
      url='http://allican.be/AquaponicsModeler',
      packages=['PyElectronics'],
      package_dir={'': '../'},
      install_requires=['PyElectronics>2.0', 'PyQt5', 'matplotlib'],
      dependency_links=[
        'git+https://github.com/dolfandringa/PyElectronics.git'
        ],
      entry_points={
          'gui_scripts': [
            'aquaponicsmodeler = app.py:main'
          ]
      }
      )
