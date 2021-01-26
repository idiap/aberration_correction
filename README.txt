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

citation: 
O. Mariani, A. Ernst, N. Mercader and M. Liebling, "Reconstruction of Image Sequences From Ungated and Scanning-Aberrated Laser Scanning Microscopy Images of the Beating Heart," in IEEE Transactions on Computational Imaging, vol. 6, pp. 385-395, 2020, doi: 10.1109/TCI.2019.2948772.

@ARTICLE{8878149,
  author={O. {Mariani} and A. {Ernst} and N. {Mercader} and M. {Liebling}},
  journal={IEEE Transactions on Computational Imaging}, 
  title={Reconstruction of Image Sequences From Ungated and Scanning-Aberrated Laser Scanning Microscopy Images of the Beating Heart}, 
  year={2020},
  volume={6},
  number={},
  pages={385-395},
  doi={10.1109/TCI.2019.2948772}}


Contact info: 
Idiap Research Institute
Centre du Parc
Rue Marconi 19
PO Box 592
CH - 1920 Martigny
Switzerland
olivia.mariani@idiap.ch
