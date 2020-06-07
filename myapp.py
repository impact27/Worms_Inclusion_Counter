# -*- coding: utf-8 -*-
"""
Copyright (C) 2019 Quentin Peter

This file is part of Worms_Inclusions.

Worms_Inclusions is distributed under CC BY-NC-SA version 4.0. You should have
recieved a copy of the licence along with Worms_Inclusions. If not, see
https://creativecommons.org/licenses/by-nc-sa/4.0/.
"""

import matplotlib
matplotlib.use('TkAgg')

import os
import sys
import tkinter as tk
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from applicationCore import applicationCore
from matplotlib.patches import Rectangle
from matplotlib.widgets import LassoSelector

progname = os.path.basename(sys.argv[0])
progversion = "0.1"


class MyMplCanvas(FigureCanvas):
    """Ultimately, this is a QWidget (as well as a FigureCanvasAgg, etc.)."""

    def __init__(self, master, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        self.compute_initial_figure()

        FigureCanvas.__init__(self, fig, master)

    def compute_initial_figure(self):
        pass


class imageCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.axes = self.figure.add_subplot(111)
        self.cbar = None

    def createLasso(self, onLassoSelect):
        self.lasso = LassoSelector(self.axes, onLassoSelect,
                                   lineprops=dict(color='w'))

    def setimage(self, im):
        self.im = im
        # if hasattr(self, 'ROIrect'):
        #     del self.ROIrect
        self.update_figure()

    def update_figure(self):
        self.axes.clear()
        mp = self.axes.imshow(self.im)
        self.axes.axis('image')
        if self.cbar is not None:
            self.cbar.mappable = mp
        else:
            self.cbar = self.figure.colorbar(mp)
        # if hasattr(self, 'ROIrect'):

        #     self.axes.add_patch(self.ROIrect)
        self.draw()

    def standalone(self):
        if hasattr(self, 'im'):
            plt.figure()
            plt.imshow(self.im)
            plt.colorbar()
            plt.show()

    def addRectangle(self, X, W, H):
        # self.ROIrect = Rectangle(X, W, H, facecolor='none',edgecolor='white')
        self.update_figure()


class inclusionCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)

    def setLabels(self, labels):
        self.labels = np.array(labels, dtype=float)
        self.labels[labels == 0] = np.nan
        self.update_figure()

    def setMaskWorm(self, maskWorm):
        self.maskWorm = maskWorm
        self.update_figure()

    def update_figure(self, axes=None):
        if axes is None:
            axes = self.axes
        axes.cla()
        if hasattr(self, 'labels'):
            axes.imshow(self.labels)
            n = np.nanmax(self.labels)
            if np.isnan(n):
                n = 0
            axes.set_title(str(int(n)) + ' Inclusions')
        if hasattr(self, 'maskWorm'):
            axes.imshow(self.maskWorm, alpha=.5, cmap=plt.get_cmap('Reds'))
        axes.axis('image')
        self.draw()

    def standalone(self, event):
        fig = plt.figure()
        axes = fig.add_subplot(111)
        self.update_figure(axes)
        plt.show()


class thresholdCanvas(MyMplCanvas):
    def __init__(self, *args, **kwargs):
        MyMplCanvas.__init__(self, *args, **kwargs)
        self.log = False

    def setData(self, data, bins):
        self.data = data
        self.bins = bins
        self.threshold = 0

    def update_figure(self):
        self.axes.cla()
        self.axes.bar(self.bins[:-1], self.data, self.bins[1] - self.bins[0])
        self.axes.plot([self.threshold, self.threshold],
                       [0, self.axes.axis()[-1]], 'g')
        self.axes.set_yscale("log")
        if self.log:
            self.axes.set_xscale("log")
        self.axes.set_xlabel('Value')
        self.draw()

    def setThreshold(self, threshold):
        self.threshold = threshold
        if hasattr(self, 'data'):
            self.update_figure()

    def onXLog(self, checked):
        self.log = checked
        self.update_figure()


