import os
import cv2
import numpy as np

def frames(fn, dst_path, dst_prefix=None, frame_int=1, start_time=0, end_time=None, lens_pars=None):
    """

    :param fn:  filename (str) or BytesIO object containing a movie dataset
    :param dst_path: str - destination for resulting frames
    :param dst_prefix: str - prefix used for naming of frames
    :param frame_int: int - frame interval, difference between frames
    :param start_time=0: start time of first frame to extract (ms)
    :param end_time=None: end time of last frame to extract (ms). If None, it is assumed the entire movie must be extracted
    :param lens_pars=None: set of parameters passed to lens_corr if needed (e.g. {"k1": -10.0e-6, "c": 2, "f": 8.0}
    :return: list of time since start (ms), list of files generated
    """
    if not(os.path.isdir(dst_path)):
        try:
            os.makedirs(dst_path)
        except:
            raise PermissionError(f"Path {os.path.abspath(dst_path)} cannot be created. Check permissions")
    while True:
        cap = cv2.VideoCapture(fn)
        n = 0
        while cap.isOpened():
            try:
                ret, img = cap.read()
            except:
                raise IOError(f"Cannot read next frame no. {n}")
            if lens_pars is not None:
                # apply lens distortion correction
                img = lens_corr(img, **lens_pars)
            # apply gray scaling, contrast- and gamma correction
            img = color_corr(img, alpha=None, beta=None, gamma=0.4)

            # save the image with name 'n'
            framename = os.path.join(dst_path, f"{dst_prefix}_{:04d}.jpg".format(n))
            cv2.imwrite(framename, img)
            n += 1


def lens_corr(img, k1=0., c=2., f=1.):
    """
    Lens distortion correction based on lens characteristics.
    Function by Gerben Gerritsen / Sten Schurer, 2019

    :param img:  3D cv2 img matrix
    :param k1=0.: float - barrel lens distorition parameter
    :param c=2.: float - optical center
    :param f=1.: float - focal length
    :return undistorted img
    """

    # define imagery characteristics
    height, width, __ = img.shape

    # define distortion coefficient vector
    dist = np.zeros((4, 1), np.float64)
    dist[0, 0] = k1

    # define camera matrix
    mtx = np.eye(3, dtype=np.float32)

    mtx[0, 2] = width / c  # define center x
    mtx[1, 2] = height / c  # define center y
    mtx[0, 0] = f  # define focal length x
    mtx[1, 1] = f  # define focal length y

    # correct image for lens distortion
    corr_img = cv2.undistort(img, mtx, dist)
    return corr_img


def color_corr(img, alpha=None, beta=None, gamma=0.5):
    """
    Grey scaling, contrast- and gamma correction. Both alpha and beta need to be
    defined in order to apply contrast correction.

    Input:
    ------
    :param img: 3D cv2 img object
    :param alpha=None: float - gain parameter for contrast correction)
    :param beta=None: bias parameter for contrast correction
    :param gamma=0.5 brightness parameter for gamma correction (default: 0.5)
    :return img 2D gray scale
    Output:
    -------
    return: img gray scaled, contrast- and gamma corrected image
    """
    # turn image into grey scale
    corr_img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)

    if alpha and beta:
        # apply contrast correction
        corr_img = cv2.convertScaleAbs(corr_img, alpha=alpha, beta=beta)

    # apply gamma correction
    invGamma = 1. / gamma
    table = (np.array([((i / 255.0) ** invGamma) * 255
                       for i in np.arange(0, 256)]).astype('uint8'))

    corr_img = cv2.LUT(corr_img, table)

    return corr_img
