import pydicom
import numpy as np
import os

from matplotlib import pyplot as plt

#%matplotlib inline

lstFilesDCM = []

def loadImageRoute(route):
    PathDicom = route
    for dirName, subdirList, fileList in os.walk(PathDicom):
        for filename in fileList:
            if ".dcm" in filename.lower():  # check whether the file's DICOM
                lstFilesDCM.append(os.path.join(dirName,filename))
                
    #Lets check what we have in the list
    print(lstFilesDCM)

def getDataImage(numImage):
    RefDs = pydicom.dcmread(lstFilesDCM[numImage])

    ConstPixelDims = (int(RefDs.Rows), int(RefDs.Columns), len(lstFilesDCM))

    try:
        SliceThickness = float(RefDs.SliceThickness)
    except AttributeError:
        SliceThickness = 1.0

    ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), SliceThickness)
    
    #print("Ref DS")
    
    #print("Const PixelSpacing")
    #print(ConstPixelSpacing)
    
    #print("ConstPixelDims")
    #print(ConstPixelDims)
    
    x = np.arange(0.0, (ConstPixelDims[0]+1)*ConstPixelSpacing[0], ConstPixelSpacing[0])
    y = np.arange(0.0, (ConstPixelDims[1]+1)*ConstPixelSpacing[1], ConstPixelSpacing[1])
    z = np.arange(0.0, (ConstPixelDims[2]+1)*ConstPixelSpacing[2], ConstPixelSpacing[2])

    half = int(np.round(x.shape[0] / 2))
    print(x[:half])
    
    ArrayDicom = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)

    # loop through all the DICOM files
    for filenameDCM in lstFilesDCM:
        # read the file
        ds = pydicom.dcmread(filenameDCM)
        
        print('DS')
        print(ds)
        print(ds.Rows)
        print(ds.Columns)
        
        # store the raw image data
        ArrayDicom[:, :, lstFilesDCM.index(filenameDCM)] = ds.pixel_array
        
        #print(ds.pixel_array)
        #plt.imshow(np.flipud(ArrayDicom[:, :, 0])) 
    
def readImages():
    print('Leyendo...')

def main():
    route = './'
    loadImageRoute(route)
    getDataImage(0)
    readImages()
    
if __name__ == "__main__":
    main()
