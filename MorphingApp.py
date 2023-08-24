# Import PySide classes
import sys
from PySide.QtCore import *
from PySide.QtGui import *
import numpy as np

from scipy.spatial import Delaunay

from PIL import ImageDraw
from Morphing import *
from MorphingGUI import *

def points(file):
    ptsArr = np.loadtxt(file,'float64')
    return ptsArr


class MorphingApp(QMainWindow, Ui_Dialog):

    def __init__(self, parent=None):

        super(MorphingApp, self).__init__(parent)
        self.setupUi(self)
        self.startPts = None
        self.endPts = None
        self.blendBtn.setEnabled(False)
        self.horizontalSlider.setTickInterval(5)
        self.horizontalSlider.setEnabled(False)
        self.alphaTextBox.setAlignment(Qt.AlignCenter)
        self.alphaTextBox.setText(str(float(self.horizontalSlider.value())))
        self.alphaTextBox.setDisabled(True)


        self.alpha = None

        self.startFile = None      #Image file for start image
        self.endFile = None

        self.startFlag = 0         #DONT EVEN KNOW WHY THIS IS HERE CHECK CHECK CHECK
        self.endFlag = 0

        self.showStartFlag = 0          #Original flag for basic stuff,in showPoints and all
        self.showEndFlag =0

        self.onlyImStartScene = None        #The current GraphicsScene for the start image without a pts file
        self.onlyImEndScene = None          #The current GraphicsScene for the end image without a pts file

        #self.onlyImScene = None
        self.file = None
        self.nowStart = 0 #CHECK IF YOU STILL NEED THESE 2
        self.nowEnd = 0

        self.onlyImSPtsFile = None
        self.onlyImEPtsFile = None

        self.goodSscene = None
        self.goodEscene = None

        #Following 4: current clicked coordinates for start and end (s,e)
        self.Sx = None
        self.Sy = None

        self.Ex = None
        self.Ey = None

        #self.BSpresses = 0

        self.BSstart = 0
        self.BSend = 0

        self.saved = 0

        self.startDone = 0      #to check if start image point choosing is done
        self.endDone = 0        #to check if end image point choosing is done

        self.mouseFlag = 1
        #self.startItems = []
        #self.endItems = []

        self.triFlag = 0
        self.afterTri = 0

        self.Escene = None
        self.Sscene = None

        self.drewS = 0

        self.SnewCoords= []
        self.EnewCoords = []
        self.StempCoords = []
        self.EtempCoords = []

        self.tempItem = None

        self.SthroughDel = 0
        self.EthroughDel = 0

        self.started = 0

        self.notDone = 0
        self.splCase = 0
        self.loadStart.clicked.connect(self.loadStartData)
        self.loadEnd.clicked.connect(self.loadEndData)

        self.checkBox.toggled.connect(self.loadDelTri)

        self.horizontalSlider.valueChanged.connect(self.showAlpha)

        self.blendBtn.clicked.connect(self.blendFunc)



    def enWidgets(self):
        if (self.startFlag == 1 and self.endFlag == 1):
            self.blendBtn.setEnabled(True)
            self.horizontalSlider.setEnabled(True)
            self.alphaTextBox.setDisabled(False)

            self.horizontalSlider.setTickInterval(5)
            self.horizontalSlider.setSingleStep(5)


    def loadStartData(self):
        """
        Obtain a file name from a file dialog, and pass it on to the loading method. This is to facilitate automated
        testing. Invoke this method when clicking on the 'load' button.

        *** DO NOT MODIFY THIS METHOD! ***
        """
        filePath, _ = QFileDialog.getOpenFileName(self, caption='Open PNG or JPG file ...', filter=("Images (*.png *.jpg)"))

        if not filePath:
            return

        self.loadStartFunc(filePath)


    def loadStartFunc(self,fileName):
            self.triFlag = 0

            #print('In load start')

            self.startFile = fileName

            scn = QGraphicsScene()
            pixmap = QPixmap(fileName)
            scn.addPixmap(pixmap)
            self.onlyImStartScene = scn
            self.startImage.setScene(scn)
            #self.startImage.scale(0.497,0.4966)
            self.startImage.fitInView(scn.sceneRect(),Qt.KeepAspectRatio)

            ptsFile = fileName+'.txt'
            self.onlyImSPtsFile = ptsFile

            try:
                self.startPts = np.loadtxt(ptsFile)
            except:
                #print('No file')
                self.triFlag = 0
                pass


            self.startFlag = 1
            self.enWidgets()
            self.showStartFlag = 1
            self.showEndFlag = 0
            #if (self.triFlag == 0):
            self.showPoints(fileName)
            #else:
                #self.newShow(fileName)




    def loadEndData(self):
        """
        Obtain a file name from a file dialog, and pass it on to the loading method. This is to facilitate automated
        testing. Invoke this method when clicking on the 'load' button.

        *** DO NOT MODIFY THIS METHOD! ***
        """
        #match = re.search(r'')
        filePath, _ = QFileDialog.getOpenFileName(self, caption='Open PNG or JPG file ...', filter=("Images (*.png *.jpg)"))

        if not filePath:
            return

        self.loadEndFunc(filePath)


    def loadEndFunc(self,fileName):
            self.triFlag = 0

            #print('In load end')

            self.endFile = fileName

            scn = QGraphicsScene()
            pixmap = QPixmap(fileName)
            scn.addPixmap(pixmap)
            self.onlyImEndScene = scn
            self.endImage.setScene(scn)
            #self.endImage.scale(0.497,0.4966)
            self.endImage.fitInView(scn.sceneRect(),Qt.KeepAspectRatio)

            ptsFile = fileName+'.txt'
            self.onlyImEPtsFile = ptsFile

            try:
                self.endPts = np.loadtxt(ptsFile)
            except:
                #print('No file')
                self.triFlag = 1
                pass

            self.endFlag = 1
            self.enWidgets()
            self.showEndFlag = 1
            #if (self.triFlag == 0):
            self.showPoints(fileName)
            #else:
            #    self.newShow(fileName)


    def loadFinal(self,fileName):

        scn = QGraphicsScene()
        pixmap = QPixmap(fileName)
        scn.addPixmap(pixmap)

        self.blendImage.setScene(scn)
        self.blendImage.fitInView(scn.sceneRect(),Qt.KeepAspectRatio)


    def showPoints(self,fileName):
        #print('In show points')
        ptsFile = fileName+'.txt'
        self.saved = 0

        try:

            if (self.triFlag == 0):
                self.goodIm = 1
                #print('trying')
                #print('HEREEEEE')
                #print(fileName)
                #print(ptsFile)
                pts = np.loadtxt(ptsFile)

                # self.goodSscene = QGraphicsScene()
                # pixmap = QPixmap(fileName)
                # self.goodSscene.addPixmap(pixmap)
                #
                # self.goodEscene = QGraphicsScene()
                # pixmap = QPixmap(fileName)
                # self.goodEscene.addPixmap(pixmap)
                scene = QGraphicsScene()
                pixmap = QPixmap(fileName)
                scene.addPixmap(pixmap)


                for i in range(len(pts)):

                    #if(self.triFlag == 0):

                    newBrush = QBrush(Qt.SolidPattern)
                    newBrush.setColor(QColor(255,0,0))

                    newPen = QPen()
                    newPen.setColor(Qt.red)
                    scene.addEllipse(pts[i][0]-5,pts[i][1]-5,9,9,newPen,newBrush)

                if (self.showStartFlag == 1):
                    self.showStartFlag = 0
                    self.startImage.setScene(scene)
                    self.startImage.fitInView(scene.sceneRect(),Qt.KeepAspectRatio)

                    self.goodIm = 1
                    self.goodSscene = scene
                    self.goodSscene.mousePressEvent = self.getStartPos

                if (self.showEndFlag == 1):
                    self.showEndFlag = 0
                    self.endImage.setScene(scene)
                    self.endImage.fitInView(scene.sceneRect(),Qt.KeepAspectRatio)
                    self.goodIm = 1
                    self.goodEscene = scene
                    self.goodEscene.mousePressEvent = self.getEndPos


                #print('done HEREEE')



            elif (self.triFlag == 1):

                newBrush = QBrush(Qt.SolidPattern)
                newBrush.setColor(Qt.blue)

                newPen = QPen()
                newPen.setColor(Qt.blue)
                scene.addEllipse(pts[i][0]-5,pts[i][1]-5,9,9,newPen,newBrush)

                if (self.showStartFlag == 1):
                    #print('here')
                    self.showStartFlag = 1
                                     #self.showStartFlag = 0
                    self.startImage.setScene(scene)
                    self.startImage.fitInView(scene.sceneRect(),Qt.KeepAspectRatio)

                if (self.showEndFlag == 1):
                    #print('here2')
                    self.showEndFlag = 1
                     #self.showEndFlag = 0
                    self.endImage.setScene(scene)
                    self.endImage.fitInView(scene.sceneRect(),Qt.KeepAspectRatio)
                 #print('done HEREEE')


                if (self.triFlag == 1):
                    #print('doing this')
                    self.showStartFlag = 1
                    self.showEndFlag = 1

                    self.drawPoints()

        except:
            self.goodIm = 0
            #print('excepted')
            self.drawPoints()



    # def backToThis(self):
    #
    #     self.showStartFlag = 1          #Original flag for basic stuff,in showPoints and all
    #     self.showEndFlag = 1
    #
    #     self.Sx = None
    #     self.Sy = None
    #     self.Ex = None
    #     self.Ey = None
    #
    #     self.BSpresses = 0
    #
    #     self.BSstart = 1
    #     self.BSend = 1
    #
    #     self.startDone = 0      #to check if start image point choosing is done
    #     self.endDone = 0        #to check if end image point choosing is done
    #
    #     self.drawPoints()

    def drawPoints(self):
        #print('in draw points')
        #self.triFlag = 1
        #self.drewS = 1
        #self.mWflag = 0
        self.startDone = 0
        #print(self.showStartFlag)
        #print(self.showEndFlag)
        if (self.showStartFlag == 1):

            #print('start')
            self.showStartFlag = 0

            self.nowStart = 1
            self.startImage.setDisabled(False)
            self.onlyImStartScene.mousePressEvent = self.getStartPos
            if (self.goodIm == 1):
                self.goodSscene.mousePressEvent = self.getStartPos

        if (self.showEndFlag == 1):

            #print('end')

            self.showEndFlag = 0

            self.nowEnd = 1
            self.endImage.setDisabled(False)
            self.onlyImEndScene.mousePressEvent = self.getEndPos
            if (self.goodIm == 1):
                self.goodEscene.mousePressEvent = self.getEndPos
