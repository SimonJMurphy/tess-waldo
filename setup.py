from setuptools import setup

setup(name='tess-waldo',
version = '1.0.1',
description = "A friendly package for finding targets on TESS CCDs.",
author = 'Simon J. Murphy',
author_email = 'simon.murphy@sydney.edu.au',
license = 'MIT',
install_requires = ['tess-point', 'lightkurve', 'astroquery'],
packages = ['tess_waldo'])