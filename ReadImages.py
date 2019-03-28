import warnings
import pydicom
import Gaussian

import os
import numpy as np
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from tkinter import *
from tkinter import filedialog
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox

#Global Variables

#Cargar el archivo
def loadFiles():
    fileName.set(filedialog.askopenfilename(filetypes=[("Dicom files", "*.dcm")]))
    descomposeImage()
    
#Mostrar el Header
def showHeaderInfo(header):
    info_text.delete('1.0', END)
    info_text.config(state=NORMAL)  
    info = "\nPatient ID: "+header.PatientID
    info += "\nManufacturer: "+header.Manufacturer
    info += "\nStudy Description: "+header.StudyDescription
    info += "\nMR Acquisition Type: "+header.MRAcquisitionType
    info += "\nSpacing Between Slices: "+str(header.SpacingBetweenSlices)
    info += "\nPixel Bandwidth: "+str(header.PixelBandwidth)
    info += "\nRows: "+str(header.Rows)
    info += "\nColumns: "+str(header.Columns)
    info += "\nPixel Spacing : "+str(header.PixelSpacing)
    info_text.delete('1.0', END)
    info_text.insert('1.0', info)
    info_text.config(state=DISABLED)

def otsuThreshold(histgrm):
    sume = 0.0
    for i in range(len(histgrm)):
        sume += i * histgrm[i]
    sumB = 0.0
    wB = 0
    wF = 0

    varMax = 0.0
    threshold = 0
    total=len(histgrm)
    varBetween=0.0
    mB=0
    mF=0
    threshold=0

    for i in range(len(histgrm)):
        wB+=histgrm[i]              # Weight Background
        if(wB == 0):
          continue

        wF = total-wB                 # Weight Foreground
        if (wF == 0): break

        sumB += i*histgrm[i]
        

        mB = sumB/wB            # Mean Background
        mF = (sume-sumB)/wF    # Mean Foreground

        varBetween = float(wB)*float(wF)*(mB - mF)*(mB - mF)

        if (varBetween > varMax):
            varMax = varBetween
            threshold = i
    return threshold

#Convolucion
def convolution(image,kernel,scalar):
    imageRows = len(image)
    imageCols = len(image[0])
    imgAux = np.zeros([imageRows,imageCols])
    neighbours = int(len(kernel)/2)
    for i in range(0,imageRows):
        for j in range(0,imageCols):
            if i < neighbours or j < neighbours or i > imageRows - neighbours - 1 or j > imageCols - neighbours - 1:
                imgAux[i,j] = image[i,j]
                continue
            x = 0
            y = 0
            summ = 0
            for k in range(i - neighbours, i + neighbours + 1):
                for l in range(j - neighbours, j + neighbours + 1):
                    summ += (image[k,l]*kernel[x,y])
                    y += 1
                y = 0
                x += 1
            total = summ/scalar
            imgAux[i,j] = int64(total + 0.5)
    return imgAux

#Median Filter
def medianFilter(image, neighbours):
    imageRows = len(image)
    imageCols = len(image[0])
    imgAux = np.zeros([imageRows,imageCols])
    for i in range(0,imageRows):
        for j in range(0,imageCols):
            if i < neighbours or j < neighbours or i > imageRows - neighbours - 1 or j > imageCols - neighbours - 1:
                imgAux[i,j] = image[i,j]
                continue
            x = 0
            y = 0
            elements = []
            for k in range(i - neighbours, i + neighbours + 1):
                for l in range(j - neighbours, j + neighbours + 1):
                    elements.append(image[k,l])
            elements.sort()
            imgAux[i,j] = np.int64(elements[int(len(elements)/2)])
    return imgAux



#Histograma
def histogram(image):   
    rows = len(image)
    columns = len(image[0])
    intensity = [0]*65536
    
    for i in range(rows):
        for j in range(columns):
            intensity[image[i,j]] = intensity[image[i,j]]+1
            
    intensity = np.asarray(intensity)
    return intensity
    plt.plot(intensity)

    fig = plt.gcf()
    fig.canvas.set_window_title('Histogram')       
    
    plt.show()

