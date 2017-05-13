import os
import glob
import copy
import numpy as np
import scipy
import scipy.special
import pandas as pd
import skimage.io
import skimage.morphology
import skimage.filters
import skimage.feature
import seaborn as sns
import statsmodels.tools.numdiff as smnd
from PIL import Image
import matplotlib.pyplot as plt
import seaborn as sns
from operator import itemgetter

# Directory containing the screenshots
data_dir = '../data/screens/'
output_dir = '../data/labeled/'

# Glob string for TIF image stacks
im_glob = os.path.join(data_dir, '*.png')

# Get list of files in directory
im_list = glob.glob(im_glob)
ic = skimage.io.ImageCollection(im_list, conserve_memory=False)

def add_bounding_boxes(img, boxes):
    new_img = copy.deepcopy(img)
    for i in range(len(boxes)):
        box = boxes[i]
        for x in range(box[0], box[2] + 1):
            for y in range(box[1], box[3] + 1):
                new_img[x][y] = img[x][y] * 0.8

    return new_img

for i in range(len(ic)):
    # Convert image to float
    im_float = skimage.img_as_float(ic[i])

    sorted_values = np.sort(im_float[:,:,0].flatten())[::-1]
    thesh = sorted_values[int(0.001 * len(sorted_values))]

    if thesh > 0.5:
        print('Image ' + str(i) + ': Likely has clouds/land obstructions - open sea images work best!')
    if thesh < 0.12:
        print('Image ' + str(i) + ': Perhaps has no ships, be wary of bounding boxes on ocean!')

    im_bw = im_float[:,:,0] < thesh

    selem = skimage.morphology.square(3)
    im_snp_filt2 = skimage.filters.rank.median(im_bw, selem)

    im_edge = skimage.feature.canny(im_snp_filt2, 0.3)
    im_filled = scipy.ndimage.morphology.binary_fill_holes(im_edge)

    im_labeled, n_labels = skimage.measure.label(
                            im_filled, background=0, return_num=True)

    im_props = skimage.measure.regionprops(im_labeled, intensity_image=im_filled)

    ships_bboxes = []
    for prop in im_props:
        if prop.area > 20:
            ships_bboxes.append([prop.bbox, prop.area])

    sorted_bboxes = sorted(ships_bboxes, key=itemgetter(1))
    if len(sorted_bboxes) > 10:
        sorted_bboxes = sorted_bboxes[:10]
    ships_bboxes = [sb[0] for sb in sorted_bboxes]

    im_boxes = add_bounding_boxes(im_float, ships_bboxes)

    scipy.misc.imsave(output_dir + str(i) + '.png', im_boxes)
    # plt.imsave(im_boxes, output_dir + str(i) + '.png')
