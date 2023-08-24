from PIL import Image, ImageDraw
import imageio
import numpy as np
from scipy.spatial import Delaunay
from scipy.interpolate import RectBivariateSpline
from scipy.misc import imread


def ImgArray(imgFile):
    Iopen = Image.open(imgFile)
    Iopen.load()
    array = np.array(Iopen,'uint8')
    return array

def myArr(imgFile):
    array = imageio.imread(imgFile)
    nArray = np.array(array,'uint8')
    return nArray

def points(file):
    ptsArr = np.loadtxt(file,'float64')
    return ptsArr

def saveImg(file,imgData):
    getImg = Image.fromarray(np.asarray(np.clip(imgData,0,255),'uint8'))
    getImg.save(file)

def saveRGBImg(file,imgData):
    getImg = Image.fromarray(imgData,"RGB")
    getImg.save(file)


class Affine:
    #Get source image array using numpy, pil  -> Load image into 2D pixel array
    def __init__(self,source,destination):

        if (source.shape != (3,2)) or (destination.shape != (3,2)):
            raise ValueError('Dimensions of either source or destination array are incorrect.')
        if (source.dtype != 'float64') or (destination.dtype != 'float64'):
            raise ValueError('Image arrays not of type float64')

        self.source = source
        self.destination = destination
        self.matrix = self.getH(source,destination)
	
	
    def getH(self,source,destination):

        #Ah = b
        #source,destination:
        #  0   1
        #0[x1,y1]
        #1[x2,y2]
        #2[x3,y3]
        A = np.array([[source[0,0],source[0,1],1,0,0,0],
                     [0,0,0,source[0,0],source[0,1],1],
                     [source[1,0],source[1,1],1,0,0,0],
                     [0,0,0,source[1,0],source[1,1],1],
                     [source[2,0],source[2,1],1,0,0,0],
                     [0,0,0,source[2,0],source[2,1],1]])

        b = np.array([[destination[0,0]],[destination[0,1]],[destination[1,0]],[destination[1,1]],[destination[2,0]],[destination[2,1]]])
        #get h (6x1) using linalg
        h = np.linalg.solve(A,b)
        #print(h)
        #print("solving matrix - I am working")
        H = np.array([[h[0,0],h[1,0],h[2,0]],
                      [h[3,0],h[4,0],h[5,0]],
                      [0,0,1]])
        #H = np.array(([[h[0,0],h[1,0],h[2,0]],[h[3,0],h[4,0],h[5,0]],[0,0,1]]),'float64')
        #print(H)
        return H

    def transform(self,sourceImage,destinationImage):

        width = sourceImage.shape[1]
        height = sourceImage.shape[0]

        if (not(isinstance(sourceImage,np.ndarray))) or (not(isinstance(destinationImage,np.ndarray))):
            raise TypeError('One or more of the inputs is not of type ndarray.')


        #generate binary mask

        #vertices tuple with values from destination(mid tri)
        vertices = []
        for everyCoor in self.destination:
            vertices.append(tuple(everyCoor))

        img = Image.new('L',(width,height),0)
        #draw and fill triangle with white
        ImageDraw.Draw(img).polygon(vertices,outline=255,fill=255)
        #convert to numpy array
        mask = np.array(img)
        #nonzero
        blankFill = (np.nonzero(mask))  #gives tuple containing 2 arrays with x and y
        # blankX = blankFill[0]
        # blankY = blankFill[1]
        blankX = blankFill[1]
        blankY = blankFill[0]

        pairedUp = zip(blankX,blankY)

        #2D interpolation
        interpol = RectBivariateSpline(np.arange(height),np.arange(width),sourceImage,kx=1,ky=1)
        #Matrix multiplication
        #a.dot(b)

        Hinv = np.linalg.inv(self.matrix)
        #print("inverse matrix - I am working")
        #print(Hinv)

        for (x,y) in pairedUp:
            multiplicand = np.array([[x],[y],[1]])
            affTransform = np.matmul(Hinv,multiplicand)
            destinationImage[y,x] = interpol.ev(affTransform[1],affTransform[0])

    #Delauney triangulation
    # -> 3x2 numpy array of float64 with triangle vertices goes to 'source'

    #Find location of feature pts in morphed image
    # -> destination:  A 3×2 numpy array of type float64 containing vertices of the corresponding triangle vertices in the target image.


    #Calculate affine transformation
    # -> matrix :  A 3×3 numpy array of type float64 holding the affine projection matrix

    # 2D interpolation; (scipy.interpolate.RectBivariateSpline())


