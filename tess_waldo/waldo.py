from __future__ import division, print_function

from astroquery.mast import Catalogs
import lightkurve as lk
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from tess_stars2px import tess_stars2px_function_entry
import warnings

__all__ = ["Waldo"]

class Waldo(object):
    
    def __init__(self, target):
        self.target = target
        self.get_data()
        self.ccd_size = 2048

    def get_data(self):
        catalog_data = Catalogs.query_object(f"{self.target}", catalog="TIC")

        ident, ra, dec, dstArcSec = catalog_data[0][["ID", "ra", "dec", "dstArcSec"]]
        self.mast_data = tess_stars2px_function_entry(ident, ra, dec)
        
        if dstArcSec > 0.2:
            warnings.warn(f"Warning: returned target is far ({dstArcSec} arcsec) from the requested one.")
        
        self.tic = self.mast_data[0]
        self.ra = self.mast_data[1]
        self.dec = self.mast_data[2]
        self.sectors = self.mast_data[3]
        self.cameras = self.mast_data[4]
        self.ccds = self.mast_data[5]
        self.colpix = self.mast_data[6]
        self.rowpix = self.mast_data[7]
        
        sr = lk.search_tesscut(self.target)
        self.available_sectors = sr.table["sequence_number"].data
        self.max_available = self.available_sectors.max()
        
        southern_limit = 13
        if self.max_available > southern_limit:
            raise ValueError('Sector not in Southern Hemisphere')
        
        if np.any(self.cameras) > 4:
            raise ValueError("Camera not in list")
        if np.any(self.ccds) > 4:
            raise ValueError("CCD not in list")
        
    def to_pandas(self):
        df = pd.DataFrame({'TIC': self.tic, 'RA': self.ra[1], 'Dec': self.dec[2], 
                           'Sector': self.sector[3], 'Camera': self.camera[4], 'Ccd': self.ccd[5], 
                           'ColPix': self.colpix[6], 'RowPix': self.rowpix[7]})
        
    def get_position(self, sector, camera, ccd, colpix, rowpix):
        ''' Gets the position of the star on the Camera/CCD, but presently for southern pointing only
        '''
        ccd_size = self.ccd_size
        if camera == 1 or camera == 2:
            if ccd == 1:
                col = 2*ccd_size - colpix
                row = rowpix
            elif ccd == 2:
                col = ccd_size - colpix
                row = rowpix
            elif ccd == 3:
                col = colpix
                row = 2*ccd_size - rowpix
            elif ccd == 4:
                col = ccd_size + colpix
                row = 2*ccd_size - rowpix
        elif camera == 3 or camera == 4:
            if ccd == 1:
                col = colpix
                row = 2*ccd_size - rowpix
            elif ccd == 2:
                col = ccd_size + colpix
                row = 2*ccd_size - rowpix
            elif ccd == 3:
                col = 2*ccd_size - colpix
                row = rowpix
            elif ccd == 4:
                col = ccd_size - colpix
                row = rowpix

        position = [col, row]
        return position

    def make_x_arrows(self, sector, camera, ccd):
        ''' Plotting tool for adding arrows to the camera plot in the direction of CCD readout.
        '''
        sector = 1 #hackyhack, valid for southern hemisphere only
        anchor = 128
        dx, dy = anchor, 0
        ccd_size = self.ccd_size
        
        if camera == 1 or camera == 2:
            if ccd == 1:
                x = 2*ccd_size - anchor
                y = anchor
                dx *= -1
            elif ccd == 2:
                x = ccd_size - anchor
                y = anchor
                dx *= -1
            elif ccd == 3:
                x = anchor
                y = 2*ccd_size - anchor
                dy *= -1
            elif ccd == 4:
                x = ccd_size + anchor
                y = 2*ccd_size - anchor
                dy *= -1
        elif camera == 3 or camera == 4:
            if ccd == 1:
                x = anchor
                y = 2*ccd_size - anchor
                dy *= -1
            elif ccd == 2:
                x = ccd_size + anchor
                y = 2*ccd_size - anchor
                dy *= -1
            elif ccd == 3:
                x = 2*ccd_size - anchor
                y = anchor
                dx *= -1
            elif ccd == 4:
                x = ccd_size - anchor
                y = anchor
                dx *= -1
        return x, y, dx, dy

    def make_y_arrows(self, sector, camera, ccd):
        ''' Plotting tool for adding arrows to the camera plot in the direction of CCD readout.
        '''
        sector = 1 #hackyhack, valid for southern hemisphere only
        anchor = 128
        dx, dy = 0, anchor
        ccd_size = self.ccd_size
        if camera == 1 or camera == 2:
            if ccd == 1:
                x = 2*ccd_size - anchor
                y = anchor
                dx *= -1
            elif ccd == 2:
                x = ccd_size - anchor
                y = anchor
                dx *= -1
            elif ccd == 3:
                x = anchor
                y = 2*ccd_size - anchor
                dy *= -1
            elif ccd == 4:
                x = ccd_size + anchor
                y = 2*ccd_size - anchor
                dy *= -1
        elif camera == 3 or camera == 4:
            if ccd == 1:
                x = anchor
                y = 2*ccd_size - anchor
                dy *= -1
            elif ccd == 2:
                x = ccd_size + anchor
                y = 2*ccd_size - anchor
                dy *= -1
            elif ccd == 3:
                x = 2*ccd_size - anchor
                y = anchor
                dx *= -1
            elif ccd == 4:
                x = ccd_size - anchor
                y = anchor
                dx *= -1
        return x, y, dx, dy

    def color_by_sector_availability(self, sector):
        if sector in self.available_sectors:
            return 'b'
        elif sector in self.sectors:
            return 'm'
        else:
            return 'r'

    def plot(self, ax=None, **kwargs):
        if ax is None:
            n_unique_cameras = len(np.unique(self.cameras))
            fig, axes = plt.subplots(nrows=n_unique_cameras, ncols=1, sharex=True,
                                     figsize=[6,n_unique_cameras*6], squeeze=False, **kwargs)
            axes = axes.flatten()
        
        # setup properties of Camera and CCD boundaries
        ccd_size = self.ccd_size
        frame_x = [0, 2*ccd_size, 2*ccd_size, 0, 0]
        frame_y = [2*ccd_size, 2*ccd_size, 0, 0, 2*ccd_size]
        inner_x_vert = [ccd_size, ccd_size]
        inner_y_vert = [0, 2*ccd_size]
        inner_x_horiz = [0, 2*ccd_size]
        inner_y_horiz = [ccd_size, ccd_size]
        
        for ax in axes:
            # plot the frame and ccd boundaries
            ax.plot(frame_x, frame_y, 'k',lw=4)
            ax.plot(inner_x_vert, inner_y_vert, 'k',lw=3)
            ax.plot(inner_x_horiz, inner_y_horiz, 'k',lw=3)
        
            # label the axes
            ax.set_ylabel("y position, px")
            
            # set y range for multiple panels
            ax.set_ylim(0,2*ccd_size)
            
            # plot the direction in which ccds are read out
            for i in np.arange(1,5,1):
                ax.arrow(*self.make_x_arrows(1, 4, i), head_width=8)
                ax.arrow(*self.make_y_arrows(1, 4, i), head_width=8)

        # plot the CCD positions
        for i in range(0,len(self.sectors)):
            pos = self.get_position(self.sectors[i], self.cameras[i], self.ccds[i], self.colpix[i], self.rowpix[i])
            axes[self.cameras[i]-self.cameras.max()+n_unique_cameras-1].scatter(pos[0] ,pos[1], label=f"Sector{int(self.sectors[i])}",
                       c=self.color_by_sector_availability(self.sectors[i]), s=2)

            axes[self.cameras[i]-self.cameras.max()+n_unique_cameras-1].annotate(f"{int(self.sectors[i])}", [pos[0]+16, pos[1]-16],
                        color=self.color_by_sector_availability(self.sectors[i]))
            axes[self.cameras[i]-self.cameras.max()+n_unique_cameras-1].annotate(f"Camera {int(self.cameras[i])}", [2*ccd_size - 64, 2*ccd_size - 64],
                        color='k', ha='right', va='top')

        # squash the panels together
        plt.subplots_adjust(hspace=0.)

        # provide some space at the top and bottom for the target name and the x axis
        axes[0].set_ylim(top = 2*ccd_size + 256)
        axes[-1].set_ylim(bottom = -128)

        # add the x-axis label and the target name in the newly created space
        axes[-1].set_xlabel("x position, px")
        axes[0].annotate(f"{self.target}", [ccd_size, 2*ccd_size+64], color='b', ha='center')

        plt.show()