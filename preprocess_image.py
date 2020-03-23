import cv2
import numpy as np

def otsu_mask(image_input):
    '''
    Using OTSU method to segment the input image
    :param image_input: original image
    :return:OTSU mask
    '''
    kernel1 = np.ones((5, 5), dtype=np.uint8)
    kernel2 = np.ones((5, 5), dtype=np.uint8)
    kernel3 = np.ones((20, 20), dtype=np.uint8)
    ret1, th1 = cv2.threshold(image_input, 0, 255, cv2.THRESH_OTSU)
    image_close = cv2.erode(cv2.dilate(th1, kernel1), kernel2)
    image_erode = cv2.erode(image_close, kernel3)
    image_output = np.logical_and(th1, image_erode)
    return image_output


def applyCloseEdgeDetect(img):
    res = img.copy()
    quantized = img
    # quantized = applyKmeans(rgbImg, 5)
    grayImg = cv2.cvtColor(quantized, cv2.COLOR_BGR2GRAY)

    canny = cv2.Canny(grayImg, 120, 200)
    # sobelX = cv2.Sobel(grayImg, cv2.CV_8U, 1, 0, ksize=3)
    # sobelY = cv2.Sobel(grayImg, cv2.CV_8U, 0, 1, ksize=3)
    # sobelX = cv2.convertScaleAbs(sobelX)
    # sobelY = cv2.convertScaleAbs(sobelY)
    # sobel = cv2.addWeighted(sobelX, 0.5, sobelY, 0.5, 0);

    ret, thresh = cv2.threshold(canny, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 9))
    morphed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    if cv2.__version__.startswith("2"):
        contours, hierarchy = cv2.findContours(morphed, 0, 1)
    else:
        contours, hierarchy = cv2.findContours(morphed, 0, 1)
    for contour in contours:
        if len(contour) > 100:
            contours_poly = cv2.approxPolyDP(contour, 3, True)
            x, y, w, h = cv2.boundingRect(contours_poly)
            cv2.rectangle(res, (x, y), (x + w, y + h), (0, 255, 0), 2)

    pltShow(img, quantized, canny, morphed, res)

def binarize_image(gray_image, threshold_value=177):
    """
    Convert input_image to binary representation

    :param input_image: image
    :type input_image: numpy.ndarray
    :param threshold_value: value to be used as a
                          threshold
    :type threshold_value: int
    :return: image in binary form
    :rtype: numpy.ndarray
    """
    bin_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
    _, bin_image = cv2.threshold(bin_image,
                                 threshold_value,
                                 255,
                                 cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return bin_image

def verticalEdgeDetection(image):
    image_sobel = cv2.Sobel(image.copy(),cv2.CV_8U,1,0)
    # image = auto_canny(image_sobel)

    # img_sobel, CV_8U, 1, 0, 3, 1, 0, BORDER_DEFAULT
    # canny_image  = auto_canny(image)
    flag,thres = cv2.threshold(image_sobel,0,255,cv2.THRESH_OTSU|cv2.THRESH_BINARY)
    print(flag)
    flag,thres = cv2.threshold(image_sobel,int(flag*0.7),255,cv2.THRESH_BINARY)
    # thres = simpleThres(image_sobel)
    kernal = np.ones(shape=(3,15))
    thres = cv2.morphologyEx(thres,cv2.MORPH_CLOSE,kernal)
    return thres


def remove_background(img):
    """ Remove noise using OTSU's method.

    :param img: The image to be processed
    :return: The normalized image
    """

    img = img.astype(np.uint8)
    # Binarize the image using OTSU's algorithm. This is used to find the center
    # of mass of the image, and find the threshold to remove background noise
    threshold, _ = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Remove noise - anything higher than the threshold. Note that the image is still grayscale
    img[img > threshold] = 255

    return img


def lloret(b, g, r, img):
    '''
    The function takes arguments as original image and its color component matrices.
    It returns the segmented healthy region of leaf.
    A gray scale image is derived from original considering pixels values as values of green component pixel with highest values among other components.
    Other pixels are given zero value.
    Then, Otsu method is applied.
    '''
    row, col = b.shape

    z = np.zeros([row, col], np.uint8)

    for i in range(0, row):
        for j in range(0, col):
            if g[i][j] > b[i][j] and  g[i][j] > r[i][j]:
                z[i][j] = g[i][j]

    _, thresh = cv2.threshold(z, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    return thresh

def skeletonize(image_in):
    '''Inputs and grayscale image and outputs a binary skeleton image'''
    size = np.size(image_in)
    skel = np.zeros(image_in.shape, np.uint8)

    ret, image_edit = cv2.threshold(image_in, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    element = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
    done = False

    while not done:
        eroded = cv2.erode(image_edit, element)
        temp = cv2.dilate(eroded, element)
        temp = cv2.subtract(image_edit, temp)
        skel = cv2.bitwise_or(skel, temp)
        image_edit = eroded.copy()

        zeros = size - cv2.countNonZero(image_edit)
        if zeros == size:
            done = True

    return skel


# get grayscale image
def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# noise removal
def remove_noise(image):
    return cv2.medianBlur(image,5)

#thresholding
def thresholding(image):
    return cv2.threshold(image, 0, 255, cv2.THRESH_OTSU+cv2.THRESH_BINARY)[1]

#dilation
def dilate(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.dilate(image, kernel, iterations = 1)

#erosion
def erode(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.erode(image, kernel, iterations = 1)

#opening - erosion followed by dilation
def opening(image):
    kernel = np.ones((5,5),np.uint8)
    return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

#canny edge detection
def canny(image):
    return cv2.Canny(image, 100, 200)

#skew correction
def deskew(image):
    coords = np.column_stack(np.where(image > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

#template matching
def match_template(image, template):
    return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED)