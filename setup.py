import setuptools
#from distutils.core import setup
#long_description = ""
#with open("README.txt", "r") as fh:
 #   long_description = fh.read()

setuptools.setup(
    name='aberration_correction',
    version='1.0',
    description='Periodic data sorting and shear correction of scan-aberrated heartbeat microscopy data in NPY format.',    
  #  long_description=long_description,
license='3-clause BSD',
    author='Olivia Mariani',
    author_email='olivia.mariani@idiap.ch',
    packages=['sorting','toolbox','unshearing'],
    python_requires='>=3.6.0',
    classifiers=[
        "Programming Language :: Python :: 3",],
    install_requires=["python-dateutil==2.8.0","numpy>=1.14.0", "scipy>=1.0.0", "argparse>=1.4.0", "matplotlib>=2.1.1", "tifffile>=2019.7.26",
                      
]
     )

