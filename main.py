#-------------------------------------------------------------------------------
# Name:        Tarea 2 Compiladores
# Purpose:
#
# Author:      Arturo Chaves + Victor Viquez
#
# Created:     01/03/2018
# Copyright:   (c) Artch92 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------

# import the necessary packages
from PIL import Image
import pytesseract
import cv2
import os
import re

# '1001-LV-SJO-HER-ALA.jpg'
images = ['horarios/1001-LV-SJO-HER-ALA_tabla.png', 'horarios/1002-LV-ALA-HER-SJO_tabla.png']

def main():
    print("iniciando el programa")

    for image_path in images:
        filename = clean_image(image_path, "blur")
        filename = clean_image(filename, "thresh")

        textual_trips = get_lines(filename)
        os.remove(filename)

        schedule = parse_times(textual_trips)
        schedule = fix_schedule(schedule, image_path)

        print(schedule)

        #schedule = fix_schedule(schedule, image_path)

        # debug
        #print("time table: ", image_path)
        #for trip in schedule:
        #    print(trip)*/

def ensureUtf(s):
  try:
      if type(s) == unicode:
        return s.encode('utf8', 'ignore')
  except:
    return str(s)


def clean_image(image_path, preprocess):
    # load the example image and convert it to grayscale
    image = cv2.imread(image_path)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # check to see if we should apply thresholding to preprocess the
    # image
    if preprocess == "thresh":
        gray = cv2.threshold(gray, 0, 255,
        cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

    # make a check to see if median blurring should be done to remove
    # noise
    elif preprocess == "blur":
        gray = cv2.medianBlur(gray, 3)

    # write the grayscale image to disk as a temporary file so we can
    # apply OCR to it
    filename = "{}.png".format(os.getpid())
    cv2.imwrite(filename, gray)

    # load the image as a PIL/Pillow image, apply OCR, and then delete
    # the temporary file
    #text = pytesseract.image_to_string(Image.open(filename))
    #os.remove(filename)


    # show the output images
    #cv2.imshow("Image", image)
    #cv2.imshow("Output", gray)
    #return ensureUtf(text)
    return filename

def fix_schedule(trips_schedules, route):
    '''
    custom method
    '''

    schedule = ''

    if "SJO-HER-ALA" in route:
        # debug
        # print("ruta SJO - Heredia - Alajuela")
        stops = ['Ulatina', 'UCR', 'Estación Atlantico', 'Colimna', 'Santa Rosa', 'Miraflores', 'Estación Heredia', 'San Francisco', 'San Joaquín', 'Río Segundo', 'Alajuela']
        schedule = '\nHorario de SJO-HER-ALA:\n'

    elif "ALA-HER-SJO" in route:
        # debug
        # print("ruta ALA-HER-SJO")
        stops = ['Alajuela', 'Río Segundo', 'San Joaquín', 'San Franscisco', 'Estación Heredia', 'Miraflores', 'Santa Rosa', 'Colima', 'Estación Atlántico', 'UCR', 'Ulatina']
        schedule = '\nHorario de ALA-HER-SJO:\n'

    stop_value = 0
    journey = []
    for trip in trips_schedules:
        if trip != []:
            if journey == []:
                schedule = schedule + '\n' + 'Parada ' + str(stop_value + 1) + ':\n'
                journey.append(trip[0])
                schedule = schedule + '[' + trip[0] + ']'
            else:
                #print(str(journey[-1]) + ' vs ' + trip[0])
                if str(journey[-1]) < trip[0]:
                    journey.append(trip[0])
                    schedule = schedule + '[' + trip[0] + ']'
                else:
                    stop_value = stop_value + 1
                    schedule = schedule + '\n' + 'Parada ' + str(stop_value + 1) + ':\n'
                    journey = []
                    journey.append(trip[0])
                    schedule = schedule + '[' + trip[0] + ']'
    return schedule


def get_lines(filename):
    '''
    Args
    ::filename (str): Image file relative or absolute path.

    Return:
    ::list: List of lines as text from the image. Every line contain the stop
      times for a certain trip.
    '''

    text = ensureUtf(pytesseract.image_to_string(Image.open(filename)))

    textual_lines = []
    line = ''
    line_num = 0
    for char in text:
        line += char
        if char == "\n":
            # ignore lines with less than 5 chars (H:MM)
            if len(line) < 5:
                line = ''
                continue
            else:
                line_num += 1
                # debug
                # print('linea: "', line, '" numero: ', line_num,
                # q      'largo de linea: ', len(line))
                textual_lines.append(line)
                line = ''

    return textual_lines


def parse_times(textual_trips):
    '''
    Arguments:
    ::textual_trips is a str representing a trip recognized from the image.

    ::return a list of trips schedules lists. A schedule list contains stop
      times of type str.
    '''

    pattern = "(?P<hours>[0-9]|0[0-9]|1[0-9]|2[0-3])(:| |)(?P<minutes>[0-5][0-9])"
    trips_schedules = []

    for line in textual_trips:
        result = re.compile(pattern)
        stop_times = []

        for match in result.finditer(line):
            # debug
            # print(match.groupdict())
            hours = match.groupdict()['hours']
            minutes = match.groupdict()['minutes']
            stop_times += [hours + ":" + minutes]

        # debug
        # print("\nagregando stop times: ")
        # print(stop_times)
        trips_schedules += [stop_times]

    return trips_schedules


if __name__ == "__main__":
    main()
