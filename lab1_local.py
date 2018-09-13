from tkinter import filedialog
from tkinter import *
import tkinter as tk
import tkinter.ttk as ttk
import os
import dicom
import numpy as np
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


lstFilesDCM = []
      
def headerInfo():   
    info_text.delete('1.0', END)
    processImage()

def selectFolder():    
    folder =  filedialog.askdirectory()
    loadFiles(folder)

def loadFiles(folder):
    resetSelector()
    lstFilenames = []
    for dirName, subdirList, fileList in os.walk(folder):
        for filename in fileList:
            if ".dcm" in filename.lower():
                lstFilesDCM.append(os.path.join(dirName,filename))
                lstFilenames.append(filename)
    
    cb["values"] = lstFilenames    
    files_fr.pack() 
   

def resetSelector():
    global lstFilesDCM
    lstFilesDCM.clear()
    info_text.delete('1.0', END)
    cb.set("Select a DICOM file")    
    
def showHeaderInfo(header):
    info = "--------------------HEADER INFORMATION--------------------\n"
    info += "\nManufacturer: "+header.Manufacturer
    info += "\nStudy Description: "+header.StudyDescription
    info += "\nMR Acquisition Type: "+header.MRAcquisitionType
    info += "\nSpacing Between Slices: "+str(header.SpacingBetweenSlices)
    info += "\nPixel Bandwidth: "+str(header.PixelBandwidth)
    info += "\nRows: "+str(header.Rows)
    info += "\nColumns: "+str(header.Columns)
    info += "\nPixel Spacing : "+str(header.PixelSpacing)
    info_text.insert('1.0', info)
            
def processImage():
    global canvas
    RefDs = dicom.read_file(lstFilesDCM[cb.current()])
    showHeaderInfo(RefDs)   
    
    # Load dimensions based on the number of rows, columns, and slices (along the Z axis)
    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(lstFilesDCM))
    # Load spacing values (in mm)
    try:
        SliceThickness = float(RefDs.SliceThickness)
    except AttributeError:
            SliceThickness = 1.0
    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), SliceThickness)
    #Create the array staring from 0, to ConstPixelDims[0]+1 (because stop is an open interval) 
    #and the ConstPixelSpacing gives the scale to the volume. 
    #If ConstPixelSpacing == 1, then values go to ConstPixelDims[0]+1. It creates a cube.
    x = np.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
    y = np.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
    z = np.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])
        
    half = int(np.round(x.shape[0] / 2))
    # The array is sized based on 'ConstPixelDims'
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)
        
    for filenameDCM in lstFilesDCM:
        # read the file
        ds = dicom.read_file(filenameDCM)
        # store the raw image data
        ArrayDicom[:, :, lstFilesDCM.index(filenameDCM)] = ds.pixel_array
        
    plt.figure(dpi=100)
    plt.axes().set_aspect('equal')
    plt.set_cmap(plt.gray())
    plt.pcolormesh(x, y, np.flipud(ArrayDicom[:, :, 0]))        
    f = Figure()
    a = f.add_subplot(111)    
    a.imshow(np.flipud(ArrayDicom[:, :, 0])) 
    canvas.get_tk_widget().destroy()
    canvas = FigureCanvasTkAgg(f, master=root)
    canvas.draw()
    canvas.get_tk_widget().pack()    
    
#TK components
root = tk.Tk()
root.title("Medical Imaging")
root.geometry("650x600")

selectFolder_fr = Frame()
selectFolder_fr.pack()

selectFolder_bt = tk.Button(selectFolder_fr, text="Select folder", command=selectFolder)
selectFolder_bt.pack(pady=5)

files_fr =Frame()

cb = ttk.Combobox(files_fr, state='readonly')
cb.set("Select a DICOM file")
cb.pack(padx=20, pady=5)

process_bt = tk.Button(files_fr, text="Process file", command=headerInfo)
process_bt.pack(pady=5)

info_text = tk.Text(files_fr, width = 60, height = 10)
info_text.pack(pady=5)

f = Figure()
canvas = FigureCanvasTkAgg(f, master=root)

root.mainloop()