#Filter
def applyFilter(filterName=None):
    if filterName == None:
        function = filters_cb.get()
        imgAux = np.zeros([0,0])
        if function == 'Gaussian Filter':
            imgAux = applyFilter('Gaussian')
        elif function == 'Rayleigh Filter':
            imgAux = applyFilter('Rayleigh')
        elif function == 'Median Filter':
            imgAux = applyFilter('Median')
        else:
            imgAux = originalImage.pixel_array
        return imgAux

    kernel = 0
    image = originalImage.pixel_array
    if filterName == 'Gaussian':
        kernel = Gaussian.get_gaussian_filter()
    elif filterName == 'Rayleigh':
        kernel = Gaussian.get_rayleigh_filter()
    
    '''
    for i in range(0,10):
        for j in range(0,10):
            print(image[i,j], end = " \t")
        print()'''

    if filterName == 'Median':
        filterImage = medianFilter(image,1)
    else:
        filterImage = convolution(image,kernel[0],kernel[1])
    '''
    for i in range(0,10):
        for j in range(0,10):
            print(filterImage[i,j], end = " \t")
        print()'''

    #plt.imshow(filterImage)
    #plt.show()
    processImage(filterImage)
    return filterImage

def applyOtsu():
    image = originalImage.pixel_array
    image = applyFilter()
    hist = histogram(image)
    threshold = otsuThreshold(hist)

    print("THRESHOLD --------- " + str(threshold))

    imageRows = len(image)
    imageCols = len(image[0])

    for i in range(0,imageRows):
        for j in range(0,imageCols):
            if image[i,j] <= threshold:
                image[i,j] = 0
            else:
                image[i,j] = 60000

    processImage(image)
            
def processImage(imageToShow):        
    global canvas
    text_fr.pack(padx=10, pady=10, side=BOTTOM)
    apply_bt.configure(state=NORMAL)
    f = Figure()
    a = f.add_subplot(111)
    plt.set_cmap(plt.gray())
    a.imshow(imageToShow)
    canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()  

#Procesa la imagen por primera vez, sacando el header y la imagen y mostrandola
def descomposeImage():
    global canvas        
    text_fr.pack(padx=10, pady=10, side=BOTTOM)
    apply_bt.configure(state=NORMAL)
    global originalImage
    originalImage = pydicom.read_file(fileName.get())
    showHeaderInfo(originalImage)
    
    plt.set_cmap(plt.gray())
    f = Figure()
    a = f.add_subplot(111)    
    a.imshow(originalImage.pixel_array)     
    canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()    

#Seleccioanr la funcion correspondiente    
def applyFunction():
    function = functions_cb.get()  
    print("FUNCTION ----------- " + function)  
    if function == 'Histogram':
        histogram()
    elif function == 'Otsu':
        applyOtsu()


#Interfaz
root = tk.Tk()
root.title("Image Proccesing Project")
root.configure(background='light goldenrod')
root.geometry('%dx%d+%d+%d' % (1025, 800, 0, 0))

topFrame_fr = Frame(root)
topFrame_fr.configure(background='light goldenrod')
topFrame_fr.pack(padx=10, pady=10)

selectFile = Frame(topFrame_fr)
selectFile.configure(background='light goldenrod')
selectFile.pack(padx=10, pady=10, side=LEFT)

fileName = StringVar()
label = Label(selectFile, textvariable=fileName, relief=RAISED, bg = 'white', font=("consolas"))
fileName.set("   No se ha seleccionado ningún archivo   ")

selectFolder_bt = tk.Button(selectFile, text="Seleccionar archivo", command=loadFiles, bg='white', font=("consolas"))
selectFolder_bt.pack(pady=5)

files_fr =Frame(topFrame_fr)
files_fr.configure(background='light goldenrod')
files_fr.pack(padx=10, pady=10, side=LEFT)

filter_cr =Frame(topFrame_fr)
filter_cr.configure(background='light goldenrod')
filter_cr.pack(padx=10, pady=10, side=LEFT)

filters_cb = ttk.Combobox(filter_cr, state='readonly')
filters_cb.configure(background = 'white', font=("consolas"))
filters_cb.set("Select filter")
filters_cb.grid(row=1, column=0, pady=10)
filters_cb["values"] = ['None','Gaussian Filter', 'Rayleigh Filter', 'Median Filter']

functions_cb = ttk.Combobox(files_fr, state='readonly')
functions_cb.configure(background = 'white', font=("consolas"))
functions_cb.set("Select function")
functions_cb.grid(row=1, column=0, pady=10)
functions_cb["values"] = ['Histogram','Otsu']

apply_bt = tk.Button(files_fr, text="Aplicar", command=applyFunction, bg='white', state=DISABLED, font=("consolas"))
apply_bt.grid(row=1, column=1, pady=10, padx=5)

label.pack()

text_fr = Frame(root)
text_fr.configure(background='light goldenrod')

info_text = tk.Text(text_fr, width = 90, height = 11)
info_text.pack(padx=10, pady=5)

f = Figure()
canvas = FigureCanvasTkAgg(f, master=root)

root.mainloop()