class Blender:

    def __init__(self,startImage,startPoints,endImage,endPoints):

        if (not(isinstance(startImage,np.ndarray)) or not(isinstance(startPoints,np.ndarray)) or not(isinstance(endImage,np.ndarray)) or not(isinstance(endPoints,np.ndarray))):
            raise TypeError('One or more of the inputs is not of type ndarray.')


        self.startImage = startImage
        self.startPoints = startPoints
        self.endImage = endImage
        self.endPoints = endPoints


        self.delTri = Delaunay(self.startPoints)



    def getBlendedImage(self,alpha):



        width = self.startImage.shape[1]
        height = self.startImage.shape[0]

        blank1 = Image.new('L',(width,height),0)
        bNpArr1 = np.array(blank1,'uint8')
        blank2 = Image.new('L',(width,height),0)
        bNpArr2 = np.array(blank2,'uint8')

        for triangle in self.delTri.simplices:
            sCoorList = []
            eCoorList = []
            mCoorList = []
            for vertex in triangle:
                xS = self.startPoints[vertex][0]
                yS = self.startPoints[vertex][1]
                sCoorList.append([xS,yS])

                xE = self.endPoints[vertex][0]
                yE = self.endPoints[vertex][1]
                eCoorList.append([xE,yE])

                xM = (1 - alpha)*xS + alpha*xE
                yM = (1 - alpha)*yS + alpha*yE
                mCoorList.append([xM,yM])

            start_tri = np.array(sCoorList,'float64')
            end_tri = np.array(eCoorList,'float64')
            mid_tri = np.array(mCoorList,'float64')

            #blank image
            #make affine classes
            sAff = Affine(start_tri,mid_tri)
            eAff = Affine(end_tri,mid_tri)

            #pass into affine.transform
            sAff.transform(self.startImage,bNpArr1)
            eAff.transform(self.endImage,bNpArr2)


        #new = Image.new('L',(width,height),0)
        #finalArr = np.array(new,'uint8')
        finalArr = (1-alpha)*bNpArr1 + alpha*bNpArr2
        finalArr = np.array(finalArr,'uint8')
        return finalArr


def loadColorImg(file):
    rgbImg = imread(file)
    return rgbImg


class ColorAffine:
    #Get source image array using numpy, pil  -> Load image into 2D pixel array
    def __init__(self,source,destination):

        if (source.shape != (3,2)) or (destination.shape != (3,2)):
            raise ValueError('Dimensions of either source or destination array are incorrect.')
        if (source.dtype != 'float64') or (destination.dtype != 'float64'):
            raise ValueError('Image arrays not of type float64')

        self.source = source
        self.destination = destination
        self.matrix = self.getH(source,destination)



    def getH(self,source,destination):

        #Ah = b

        #source,destination:
        #  0   1
        #0[x1,y1]
        #1[x2,y2]
        #2[x3,y3]
        A = np.array([[source[0,0],source[0,1],1,0,0,0],
                     [0,0,0,source[0,0],source[0,1],1],
                     [source[1,0],source[1,1],1,0,0,0],
                     [0,0,0,source[1,0],source[1,1],1],
                     [source[2,0],source[2,1],1,0,0,0],
                     [0,0,0,source[2,0],source[2,1],1]])

        b = np.array([[destination[0,0]],[destination[0,1]],[destination[1,0]],[destination[1,1]],[destination[2,0]],[destination[2,1]]])
        #get h (6x1) using linalg
        h = np.linalg.solve(A,b)
        #print(h)
        #print("solving matrix - I am working")
        H = np.array([[h[0,0],h[1,0],h[2,0]],
                      [h[3,0],h[4,0],h[5,0]],
                      [0,0,1]])
        #H = np.array(([[h[0,0],h[1,0],h[2,0]],[h[3,0],h[4,0],h[5,0]],[0,0,1]]),'float64')
        #print(H)
        return H

    def transform(self,sourceImage,destinationImage):

        if (not(isinstance(sourceImage,np.ndarray))) or (not(isinstance(destinationImage,np.ndarray))):
            raise TypeError('One or more of the inputs is not of type ndarray.')


        #generate binary mask

        #vertices tuple with values from destination(mid tri)
        vertices = []
        for everyCoor in self.destination:
            vertices.append(tuple(everyCoor))

        width = sourceImage.shape[1]
        height = sourceImage.shape[0]

        #for cI in range(3):

        img = Image.new('RGB',(width,height),0)
        #draw and fill triangle with white
        ImageDraw.Draw(img).polygon(vertices,outline=255,fill=255)
        #convert to numpy array
        mask = np.array(img)
        #nonzero
        blankFill = (np.nonzero(mask))  #gives tuple containing 2 arrays with x and y
        # blankX = blankFill[0]
        # blankY = blankFill[1]
        blankX = blankFill[1]
        blankY = blankFill[0]

        pairedUp = zip(blankX,blankY)

        #2D interpolation
        interpol1 = RectBivariateSpline(np.arange(sourceImage.shape[0]),np.arange(sourceImage.shape[1]),sourceImage[:,:,0],kx=1,ky=1)
        interpol2 = RectBivariateSpline(np.arange(sourceImage.shape[0]),np.arange(sourceImage.shape[1]),sourceImage[:,:,1],kx=1,ky=1)
        interpol3 = RectBivariateSpline(np.arange(sourceImage.shape[0]),np.arange(sourceImage.shape[1]),sourceImage[:,:,2],kx=1,ky=1)

        #Matrix multiplication
        #a.dot(b)

        Hinv = np.linalg.inv(self.matrix)
        #print("inverse matrix - I am working")
        #print(Hinv)

        for (x,y) in pairedUp:
            multiplicand = np.array([[x],[y],[1]])
            affTransform = np.matmul(Hinv,multiplicand)
            destinationImage[y,x,0] = interpol1.ev(affTransform[1],affTransform[0])
            destinationImage[y,x,1] = interpol2.ev(affTransform[1],affTransform[0])
            destinationImage[y,x,2] = interpol3.ev(affTransform[1],affTransform[0])