#TRY FOR TRIANGLE ERROR PART WITH A FLAG FOR CHECKING IF EVENT.POS OR EVENT.SCENEPOS

    def getStartPos(self, event):

        if (self.notDone != 1):

            self.startDone = 0
            #self.triFlag = 1
            #self.drewS = 1
            #print('I\'m in startpos bruh')
            coords = event.scenePos()
            #coords = event.pos()

            self.Sx = coords.x()
            self.Sy = coords.y()
            self.SnewCoords.append((self.Sx, self.Sy))
            self.StempCoords = [coords.x(),coords.y()]
            #print('Got coordinates: {} {}'.format(self.Sx,self.Sy))
            scene = QGraphicsScene()
            pixmap = QPixmap(self.startFile)
            scene.addPixmap(pixmap)

            newBrush = QBrush(Qt.SolidPattern)
            newBrush.setColor(Qt.green)

            newPen = QPen()
            newPen.setColor(Qt.green)

            self.showStartFlag = 1 #so that it keeps going back to the function and can go through to if block for start.

            #print(self.onlyImStartScene.items())
            self.onlyImStartScene.addEllipse(self.Sx-4,self.Sy-4,7,7,newPen,newBrush)
            #print(self.onlyImStartScene.items())

            #print('good im: {}'.format(self.goodIm))
            if (self.goodIm == 1):
                self.started = 1
                #self.onlyImStartScene = self.goodSscene
                #print('here trying to draw on the good image')
                #self.goodIm = 0
                self.goodSscene.addEllipse(self.Sx-4,self.Sy-4,7,7,newPen,newBrush)


            if (self.SthroughDel == 1):

                newBrush = QBrush(Qt.SolidPattern)
                newBrush.setColor(Qt.green)

                newPen = QPen()
                newPen.setColor(Qt.green)

                self.Sscene.addEllipse(self.Sx-4,self.Sy-4,7,7,newPen,newBrush)

                #self.SthroughDel = 0



            self.startImage.setDisabled(True)
            self.startDone = 1
            self.mouseFlag += 1
            #print('done with startpos')



    def getEndPos(self, event):

        if (self.startDone == 1):
            #self.triFlag = 1
            self.drewE = 1
            #print('I\'m in endpos bruh')
            coords = event.scenePos()

            #coords = event.pos()

            self.Ex = coords.x()
            self.Ey = coords.y()
            self.EnewCoords.append((self.Ex, self.Ey))
            self.EtempCoords = [coords.x(),coords.y()]
            #print('Got coordinates: {} {}'.format(self.Ex,self.Ey))

            scene = QGraphicsScene()
            pixmap = QPixmap(self.endFile)
            scene.addPixmap(pixmap)

            newBrush = QBrush(Qt.SolidPattern)
            newBrush.setColor(Qt.green)

            newPen = QPen()
            newPen.setColor(Qt.green)



            self.onlyImEndScene.addEllipse(self.Ex-4,self.Ey-4,7,7,newPen,newBrush)

            #print('good im: {}'.format(self.goodIm))
            if (self.goodIm == 1):
                #print('here trying to draw on the good image')
                #self.goodIm = 0
                self.goodEscene.addEllipse(self.Ex-4,self.Ey-4,7,7,newPen,newBrush)

            if (self.EthroughDel == 1):

                newBrush = QBrush(Qt.SolidPattern)
                newBrush.setColor(Qt.green)

                newPen = QPen()
                newPen.setColor(Qt.green)

                self.Escene.addEllipse(self.Ex-4,self.Ey-4,7,7,newPen,newBrush)

                #self.EthroughDel = 0


            self.endImage.setDisabled(True)
            self.endDone = 1
            self.mouseFlag += 1
            self.saved = 0
            self.doneChoosingPts()

    def keyPressEvent(self, event):

        #print('Detected a keypress')

        if (self.startDone == 1):
            if (self.endDone == 0):
                if (self.BSstart == 0):
                    #self.BSstart = 1
                    self.startDone = 0
                    self.startImage.setDisabled(False)
                    if (event.key() == Qt.Key_Backspace):
                        #print('Trying to delete element from start scene list')
                        #print(self.onlyImStartScene.items())
                        self.onlyImStartScene.removeItem(self.onlyImStartScene.items()[0])
                        #print(self.onlyImStartScene.items())
                    self.Sx = None
                    self.Sy = None

                    self.drawPoints()

        if(self.endDone == 1):
            if (self.BSend == 0):
                #self.BSend = 1
                self.endDone = 0
                #self.startDone = 1
                self.endImage.setDisabled(False)
                if (event.key() == Qt.Key_Backspace):
                    #print('Trying to delete element from end scene list')
                    #print(self.onlyImEndScene.items())
                    self.onlyImEndScene.removeItem(self.onlyImEndScene.items()[0])
                    #print(self.onlyImEndScene.items())

                self.Ex = None
                self.Ey = None
                self.showEndFlag = 1

                #self.drawPoints()
                self.onlyImEndScene.mousePressEvent = self.getEndPos


    def doneChoosingPts(self):
        self.clicked = 0
        self.notDone = 1
        #print('Waiting for main window click')
        #mW = QMainWindow()
        #mW.mousePressEvent = self.wantToSave
        #self.mWflag = 1
        self.startImage.setDisabled(False)
        #print("I'm in donechoosing")
        if (self.afterTri == 1):
            #print('Yea!')
            self.drawPoints()
        else:
            #print('Okay in done choosing waiting for a click!')
            if (self.saved == 0):
                #print('Here where you want me')
                self.onlyImStartScene.mousePressEvent = self.startClickedSave
                if (self.goodIm == 1):
                    #print('In here')
                    self.goodSscene.mousePressEvent = self.startClickedSave
                if (self.splCase == 1):
                        self.Sscene.mousePressEvent = self.startClickedSave
                if (self.clicked == 0):
                    self.mousePressEvent = self.wantToSave


    def startClickedSave(self,event):
        #print('HEREEE PROPERRLLYYY')
        self.clicked = 1

        #self.Sx = (event.scenePos()).x()
        #self.Sy = (event.scenePos()).y()

        #print("I'm in new start clicked save")
        #self.triFlag = 1
        #print('setting it to 2 in start clicked save')
        #self.drewS = 0
        self.drewE = 2
        pressPos = event.scenePos()

        #check for backspace happens automatically with keypressevent
        #if self.mouseFlag == 2:
            #self.mouseFlag = 0
        #print('Detected start image click')
        #print('Checking for widget..')
        self.setMouseTracking(False)
        #pressPos = event.pos()
        #print(pressPos)
        #print(self.endImage.geometry())
        # if ((self.endImage.geometry()).contains(pressPos)):
        #     print('No')
        #     pass
        #
        # else:
        #print('Yes')

        if (self.startDone == 1 and self.endDone == 1):

            #print('Done!!!')
        #check for startimage press
        #check for mainwindow press  #ASK WHICH FUNCTION OR SIGNAL TO USE
            #save to files, change dots to blue
            scene = QGraphicsScene()
            pixmap = QPixmap(self.startFile)
            scene.addPixmap(pixmap)

            aBrush = QBrush(Qt.SolidPattern)
            aBrush.setColor(Qt.blue)

            aPen = QPen()
            aPen.setColor(Qt.blue)

            self.onlyImStartScene.removeItem(self.onlyImStartScene.items()[0])
            self.onlyImStartScene.addEllipse(self.Sx-4,self.Sy-4,7,7,aPen,aBrush)
            self.onlyImEndScene.removeItem(self.onlyImEndScene.items()[0])
            self.onlyImEndScene.addEllipse(self.Ex-4,self.Ey-4,7,7,aPen,aBrush)

            if (self.SthroughDel == 1 and self.EthroughDel == 1):
                self.SthroughDel = 0
                self.EthroughDel = 0
                #self.Sscene.removeItem(self.onlyImStartScene.items()[0])
                self.Sscene.addEllipse(self.Sx-4,self.Sy-4,7,7,aPen,aBrush)
                #self.Escene.removeItem(self.onlyImEndScene.items()[0])
                self.Escene.addEllipse(self.Ex-4,self.Ey-4,7,7,aPen,aBrush)

            if (self.goodIm == 1):
                self.goodSscene.removeItem(self.goodSscene.items()[0])
                self.goodSscene.addEllipse(self.Sx-4,self.Sy-4,7,7,aPen,aBrush)
                self.goodEscene.removeItem(self.goodEscene.items()[0])
                self.goodEscene.addEllipse(self.Ex-4,self.Ey-4,7,7,aPen,aBrush)


            with open(self.onlyImSPtsFile,'a') as fptr:
                str1 = '\n'+'\t'+str(self.Sx)+'\t'+str(self.Sy)+'\n'
                fptr.write(str1)
            self.startPts = np.loadtxt(self.onlyImSPtsFile)
            with open(self.onlyImEPtsFile,'a') as fptr2:
                str2 = '\n'+'\t'+str(self.Ex)+'\t'+str(self.Ey)+'\n'
                fptr2.write(str2)
            self.endPts = np.loadtxt(self.onlyImEPtsFile)
            #mW = QMainWindow()
            #mW.blockSignals(True)
            #self.saved = 1
            self.startDone = 0
            self.endDone = 0
            self.startImage.setDisabled(False)
            self.endImage.setDisabled(False)
            #print('setting it to 1 in start clicked save')
            #self.drewS = 1
            self.saved = 1


            #if ((self.startImage.geometry()).contains(pressPos)):
            # if ((self.startImage.geometry()).contains(pressPos)):
            #    self.startClickedStartPos(event)

            # else:
            #     self.Sx = None
            #     self.Sy = None
            #     self.Ex = None
            #     self.Ey = None

            self.notDone = 0

            self.getStartPos(event)
            if (self.checkBox.isChecked() == True):
                #print('HERE COME ON THEN WHY NOT WORKING')
                self.splCase = 1
                self.loadDelTri()

        else:

            pass



    def wantToSave(self,event):
        #print("I'm in want to save")
        #self.triFlag = 1
        #print('setting it to 2 in wanttosave')
        #self.drewS = 0
        self.drewE = 2
        pressPos = event.pos()

        self.StempCoords = []
        self.EtempCoords = []

        #check for backspace happens automatically with keypressevent
        #if self.mouseFlag == 2:
            #self.mouseFlag = 0
        #print('Detected main window click')
        #print('Checking for widget..')
        self.setMouseTracking(False)
        pressPos = event.pos()
        #print(pressPos)
        #print(self.endImage.geometry())
        if ((self.endImage.geometry()).contains(pressPos)):
            #print('No')
            self.doneChoosingPts()
            #pass

        else:
            #print('Yes')

            if (self.startDone == 1 and self.endDone == 1):

                #print('Done!!!')
            #check for startimage press
            #check for mainwindow press  #ASK WHICH FUNCTION OR SIGNAL TO USE
                #save to files, change dots to blue
                scene = QGraphicsScene()
                pixmap = QPixmap(self.startFile)
                scene.addPixmap(pixmap)

                aBrush = QBrush(Qt.SolidPattern)
                aBrush.setColor(Qt.blue)

                aPen = QPen()
                aPen.setColor(Qt.blue)

                self.onlyImStartScene.removeItem(self.onlyImStartScene.items()[0])
                self.onlyImStartScene.addEllipse(self.Sx-4,self.Sy-4,7,7,aPen,aBrush)
                self.onlyImEndScene.removeItem(self.onlyImEndScene.items()[0])
                self.onlyImEndScene.addEllipse(self.Ex-4,self.Ey-4,7,7,aPen,aBrush)

                if (self.SthroughDel == 1 and self.EthroughDel == 1):
                    self.SthroughDel = 0
                    self.EthroughDel = 0
                    #self.Sscene.removeItem(self.onlyImStartScene.items()[0])
                    self.Sscene.addEllipse(self.Sx-4,self.Sy-4,7,7,aPen,aBrush)
                    #self.Escene.removeItem(self.onlyImEndScene.items()[0])
                    self.Escene.addEllipse(self.Ex-4,self.Ey-4,7,7,aPen,aBrush)

                if (self.goodIm == 1):
                    self.goodSscene.removeItem(self.goodSscene.items()[0])
                    self.goodSscene.addEllipse(self.Sx-4,self.Sy-4,7,7,aPen,aBrush)
                    self.goodEscene.removeItem(self.goodEscene.items()[0])
                    self.goodEscene.addEllipse(self.Ex-4,self.Ey-4,7,7,aPen,aBrush)


                with open(self.onlyImSPtsFile,'a') as fptr:
                    str1 = '\n'+'\t'+str(self.Sx)+'\t'+str(self.Sy)+'\n'
                    fptr.write(str1)
                self.startPts = np.loadtxt(self.onlyImSPtsFile)
                with open(self.onlyImEPtsFile,'a') as fptr2:
                    str2 = '\n'+'\t'+str(self.Ex)+'\t'+str(self.Ey)+'\n'
                    fptr2.write(str2)
                self.endPts = np.loadtxt(self.onlyImEPtsFile)
                #mW = QMainWindow()
                #mW.blockSignals(True)
                #self.saved = 1
                self.startDone = 0
                self.endDone = 0
                self.startImage.setDisabled(False)
                self.endImage.setDisabled(False)
                #print('setting it to 1 in wanttosave')
                #self.drewS = 1
                self.saved = 1


                #if ((self.startImage.geometry()).contains(pressPos)):
                # if ((self.startImage.geometry()).contains(pressPos)):
                #    self.startClickedStartPos(event)

                if (self.checkBox.isChecked() == True):
                    self.loadDelTri()
                #else:
                self.Sx = None
                self.Sy = None
                self.Ex = None
                self.Ey = None
                self.notDone = 0
                #self.doneChoosingPts()
                self.drawPoints()


            else:

                pass
            #self.drewS = 1
            #self.mouseFlag = 0
        #else:
            #event.ignore()


    def loadDelTri(self):


        if (self.checkBox.isChecked() == True):
            self.splCase = 1
            self.showStartFlag = 1
            self.showEndFlag = 1
            #print('checked')
            SptsArr = np.loadtxt(self.onlyImSPtsFile,'float64')
            EptsArr = np.loadtxt(self.onlyImEPtsFile,'float64')

            try:


                if (self.started == 1):
                    #print('Okay here')
                    delTri = Delaunay(SptsArr)

                    Sscene = QGraphicsScene()
                    SpixMap = QPixmap(self.startFile)
                    Sscene.addPixmap(SpixMap)


                    Escene = QGraphicsScene()
                    EpixMap = QPixmap(self.endFile)
                    Escene.addPixmap(EpixMap)

                    pen = QPen()
                    pen.setColor(QColor(0,120,190))
                    #pen.setWidth(0)

                    brush = QBrush()
                    brush.setColor(QColor(0,120,190))

                    for tri in delTri.simplices:


                        STriangle = QPolygonF()
                        STriangle.append(QPointF(SptsArr[tri[0]][0],SptsArr[tri[0]][1]))
                        STriangle.append(QPointF(SptsArr[tri[1]][0],SptsArr[tri[1]][1]))
                        STriangle.append(QPointF(SptsArr[tri[2]][0],SptsArr[tri[2]][1]))

                        self.goodSscene.addPolygon(STriangle,pen,brush)

                        ETriangle = QPolygonF()
                        #print(self.endPts)
                        ETriangle.append(QPointF(EptsArr[tri[0]][0],EptsArr[tri[0]][1]))
                        ETriangle.append(QPointF(EptsArr[tri[1]][0],EptsArr[tri[1]][1]))
                        ETriangle.append(QPointF(EptsArr[tri[2]][0],EptsArr[tri[2]][1]))

                        self.goodEscene.addPolygon(ETriangle,pen,brush)

                    redBrush = QBrush(Qt.SolidPattern)
                    redBrush.setColor(Qt.red)
                    redPen = QPen()
                    redPen.setColor(Qt.red)

                    blueBrush = QBrush(Qt.SolidPattern)
                    blueBrush.setColor(Qt.blue)
                    bluePen = QPen()
                    bluePen.setColor(Qt.blue)

                    greenBrush = QBrush(Qt.SolidPattern)
                    greenBrush.setColor(Qt.green)
                    greenPen = QPen()
                    greenPen.setColor(Qt.green)

                    for i in range(len(SptsArr)):
                        self.goodSscene.addEllipse(SptsArr[i][0]-5,SptsArr[i][1]-5,9,9,redPen,redBrush)
                        #Sscene.addEllipse(SptsArr[i][0]-5,SptsArr[i][1]-5,9,9,redPen,redBrush)

                    for i in range(len(EptsArr)):
                        self.goodEscene.addEllipse(EptsArr[i][0]-5,EptsArr[i][1]-5,9,9,redPen,redBrush)
                        #Escene.addEllipse(EptsArr[i][0]-5,EptsArr[i][1]-5,9,9,redPen,redBrush)

                    if (self.SnewCoords != []):
                        for i in self.SnewCoords:
                            self.goodSscene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)
                            #Sscene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)

                    if (self.EnewCoords != []):
                        for i in self.EnewCoords:
                            self.goodEscene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)
                            #Escene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)

                    if (self.StempCoords != []):
                        self.goodSscene.addEllipse(self.StempCoords[0]-5,self.StempCoords[1]-5,9,9,greenPen,greenBrush)
                        #Sscene.addEllipse(self.StempCoords[0]-5,self.StempCoords[1]-5,9,9,greenPen,greenBrush)

                    if (self.EtempCoords != []):
                        self.goodEscene.addEllipse(self.EtempCoords[0]-5,self.EtempCoords[1]-5,9,9,greenPen,greenBrush)
                        #Escene.addEllipse(self.EtempCoords[0]-5,self.EtempCoords[1]-5,9,9,greenPen,greenBrush)


                else:

                    delTri = Delaunay(SptsArr)

                    Sscene = QGraphicsScene()
                    SpixMap = QPixmap(self.startFile)
                    Sscene.addPixmap(SpixMap)


                    Escene = QGraphicsScene()
                    EpixMap = QPixmap(self.endFile)
                    Escene.addPixmap(EpixMap)

                    for tri in delTri.simplices:
                        if (self.triFlag == 0):

                            #print('Okay..')
                            pen = QPen()
                            pen.setColor(Qt.red)
                            #pen.setWidth(0)

                            brush = QBrush()
                            brush.setColor(Qt.red)

                        elif (self.triFlag == 1):
                            #self.triFlag = 0
                            pen = QPen()
                            pen.setColor(Qt.blue)
                            #pen.setWidth(0)

                            brush = QBrush()
                            brush.setColor(Qt.blue)



                        newBrush = QBrush(Qt.SolidPattern)
                        newBrush.setColor(Qt.green)

                        newPen = QPen()
                        newPen.setColor(Qt.green)

                        if (self.Sx != None and self.Sy != None):
                            #if (self.saved == 0):
                            Sscene.addEllipse(self.Sx-4,self.Sy-4,7,7,newPen,newBrush)

                        if (self.Ex != None and self.Ey != None):
                            #if (self.saved == 0):
                            Escene.addEllipse(self.Ex-4,self.Ey-4,7,7,newPen,newBrush)


                        STriangle = QPolygonF()
                        STriangle.append(QPointF(SptsArr[tri[0]][0],SptsArr[tri[0]][1]))
                        STriangle.append(QPointF(SptsArr[tri[1]][0],SptsArr[tri[1]][1]))
                        STriangle.append(QPointF(SptsArr[tri[2]][0],SptsArr[tri[2]][1]))

                        Sscene.addPolygon(STriangle,pen,brush)

                        ETriangle = QPolygonF()
                        #print(self.endPts)
                        ETriangle.append(QPointF(EptsArr[tri[0]][0],EptsArr[tri[0]][1]))
                        ETriangle.append(QPointF(EptsArr[tri[1]][0],EptsArr[tri[1]][1]))
                        ETriangle.append(QPointF(EptsArr[tri[2]][0],EptsArr[tri[2]][1]))

                        Escene.addPolygon(ETriangle,pen,brush)

                    for i in range(len(SptsArr)):
                        if (self.triFlag == 0):
                            #print('Okay..')
                            newPen = QPen()
                            newPen.setColor(Qt.red)
                            #pen.setWidth(0)

                            newBrush = QBrush(Qt.SolidPattern)
                            newBrush.setColor(Qt.red)

                        elif (self.triFlag == 1):

                            newPen = QPen()
                            newPen.setColor(Qt.blue)
                            #pen.setWidth(0)

                            newBrush = QBrush(Qt.SolidPattern)
                            newBrush.setColor(Qt.blue)


                        #newBrush = QBrush(Qt.SolidPattern)
                        #newBrush.setColor(Qt.blue)

                        #newPen = QPen()
                        #newPen.setColor(Qt.blue)

                        Sscene.addEllipse(SptsArr[i][0]-5,SptsArr[i][1]-5,9,9,newPen,newBrush)

                    for i in range(len(EptsArr)):
                        if (self.triFlag == 0):
                            self.triFlag = 0
                            newPen = QPen()
                            newPen.setColor(Qt.red)
                            #pen.setWidth(0)

                            newBrush = QBrush(Qt.SolidPattern)
                            newBrush.setColor(Qt.red)

                        elif (self.triFlag == 1):

                            newPen = QPen()
                            newPen.setColor(Qt.blue)
                            #pen.setWidth(0)

                            newBrush = QBrush(Qt.SolidPattern)
                            newBrush.setColor(Qt.blue)



                        # newBrush = QBrush(Qt.SolidPattern)
                        # newBrush.setColor(Qt.blue)
                        #
                        # newPen = QPen()
                        # newPen.setColor(Qt.blue)

                        Escene.addEllipse(EptsArr[i][0]-5,EptsArr[i][1]-5,9,9,newPen,newBrush)

                    self.Sscene = Sscene
                    self.Escene = Escene

                    self.showStartFlag = 0
                    self.startImage.setScene(Sscene)
                    self.startImage.fitInView(Sscene.sceneRect(),Qt.KeepAspectRatio)

                    self.showEndFlag = 0
                    self.endImage.setScene(Escene)
                    self.endImage.fitInView(Escene.sceneRect(),Qt.KeepAspectRatio)

                    self.Sscene = Sscene
                    self.Escene = Escene

                    if(self.triFlag == 1):
                        #print('Now doing to draw from delTri')
                        self.SthroughDel = 1
                        self.EthroughDel = 1
                        self.Sscene = Sscene
                        self.Escene = Escene
                        Sscene.mousePressEvent = self.getStartPos
                        Escene.mousePressEvent = self.getEndPos


                # if (self.splCase == 1):
                #     self.splCase = 0
                #     newBrush = QBrush(Qt.SolidPattern)
                #     newBrush.setColor(Qt.green)
                #
                #     newPen = QPen()
                #     newPen.setColor(Qt.green)
                #
                #     Sscene.addEllipse(self.Sx-4,self.Sy-4,7,7,newPen,newBrush)

            except:
                pass

        elif (self.checkBox.isChecked() == False):
            #print('not clicked')
            self.splCase = 0
            self.showStartFlag = 1
            self.showEndFlag = 1
            #print("trif:{}".format(self.triFlag))
            SptsArr = np.loadtxt(self.onlyImSPtsFile,'float64')
            EptsArr = np.loadtxt(self.onlyImEPtsFile,'float64')

            if (self.triFlag == 1):
                #print('NOT HERE NOOO')
                self.startImage.setScene(self.onlyImStartScene)
                self.startImage.fitInView(self.onlyImStartScene.sceneRect(),Qt.KeepAspectRatio)
                self.endImage.setScene(self.onlyImEndScene)
                self.endImage.fitInView(self.onlyImEndScene.sceneRect(),Qt.KeepAspectRatio)

                self.drawPoints()
            else:
                #print('Here in else part')

                if (self.started == 0):
                    self.loadStartFunc(self.startFile)
                    self.loadEndFunc(self.endFile)

                else:
                    #print('Here')


                    for i in range(len(self.goodSscene.items()) - 2):
                        self.goodSscene.removeItem(self.goodSscene.items()[0])

                    for i in range(len(self.goodEscene.items()) - 2):
                        self.goodEscene.removeItem(self.goodEscene.items()[0])

                    redBrush = QBrush(Qt.SolidPattern)
                    redBrush.setColor(Qt.red)
                    redPen = QPen()
                    redPen.setColor(Qt.red)

                    blueBrush = QBrush(Qt.SolidPattern)
                    blueBrush.setColor(Qt.blue)
                    bluePen = QPen()
                    bluePen.setColor(Qt.blue)

                    greenBrush = QBrush(Qt.SolidPattern)
                    greenBrush.setColor(Qt.green)
                    greenPen = QPen()
                    greenPen.setColor(Qt.green)

                    for i in range(len(SptsArr)):
                        self.goodSscene.addEllipse(SptsArr[i][0]-5,SptsArr[i][1]-5,9,9,redPen,redBrush)
                        #Sscene.addEllipse(SptsArr[i][0]-5,SptsArr[i][1]-5,9,9,redPen,redBrush)

                    for i in range(len(EptsArr)):
                        self.goodEscene.addEllipse(EptsArr[i][0]-5,EptsArr[i][1]-5,9,9,redPen,redBrush)
                        #Escene.addEllipse(EptsArr[i][0]-5,EptsArr[i][1]-5,9,9,redPen,redBrush)

                    if (self.SnewCoords != []):
                        for i in self.SnewCoords:
                            self.goodSscene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)
                            #Sscene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)

                    if (self.EnewCoords != []):
                        for i in self.EnewCoords:
                            self.goodEscene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)
                            #Escene.addEllipse(i[0]-5,i[1]-5,9,9,bluePen,blueBrush)

                    if (self.StempCoords != []):
                        self.goodSscene.addEllipse(self.StempCoords[0]-5,self.StempCoords[1]-5,9,9,greenPen,greenBrush)
                        #Sscene.addEllipse(self.StempCoords[0]-5,self.StempCoords[1]-5,9,9,greenPen,greenBrush)

                    if (self.EtempCoords != []):
                        self.goodEscene.addEllipse(self.EtempCoords[0]-5,self.EtempCoords[1]-5,9,9,greenPen,greenBrush)
                        #Escene.addEllipse(self.EtempCoords[0]-5,self.EtempCoords[1]-5,9,9,greenPen,greenBrush)

                # self.loadStartFunc(self.startFile)
                # self.loadEndFunc(self.endFile)
            #self.triFlag = 0

    def showAlpha(self):

        val = self.horizontalSlider.value()
        newVal = val
        newVal/=100
        self.alpha = newVal
        if (val % 5 == 0):
            self.alphaTextBox.setText(str(newVal))



    def blendFunc(self):

        sArr = loadColorImg(self.startFile)
        eArr = loadColorImg(self.endFile)

        #stPts = points(self.startPts)
        #enPts = points(self.endPts)
        if (self.alpha == None):
            self.alpha = 0

        if len(sArr.shape) == 2:
            newBlend = Blender(sArr,self.startPts,eArr,self.endPts)
            finalArr = newBlend.getBlendedImage(self.alpha)
            saveImg('newGray.jpg',finalArr)
            self.loadFinal('newGray.jpg')
        elif len(sArr.shape) == 3:
            newBlend = ColorBlender(sArr,self.startPts,eArr,self.endPts)
            finalArr = newBlend.getBlendedImage(self.alpha)
            saveRGBImg('newColor.jpg',finalArr)
            self.loadFinal('newColor.jpg')


if __name__ == "__main__":
    currentApp = QApplication(sys.argv)
    currentForm = MorphingApp()

    currentForm.show()
    currentApp.exec_()
