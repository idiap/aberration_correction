#!/usr/bin/env python

"""
Loads NPY or TIFF files with data of periodic movement, and sorts the data to
form one single period.

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

"""

import numpy as np
import sys
from os.path import join, basename, dirname
import argparse
import logging
from tempfile import mkdtemp

from sorting import write_tsp
from toolbox import om_toolbox


def parsing():
    """
    Bash commands
    :return:
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input_file_path", type=str,
                        help="Input data path. Expected 5D data XYZCT.")
    parser.add_argument("-o", "--output_file_path", type=str, default='',
                        help="Input data path. Expected 5D data XYZCT.")
    parser.add_argument("--concorde", type=str,
                        help="concorde executable path")
    parser.add_argument("--input_tsp", type=str,
                        help="Existing tsp file path")
    parser.add_argument("-y", "--ydownsizing", type=int, default="4",
                        help="Downsizing factor for dimension Y.")
    parser.add_argument("-x", "--xdownsizing", type=int, default="4",
                        help="Downsizing factor for dimension X.")
    parser.add_argument("--tsp_file", type=str, default='',
                        help="Applies the solution from tsp_file to the input file. must have the same number of time "
                             "points. Default=''")
    parser.add_argument("--show_tsp", type=bool, default=False,
                        help="Shows movie of original data, downsized data, and sorted data.")
    parser.add_argument("--logging_level", type=str, default='INFO', help="logging level from the logging python "
                                                                          "package. Can be INFO, WARNING, ERROR.")
    return parser.parse_args()


def main(input_file_path, concorde_path, output_file_path='', x_down_sizing_factor=4, y_down_sizing_factor=4,
         tsp_file='', input_tsp_path='', show_tsp=False, logging_level='INFO'):
    """

    :param input_file_path: Input data path
    :param output_file_path: Output data path
    :param concorde_path: Concorde path
    :param x_down_sizing_factor: Downsizing factor for the columns. Default=4
    :param y_down_sizing_factor: Downsizing factor for the lines. Default=4
    :param tsp_file: If file not empty, applies this solution to the input file. Default=''
    :param input_tsp_path: Existing tsp file path. Default=''
    :param show_tsp: plays the input data, downsized data, sorted data. Default=False
    :param logging_level: level of info printed to log file. Can be INFO, WARNING, or ERROR. Log file in input
    directory.
    :return:
    """

    file_path = input_file_path
    dir_data = dirname(file_path)
    tmp_data = mkdtemp()
    filename = basename(file_path)
    logging.basicConfig(filename=join(dir_data, 'sorting.log'), level=logging_level)

    if input_tsp_path == '':
        tsp_path = join(dir_data, filename[:filename.find(".")] + '_tsp_file')
    else:
        tsp_path = input_tsp_path

    im = om_toolbox.load_data(file_path)

    if im.ndim != 5:
        logging.error('Expecting array with 5 dimensions. Here the array has {} dimensions ({}). Exiting script.'
                      .format(im.ndim, im.size))
        sys.exit(-1)
    im_mapped = np.memmap(join(tmp_data, 'tmp.npy'), dtype=im.dtype, mode='w+', shape=im.shape)
    im_mapped[:] = im[:]

    del im

    logging.info('TSP solver starting...')

    tsp_movie = np.memmap(join(tmp_data, 'tsp.npy'), dtype=im_mapped.dtype, mode='w+', shape=im_mapped.shape)
    tsp_movie[:] = write_tsp.run_tsp(im_mapped, concorde_path=concorde_path, show_data=show_tsp, tsp_path=tsp_path,
                                     y_downsizing_factor=y_down_sizing_factor,
                                     x_downsizing_factor=x_down_sizing_factor, tsp_files_exist=tsp_file)

    if output_file_path == '':
        output_file_path = join(dir_data, filename[:filename.find(".")] + '_sorted.npy')

    np.save(output_file_path, tsp_movie)
    logging.info('Saved data as {}'.format(output_file_path))

    logging.info('Done.')


if __name__ == "__main__":

    parse = parsing()

    main(parse.input_file_path, parse.concorde, output_file_path=parse.output_file_path,
         x_down_sizing_factor=parse.xdownsizing, y_down_sizing_factor=parse.ydownsizing, tsp_file=parse.tsp_file,
         show_tsp=parse.show_tsp, logging_level=parse.logging_level)