class ColorBlender:

    def __init__(self,startImage,startPoints,endImage,endPoints):

        if (not(isinstance(startImage,np.ndarray)) or not(isinstance(startPoints,np.ndarray)) or not(isinstance(endImage,np.ndarray)) or not(isinstance(endPoints,np.ndarray))):
            raise TypeError('One or more of the inputs is not of type ndarray.')


        self.startImage = startImage
        self.startPoints = startPoints
        self.endImage = endImage
        self.endPoints = endPoints


        self.delTri = Delaunay(self.startPoints)



    def getBlendedImage(self,alpha):

        width = self.startImage.shape[1]
        height = self.startImage.shape[0]

        #blank1 = Image.new('L',(800,600),0)
        blank1 = Image.new('RGB',(width,height),0)
        bNpArr1 = np.array(blank1,'uint8')
        blank2 = Image.new('RGB',(width,height),0)
        bNpArr2 = np.array(blank2,'uint8')

        for triangle in self.delTri.simplices:
            sCoorList = []
            eCoorList = []
            mCoorList = []
            for vertex in triangle:
                #xS = self.startImage[i][0]
                #yS = self.startImage[i][1]
                xS = self.startPoints[vertex][0]
                yS = self.startPoints[vertex][1]
                sCoorList.append([xS,yS])

                # xE = self.endImage[i][0]
                # yE = self.endImage[i][1]
                xE = self.endPoints[vertex][0]
                yE = self.endPoints[vertex][1]
                eCoorList.append([xE,yE])

                xM = (1 - alpha)*xS + alpha*xE
                yM = (1 - alpha)*yS + alpha*yE
                mCoorList.append([xM,yM])

            start_tri = np.array(sCoorList,'float64')
            end_tri = np.array(eCoorList,'float64')
            mid_tri = np.array(mCoorList,'float64')

            #blank image
            #make affine classes
            sAff = ColorAffine(start_tri,mid_tri)
            eAff = ColorAffine(end_tri,mid_tri)

            #pass into affine.transform
            sAff.transform(self.startImage,bNpArr1)
            eAff.transform(self.endImage,bNpArr2)


        new = Image.new('RGB',(width,height),0)
        finalArr = np.array(new,'uint8')
        for r in range(width):
            for c in range(height):
                finalArr[c,r,0] = (1-alpha)*bNpArr1[c,r,0] + alpha*bNpArr2[c,r,0]
                finalArr[c,r,1] = (1-alpha)*bNpArr1[c,r,1] + alpha*bNpArr2[c,r,1]
                finalArr[c,r,2] = (1-alpha)*bNpArr1[c,r,2] + alpha*bNpArr2[c,r,2]
                #print("Blending - I am working {}".format(finalArr[y][x]))
        #finalArr = np.array(finalArr,'uint8')
        return finalArr


if __name__ == "__main__":

    sArr = loadColorImg('Tiger2Color.jpg')
    sPts = (points('tiger2.jpg.txt'))
    eArr = loadColorImg('WolfColor.jpg')
    ePts = points('wolf.jpg.txt')

    #cArr = loadColorImg('Tiger2Color.jpg')
    #print(cArr)
    s2Arr = loadColorImg('Tiger2Gray.jpg')
    #sPts = (points('tiger2.jpg.txt'))
    e2Arr = loadColorImg('WolfGray.jpg')
    #ePts = points('wolf.jpg.txt')


    newBlend2 = Blender(s2Arr,sPts,e2Arr,ePts)
    finalArr2 = newBlend2.getBlendedImage(0.5)
    saveImg('newestGray.jpg',finalArr2)

    #newBlend = ColorBlender(sArr,sPts,eArr,ePts)
    #finalArr = newBlend.getBlendedImage(0.25)
    #saveRGBImg('newColor.jpg',finalArr)