class ApplicationWindow():
    def __init__(self, root):
        self.main_window = root

        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        bottom_frame = tk.Frame(root)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        # Create canevas
        self.imageCanvas = imageCanvas(master=top_frame)
        self.inclusionCanvas = inclusionCanvas(master=top_frame)
        self.thresholdCanvas = thresholdCanvas(master=bottom_frame)

        self.imageCanvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.inclusionCanvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
        self.thresholdCanvas.get_tk_widget().pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        buttons_frame = tk.Frame(bottom_frame)
        buttons_frame.pack(side=tk.RIGHT, padx=10)

        # create appication core
        self.applicationCore = applicationCore(self.imageCanvas,
                                               self.inclusionCanvas,
                                               self.thresholdCanvas)

        # Create Buttons
        self.is_threshold_log = tk.IntVar()
        logbutton = tk.Checkbutton(buttons_frame, text='Threshold xlog',
                                   variable=self.is_threshold_log,
                                   command=self.onXLog)
        self.is_intensity_threshold = tk.IntVar()
        thresTypebutton = tk.Checkbutton(buttons_frame, text='Intensity threshold',
                                         variable=self.is_intensity_threshold,
                                         command=self.onThreshType)
        self.is_show_gradient = tk.IntVar()
        gradbutton = tk.Checkbutton(buttons_frame, text='Show gradient',
                                    variable=self.is_show_gradient,
                                    command=self.onImageDisplay)
        self.is_edit_worm = tk.IntVar()
        bgbutton = tk.Checkbutton(buttons_frame, text='Edit worm',
                                  variable=self.is_edit_worm,
                                  command=self.onEditWorm)
        openButton = tk.Button(
            buttons_frame, text='Load Folder',
            command=self.applicationCore.onOpenFile)
        nextButton = tk.Button(
            buttons_frame, text='Save/Next',
            command=self.applicationCore.onNext)
        sameButton = tk.Button(
            buttons_frame, text='Save/Same',
            command=self.applicationCore.onSame)
        skipButton = tk.Button(
            buttons_frame, text='Skip',
            command=self.applicationCore.onSkip)
        endButton = tk.Button(
            buttons_frame, text='End',
            command=self.applicationCore.onEnd)
        ResetROIButton = tk.Button(
            buttons_frame, text='Reset ROI',
            command=self.applicationCore.onROIReset)

        scaleLine = tk.Entry(buttons_frame)
        scaleLine.insert(0, '1')
        # add method to applicationCore
        self.applicationCore.iseditingbg = self.is_edit_worm.get
        self.applicationCore.getRatioText = scaleLine.get

        # Connections
        self.thresholdCanvas.mpl_connect('button_press_event',
                                         self.applicationCore.onThresClick)
#        self.imageCanvas.mpl_connect('button_press_event',
#                                     self.applicationCore.onImageClick)
#        self.imageCanvas.mpl_connect('motion_notify_event',
#                                     self.applicationCore.onImageMove)
#        self.imageCanvas.mpl_connect('button_release_event',
#                                     self.applicationCore.onImageRelease)
        self.inclusionCanvas.mpl_connect('button_press_event',
                                         self.inclusionCanvas.standalone)

        thresTypebutton.pack(fill=tk.X)
        logbutton.pack(fill=tk.X)
        gradbutton.pack(fill=tk.X)
        bgbutton.pack(fill=tk.X)
        openButton.pack(fill=tk.X)
        nextButton.pack(fill=tk.X)
        sameButton.pack(fill=tk.X)
        ResetROIButton.pack(fill=tk.X)
        scaleLine.pack(fill=tk.X)
        skipButton.pack(fill=tk.X)
        endButton.pack(fill=tk.X)

        self.applicationCore.onOpenFile()

    def onThreshType(self):
        self.applicationCore.onThreshType(self.is_intensity_threshold.get())

    def onImageDisplay(self):
        self.applicationCore.onImageDisplay(self.is_show_gradient.get())

    def onEditWorm(self):
        self.applicationCore.onEditWorm(self.is_edit_worm.get())

    def onXLog(self):
        self.thresholdCanvas.onXLog(self.is_threshold_log.get())

if __name__ == "__main__":
    root = tk.Tk()
    window = ApplicationWindow(root)
    root.title("%s" % progname)
    root.mainloop()
