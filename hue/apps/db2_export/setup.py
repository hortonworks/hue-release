from setuptools import setup, find_packages
from hueversion import VERSION

setup(
      name = "db2_export",
      version = VERSION,
      author = "Expedia",
      url = 'https://github.com/ExpediaEDW/edw-hue',
      description = "DB2 export interface on Hue",
      packages = find_packages('src'),
      package_dir = {'': 'src'},
      install_requires = ['setuptools', 'desktop'],
      entry_points = { 'desktop.sdk.application': 'db2_export=db2_export' },
)
