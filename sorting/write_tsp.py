"""
Calls the Concorde TSP solver to sort the input periodic movie into one single period.

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

O. Mariani, K. Chan, A. Ernst, N. Mercader and M. Liebling, "Virtual High-Framerate Microscopy Of The Beating Heart Via Sorting Of Still Images," 2019 IEEE 16th International Symposium on Biomedical Imaging (ISBI 2019), Venice, Italy, 2019, pp. 312-315, doi: 10.1109/ISBI.2019.8759595.

@INPROCEEDINGS{8759595,
  author={O. {Mariani} and K. {Chan} and A. {Ernst} and N. {Mercader} and M. {Liebling}},
  booktitle={2019 IEEE 16th International Symposium on Biomedical Imaging (ISBI 2019)}, 
  title={Virtual High-Framerate Microscopy Of The Beating Heart Via Sorting Of Still Images}, 
  year={2019},
  volume={},
  number={},
  pages={312-315},
  doi={10.1109/ISBI.2019.8759595}}
  
"""

import numpy as np
import os
import sys
import subprocess
import logging

from toolbox import om_toolbox

HEADER_FMT = """NAME: Periodic data
Type:TSP
COMMENT: {} frames
TYPE: TSP
DIMENSION: {}
EDGE_WEIGHT_TYPE: EXPLICIT
EDGE_WEIGHT_FORMAT: FULL_MATRIX
EDGE_WEIGHT_SECTION
"""


def write_tsp(concorde_data, concorde_output_path):
    """
    Writes the input file for the TSP solver Concorde
    :param concorde_data: Data to sort
    :param concorde_output_path: Concorde output file path
    :return: No return
    """
    n_t = concorde_data.shape[1]
    dir_ = os.path.dirname(concorde_output_path)
    header = HEADER_FMT.format(n_t, n_t)
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    with open(concorde_output_path, 'wb') as f:
        f.write(bytes(header, 'utf-8'))
        np.savetxt(f, concorde_data, fmt='%4d')
        f.write(bytes('EOF', 'utf-8'))


def get_frame_sorted(sol_file_path, input_im):
    """
    Sorts the frames according to the result in the SOL file
    :param sol_file_path: solution file, concorde output
    :param input_im: data to be sorted with the solution file
    :return: Sorted data and solution array
    """
    arr_concorde = om_toolbox.load_tsp_sol_file(sol_file_path)

    if arr_concorde.size != input_im.shape[-1]:
        logging.error('Discrepancy between concorde SOL file number of time points and input data number of time '
                      'points ({} / {})'.format(arr_concorde.size, input_im.shape[-1]))
        sys.exit(-1)

    return input_im[..., arr_concorde], arr_concorde


def run_tsp(input_im, concorde_path, y_downsizing_factor=1, x_downsizing_factor=1, show_data=False, tsp_path='',
            tsp_files_exist=''):
    """

    :param input_im: Data to sort
    :param concorde_path: path to the Concorde executable
    :param y_downsizing_factor: Downsizing factor for the lines
    :param x_downsizing_factor: Downsizing factor fot the columns
    :param show_data: Plays movies of the input, downsized, and sorted data if True
    :param tsp_path: path to save the tsp solution files
    :param tsp_files_exist: path to an existing tsp SOL file
    :return: ndarray sorted with respect to last dimension
    """

    if show_data:
        om_toolbox.play_movie(input_im)

    if not os.path.exists(tsp_files_exist):
        downsized_im = om_toolbox.average_downsizing(input_im, y_downsizing_factor, x_downsizing_factor)
        if show_data:
            om_toolbox.play_movie(downsized_im)

        diffs = om_toolbox.compute_differences(downsized_im[..., 0, 0, :])

        tsp_file = tsp_path + '_edge_weight.txt'
        sol_file = tsp_path + '_solution.txt'

        logging.info(tsp_path)
        write_tsp(diffs, tsp_file)

        subprocess.call([concorde_path, '-o', sol_file, '-x', tsp_file])
    else:
        sol_file = tsp_files_exist

    im_out, arr_concorde = get_frame_sorted(sol_file, input_im)

    if show_data:
        om_toolbox.play_movie(im_out, repeat_delay=100)

    return im_out
