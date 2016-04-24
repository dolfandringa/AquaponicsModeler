#!/usr/bin/env python

from setuptools import setup


setup(name='AquaponicsModeler',
      version='0.1',
      description='A modelling application for aquaponics systems.',
      author='Dolf Andringa',
      author_email='dolfandringa@gmail.com',
      url='http://allican.be/AquaponicsModeler',
      packages=['AquaponicsModeler'],
      package_dir={'': '../'},
      install_requires=['PyElectronics', 'PyQt5', 'matplotlib'],
      dependency_links=[
        'https://github.com/dolfandringa/PyElectronics/archive/master.zip'+
          '#egg=PyElectronics-1.0'
        ],
      entry_points={
          'gui_scripts': [
            'aquaponicsmodeler = app.py:main'
          ]
      }
      )
