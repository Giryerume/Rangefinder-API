#!/usr/bin/env python
# coding: utf-8


# Imports

import numpy as np
import imutils
import cv2
import math
from imutils import paths


#Constantes

MARKER_1_HEIGHT = 105 # altura do marcador1 (mm)
MARKER_2_HEIGHT = 110 # altura do marcador2 (mm)
FOCAL_LENGTH = 4.3 # distancia focal da camera (mm)
SENSOR_HEIGHT = 4.1 # altura do sensor da camera (mm)


# Funções

def find_marker(image):
    # converte imagem para escala de cinza, desfoca ela, e detecta arestas
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 75, 200)
    edged = cv2.dilate(edged, None, iterations=1)
    edged = cv2.erode(edged, None, iterations=1)

    # passos
    #cv2_imshow(image)
    #cv2_imshow(gray)
    #cv2_imshow(edged)

    # encontra os contornos na imagem com arestas
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    # assume-se que será o marcador na imagem
    cnts = imutils.grab_contours(cnts)

    # escolhe contorno de quatro pontos
    cnts = sorted(cnts, key = cv2.contourArea, reverse = True)[:5]
    #cnts = sorted(cnts, key=lambda cnts: cv2.boundingRect(cnts)[0] + cv2.boundingRect(cnts)[1] * image.shape[1], reverse = True)[:5]

    # percorre os contornos
    for c in cnts:
        # aproxima o contorno
        peri = cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, 0.02 * peri, True)
        # se o contorno aproximado tem quatro pontos, então assume-se que o marcador foi encontrado
        if len(approx) == 4:
            marker = approx
            break

    # calcula o bounding box da região do marcador e retorna ela
    return cv2.minAreaRect(marker)

# calcula e retorna a distancia do marcador até a camera
def distance_to_camera(image, knownHeight, focalLength, perHeight, sensor):
    return ((focalLength * knownHeight * image.shape[1])  / (perHeight * sensor))

# calcula e retorna a distancia focal da camera
def compute_focal_length(image, knownHeight, knownDistance, perHeight, sensor):
    return (knownDistance * perHeight * sensor)/(image.shape[1] * knownHeight)

# redimensiona uma imagem
def resize(image, pct):
    return cv2.resize(image, (0,0), fx=pct/100, fy=pct/100)

# computa o centro do contorno
def contour_center(c):
    M = cv2.moments(c)
    x = int(M["m10"] / M["m00"])
    y = int(M["m01"] / M["m00"])
    return x, y

def rangefinder(image, height, focall):
    # detecta o marcador e calcula a distancia até a camera
    marker = find_marker(image)
    dist = distance_to_camera(image, height, focall, marker[1][1], SENSOR_HEIGHT)

    # mostra o boundbox e a distancia sobreposta a imagem
    box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
    box = np.int0(box)

    # computa o centro do contorno
    cX, cY = contour_center(box)

    # desenha contornos do boundbox na imagem
    cv2.drawContours(image, [box], -1, (0, 0, 255), 2)
    cv2.circle(image, (cX, cY), 5, (0, 0, 255), -1)

    # desenha mostrador da distancia na imagem
    cv2.putText(image, "%.2fm" % (dist/1000),
              (image.shape[1] - int(image.shape[1]/1.65),
               image.shape[0] - 20),
               cv2.FONT_HERSHEY_SIMPLEX,
               1.0, (0, 0, 255), 2)

    # mostra imagem final com boundbox e mostrador
    #cv2.imshow('Result',image)
    #cv2.waitKey(0)
    #cv2.destroyAllWindows()
    return image


# Calibragem
def calibrate(image, dist, height):
    return compute_focal_length(image, height, dist, find_marker(image)[1][1], SENSOR_HEIGHT)
