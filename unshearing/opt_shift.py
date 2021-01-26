"""
Estimates the data period to correct for scanning artefacts of periodic movies.

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
from scipy.optimize import minimize
import scipy.interpolate as interpolate
import logging

from toolbox import om_toolbox


class Shift:

    def __init__(self, y_downsizing_factor, x_downsizing_factor, im_sorted, shift=None):
        """

        :param y_downsizing_factor: Downsizing factor for the lines
        :param x_downsizing_factor: Downsizing factor for the columns
        :param im_sorted: Previously sorted image
        :param shift: If not None, will apply the given shift to im_sorted
        """

        im_in = np.concatenate((im_sorted, im_sorted[..., 0, np.newaxis]), axis=-1)

        self.downsampling_factor_y = y_downsizing_factor
        self.downsampling_factor_x = x_downsizing_factor
        self.shift = shift
        self.image_out = im_in

        if shift is None:
            im_downsampled = om_toolbox.average_downsizing(im_in, y_downsizing_factor, x_downsizing_factor)
            self.image = im_downsampled

    def min_resampling(self, step):
        """
        Function to minimize
        :param step: shift size
        :return: Line-to-line difference
        """
        im = self.image.astype(np.float)

        ny, nx, nz, nc, nt = im.shape

        step = step[0]
        nts = np.arange(0, nt)
        if step < 0:
            step = -step
            im = im[::-1]
            nts = len(nts) - nts[::-1] - 1

        out = np.zeros(im.shape, dtype=np.float)

        nt_range = np.arange(0, nt)

        for y in range(ny):
            int_interp = int((step*y)//1)
            residue = (step*y) - int_interp
            interpolation_ordonn = nt_range + residue
            interpolation_ordonn[-1] = nt_range[-1]
            for x in range(nx):
                tck = interpolate.splrep(nts, im[y, x, 0, 0, :], per=True, k=3)
                out[y, x, 0, 0, :] = interpolate.splev(interpolation_ordonn, tck)
            out[y, ...] = np.roll(out[y, ...], int_interp, axis=-1)

        mean_out_y = np.sum(np.fabs(np.diff(out, axis=0)))

        return mean_out_y

    def reconstruction(self, step):
        """
        Data resampling to correct for scanning aberration.
        :param step: Reconstructs the input image with a step size of step in pixels
        :return:
        """

        im = self.image_out.astype(np.float)
        ny, nx, nz, nc, nt = im.shape
        nt_range = np.arange(0, nt)

        if step < 0:
            step = -step
            im = im[..., ::-1]

        out = np.zeros(im.shape, dtype=np.float)

        for y in range(ny):
            logging.info('Row {} / {}'.format(y + 1, ny))
            int_interp = int((step * y)//1)
            residue = (step * y) - int_interp
            interpolation_ordonn = nt_range + residue
            interpolation_ordonn[-1] = nt_range[-1]
            for x in range(nx):
                tck = interpolate.splrep(nt_range, im[y, x, 0, 0, :], per=True, k=3)
                out[y, x, ...] = interpolate.splev(interpolation_ordonn, tck)
            out[y, ...] = np.roll(out[y, ...], int_interp, axis=-1)

        return out

    def aberration_correction(self, step_init=np.array([5.3]), method='Nelder-Mead'):
        """

        :param step_init: Initial step for minimization function
        :param method: Which minimization method to use
        :return: reconstructed ndarray
        """
        if self.shift is None:
            fct_interp = self.min_resampling
            logging.info('Starting period estimation...')

            res = minimize(fct_interp, step_init, method=method)
            logging.info('Done.\nStarting reconstruction...')
            rec = self.reconstruction(res.x[0]/self.downsampling_factor_y)
            logging.info('Done.')

            return rec[..., :-1], res.x/self.downsampling_factor_y
        else:
            logging.info('Done.\nStarting reconstruction...')
            rec = self.reconstruction(self.shift)
            logging.info('Done.')
            return rec[..., :-1], self.shift

    def main(self, step_init=np.array([5.3]), method='Nelder-Mead'):
        """

        :param step_init: initial shift
        :param method: Minimization method
        :return:
        """
        self.aberration_correction(step_init=step_init, method=method)

    # EOF
