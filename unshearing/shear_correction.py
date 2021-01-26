"""
Corrects scan-shearing artefacts on sorted periodic movies.

Copyright (c) 2019 Idiap Research Institute, http://www.idiap.ch/
Written by Olivia Mariani <olivia.mariani@idiap.ch>,

This file is part of LHSAC.

LHSAC is a free software: you can redistribute it and/or modify
it under the terms of the 3-clause Berkeley Software Distribution (BSD) as
published by the Open Source Initiative.

LHSAC is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
3-clause BSD License for more details.

You should have received a copy of the 3-clause BSD along with LHSAC.
If not, see <https://opensource.org/licenses/BSD-3-Clause>.

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
"""

import numpy as np
from os.path import join, basename, dirname, exists
import argparse
import logging
from tempfile import mkdtemp

from unshearing import opt_shift
from toolbox import om_toolbox


def parsing():
    """
    Bash commands
    :return:
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file_path", type=str, help="Input file path. Expected sorted, one period data")
    parser.add_argument("-o", "--output_file_path", type=str, default='', help="Output file path.")
    parser.add_argument("-y", "--ydownsizing", type=int, default="4", help="Downsizing factor for dimension Y.")
    parser.add_argument("-x", "--xdownsizing", type=int, default="4", help="Downsizing factor for dimension X.")
    parser.add_argument("--apply", type=bool, default=False,
                        help="Applies a previous shift.")
    parser.add_argument("--input_shift_file", type=str, default='', help="Previous shift file.")
    parser.add_argument("--logging_level", type=str, default='INFO', help="logging level from the logging python "
                                                                          "package. Can be INFO, WARNING, ERROR.")
    return parser.parse_args()


def main(input_file_path, output_file_path='', x_down_sizing_factor=4, y_down_sizing_factor=4, input_shift_file='',
         logging_level='INFO'):
    """

    :param input_file_path: Input data file path
    :param output_file_path: Output data file path. Default in input file folder
    :param x_down_sizing_factor: Downsizing factor for the columns
    :param y_down_sizing_factor: Downsizing factor for the lines
    :param input_shift_file: Shift text file, if the shift was previously calculated (applies previous result)
    :param logging_level: level of info printed to log file. Can be INFO, WARNING, or ERROR. Log file in input
    directory.
    :return:
    """

    dir_data = dirname(input_file_path)
    filename = basename(input_file_path)
    tmp_data = mkdtemp()
    logging.basicConfig(filename=join(dir_data, 'unshearing.log'), level=logging_level)
    tsp = om_toolbox.load_data(input_file_path)

    im_mapped = np.memmap(join(tmp_data, 'rec_tsp.npy'), dtype=np.float64, mode='w+', shape=tsp.shape)

    im_mapped[:] = tsp[:]

    del tsp

    shift = None
    if exists(input_shift_file):
        shift = np.loadtxt(input_shift_file)

    logging.info('Scanning aberration correction...')

    shift_calc = opt_shift.Shift(y_down_sizing_factor, x_down_sizing_factor, im_sorted=im_mapped, shift=shift)

    reconstructed_data = np.memmap(join(tmp_data, 'rec_tmp.npy'), dtype=np.float64, mode='w+', shape=im_mapped.shape)
    reconstructed_data[:], pixel_shift = shift_calc.aberration_correction(step_init=np.array([5.3], dtype=np.float),
                                                                          method='Nelder-Mead')

    if output_file_path == '':
        output_file_path = join(dir_data, filename[:filename.find(".")] + '_unsheared.npy')
    np.save(output_file_path, reconstructed_data)

    del im_mapped

    logging.info('Done.')


if __name__ == "__main__":

    parse = parsing()
    main(parse.input_file_path, output_file_path=parse.output_file_path, x_down_sizing_factor=parse.xdownsizing,
         y_down_sizing_factor=parse.ydownsizing, input_shift_file=parse.input_shift_file,
         logging_level=parse.logging_level)

