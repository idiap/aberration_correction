"""
Toolbox contains functions to load the data, compute image-to-image difference, downsize images,
play movies, load SOL files.

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
import os
import sys
import glob
import logging
import tifffile

import matplotlib.pyplot as plt
import matplotlib.animation as animation


def load_data(filename):
    """
    Can open NPY files or TIFF files (single file or folder).
    :param filename:
    :return:
    """

    if filename.endswith('.npy'):
        output_im = np.load(filename)
        if output_im.ndim == 3:
            output_im = output_im[..., np.newaxis, np.newaxis, :]
    else:
        file_types = ['*.tif', '*.tiff']
        # opens a directory of TIFF files
        if os.path.isdir(filename):
            files_names = []
            for files in file_types:
                files_names.extend(glob.glob(os.path.join(filename, files)))
            tif_counter = len(files_names)
            if tif_counter >= 1:
                sorted_files = np.sort(files_names)
                output_im = []
                for i in range(tif_counter):
                    file_im = os.path.join(filename, sorted_files[i])
                    im_in = tifffile.imread(file_im)
                    if i == 0:
                        output_im = im_in[..., np.newaxis]
                    else:
                        output_im = np.concatenate((output_im, im_in[..., np.newaxis]), axis=-1)
                return output_im
            else:
                logging.error('No TIFF files found in {}'.format(filename))
                sys.exit(-1)
        else:
            logging.error('Data type should be NPY or TIFF.')
            sys.exit(-1)
    return output_im


def compute_differences(image_in):
    output = np.reshape(image_in, (image_in.shape[0]*image_in.shape[1]*image_in.shape[2]*image_in.shape[3],
                                  image_in.shape[-1]))
    image_in = None

    output = pdist(output.T, 'minkowski', p=1)
    output = squareform(output)

    return output


def average_downsizing(input_im, y_downsizing_factor, x_downsizing_factor):
    """
    Downsizes image by averaging data.
    :param input_im: Input image
    :param y_downsizing_factor: Downsizing factor for the lines
    :param x_downsizing_factor: Downsizing factor for the columns
    :return: Downsized image
    """
    shape_image = np.array(input_im.shape, dtype=np.int)
    if (shape_image[0] / y_downsizing_factor).is_integer():
        shape_image[0] = int(shape_image[0] / y_downsizing_factor)
    else:
        y_downsizing_factor = 1
        logging.warning('Y division factor {} '
                        'is not a divider of axis 0 of size {}'
                        '. Will use 1 instead.'.format(y_downsizing_factor, shape_image[0]))
    if (shape_image[1] / x_downsizing_factor).is_integer():
        shape_image[1] = int(shape_image[1] / x_downsizing_factor)
    else:
        x_downsizing_factor = 1
        logging.warning('X division factor {} '
                        'is not a divider of axis 1 of size size {}'
                        '. Will use 1 instead.'.format(x_downsizing_factor, shape_image[1]))
    if input_im.ndim == 5:
        image_out = np.ones(shape_image)*np.mean(input_im)
        for t in range(shape_image[-1]):
            for c in range(shape_image[3]):
                for z in range(shape_image[2]):
                    image_out[..., z, c, t] = rebin(input_im[..., z, c, t], image_out[..., z, c, t].shape)
    else:
        logging.warning('Input must have 5 dimensions. Returning input image without downsizing.')
        return input_im
    return image_out


def rebin(input_im, output_shape):
    """

    :param input_im: Input data
    :param output_shape: Tuple of the shape of the output data
    :return:
    """
    sh = output_shape[0], input_im.shape[0] // output_shape[0], output_shape[1], input_im.shape[1] // output_shape[1]
    return input_im.reshape(sh).mean(-1).mean(1)


def play_movie(input_im, title='', c=0, z=0, repeat_delay=1000, interval=500, repeat=True):
    """
    :param input_im: 5D data in order XYZCT
    :param title: Movie title
    :param c: Channel index if 5D
    :param z: Slice index if 5D
    :param repeat_delay: Delay between movie loops in ms
    :param interval: Delay in between frames in ms
    :param repeat: Boolean set to True for the movie to loop
    :return:
    """

    fig = plt.figure()

    ims = []
    for i in range(input_im.shape[-1]):
        image = input_im[..., z, c, i]
        im1 = plt.imshow(image, cmap='gray')
        ims.append([im1])
    ani = animation.ArtistAnimation(fig, ims, interval=interval, blit=True, repeat_delay=repeat_delay, repeat=repeat)
    plt.title(title)
    plt.show()


def load_tsp_sol_file(sol_file_path):
    """
    Loads the solution SOL file created by concorde as an array
    :param sol_file_path: the concorde SOL file path
    :return:
    """

    if os.path.exists(sol_file_path):
        with open(sol_file_path, 'r') as f:
            arr_concorde = [[int(x) for x in line.split()] for line in f]
    else:
        logging.error('File {} not found.'.format(sol_file_path))
        sys.exit(-1)
    # The first value is the size of the array
    arr_concorde.pop(0)
    arr_concorde = np.array([np.array(x) for x in arr_concorde])
    return np.hstack(arr_concorde)
