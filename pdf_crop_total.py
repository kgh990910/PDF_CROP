import cv2
import numpy as np
from pdf2image import convert_from_path
from PyPDF2 import PdfFileReader, PdfFileWriter

coordi_mouse = list()


def mouse_callback(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"({x}, {y})")
        coordi_mouse.append([x, y])


PDF_Name = input("File_Name : ")

print(f"File :{PDF_Name}")

Out_Name = input("OutPut File Name : ")

crop_count = int(input("Crop Page Count : "))

reader = [0] * crop_count
coord_x = [0] * crop_count * 2
coord_y = [0] * crop_count * 2
print("Generate Reader")

for i in range(crop_count):
    reader[i] = PdfFileReader("./source/"+PDF_Name, 'rb')
print("Finish Reading File")

writer = PdfFileWriter()
print("Generate Writer")

page = reader[0].getPage(0)

x1, y1 = page.cropBox.getLowerLeft()  # (c,d)
x2, y2 = page.cropBox.getUpperRight()  # (c,d)
pdf_x = float(x2 - x1)
pdf_y = float(y2 - y1)

print(f"Page : {reader[0].numPages}")
print(f"Result page: {reader[0].numPages * crop_count}")
while True:
    crop_type = int(input("Choose Crop Method. Manual(0) or Mouse(1)? : "))
    if crop_type != 0 and crop_type != 1:
        print("Wrong! Try Again")
    elif crop_type == 0 or crop_type == 1:
        break

if crop_type == 0:
    a, b = page.cropBox.getLowerLeft()  # (a,b)
    c, d = page.cropBox.getUpperRight()  # (c,d)
    print(f"LowerLeft({a}, {b}), UpperRight({c}, {d})")
    for i in range(crop_count):
        coord_x[2 * i] = float(input(f"page{i} LowerLeft X coordinate : "))
        coord_y[2 * i] = float(input(f"page{i} LowerLeft Y coordinate : "))
        coord_x[2 * i + 1] = float(input(f"page{i} UpperRight X coordinate : "))
        coord_y[2 * i + 1] = float(input(f"page{i} UpperRight Y coordinate : "))

elif crop_type == 1:
    print("for using mouse, convert pdf to image")
    print("if pdf have many pages, this job is long")
    images = convert_from_path("./source/" + PDF_Name)

    print("Finish Converting")
    numpy_image = np.array(images[0])
    print("Generate np array")
    opencv_image = cv2.cvtColor(numpy_image, cv2.COLOR_RGB2BGR)
    print("Finish Convert np array to image")
    jpg_h, jpg_w, c = opencv_image.shape

    jpg_h = float(jpg_h)
    jpg_w = float(jpg_w)

    print(f"{jpg_w}, {jpg_h}")

    for i in range(crop_count):
        print(f"Click Mouse LeftButton to page{i+1} Crop")
        print("First Click is LowerLeft, Second Click is UpperRight")
        cv2.namedWindow("sample")
        cv2.setMouseCallback("sample", mouse_callback)
        cv2.imshow("sample", opencv_image)
        while True:

            if len(coordi_mouse) == 2:

                coord_x[2 * i] = float((coordi_mouse[0][0])/jpg_w * pdf_x)
                coord_y[2 * i] = float((jpg_h - coordi_mouse[0][1])/jpg_h * pdf_y)
                coord_x[2 * i + 1] = float((coordi_mouse[1][0])/jpg_w * pdf_x)
                coord_y[2 * i + 1] = float((jpg_h - coordi_mouse[1][1])/jpg_h * pdf_y)

                coordi_mouse.clear()
                break
            k = cv2.waitKey(1) & 0xFF
            if k == 27:
                break

    cv2.destroyAllWindows()

    for i in range(crop_count):
        print(f"{coord_x[2 * i]}, {coord_y[2*i]}")
        print(f"{coord_x[2 * i + 1 ]}, {coord_y[2*i+1]}")

for i in range(0, reader[0].numPages):
    for j in range(crop_count):
        page = reader[j].getPage(i)

        page.cropBox.setLowerLeft((coord_x[2 * j], coord_y[2 * j]))
        page.cropBox.setUpperRight((coord_x[2 * j + 1], coord_y[2 * j + 1]))

        writer.addPage(page)
        print(f"Add Page {j + 1}")

    print(f"Processing {i + 1}/{reader[0].numPages}")

outstream = open(Out_Name + ".pdf", 'wb')
writer.write(outstream)
outstream.close()
print("Finish")
