1) Download the Concorde executable file if non-linux OS: 
http://www.math.uwaterloo.ca/tsp/concorde/downloads/downloads.htm

2) Go to the project directory where the setup.py file is located and install the project packages:
$ python -m pip install -e .

3) Data sorting
Minimal example:
$ python sorting/periodic_sorting.py -i ../../dataset/test_data.npy --concorde concorde_linux/concorde

4) Scanning-aberration correction
Minimal example:
$ python unshearing/shear_correction.py -i ../../dataset/test_data_sorted.npy

Contact info: 
Idiap Research Institute
Centre du Parc
Rue Marconi 19
PO Box 592
CH - 1920 Martigny
Switzerland
olivia.mariani@idiap.ch
