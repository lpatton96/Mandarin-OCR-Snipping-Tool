import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import tkinter as tk
from PIL import ImageGrab
import numpy as np
import cv2


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        root = tk.Tk()

        # set winsow size
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        self.setGeometry(0, 0, screen_width, screen_height)
        # default window settings
        QtCore.Qt.WindowFlags()
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setWindowTitle(' ')

        # initialize the drawing points
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        # screenshot flag
        self.isDrawing = False

        # create base layout
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # create and add screenshot button
        self.screenshotButton = QtWidgets.QPushButton("Take Screenshot")
        self.screenshotButton.clicked.connect(self.takeScreenshot)
        self.mainLayout.addWidget(self.screenshotButton)

        # create label for image
        self.imageLabel = QtWidgets.QLabel(self)
        self.mainLayout.addWidget(self.imageLabel)
        # no image no show
        self.imageLabel.hide()
        
        # update the layout
        self.setLayout(self.mainLayout)

        # show updated window with new layout
        self.show()

    def takeScreenshot(self):
        # screenshot action has begun
        self.isDrawing = True

        # hide elements for clean screenshot
        self.screenshotButton.hide()
        self.imageLabel.hide()

        # reduce opacity to see screenshot region
        self.setWindowOpacity(0.4)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor)
        )
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.update()
        print('Capture the screen...')

        # show screenshot overlay
        self.show()

    def paintEvent(self, event):
        if self.isDrawing is True:
            qp = QtGui.QPainter(self)
            qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
            qp.setBrush(QtGui.QColor(128, 128, 255, 128))
            qp.drawRect(QtCore.QRect(self.begin, self.end))
        else:
            super().paintEvent(event) #important, call super class paint event to keep the widget functional.
   
    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.isDrawing is True:
            # borderless window for perfect screenshot
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
            self.update()
            # hide entire overlay for screenshot
            self.hide()
            x1 = min(self.begin.x(), self.end.x())
            y1 = min(self.begin.y(), self.end.y())
            x2 = max(self.begin.x(), self.end.x())
            y2 = max(self.begin.y(), self.end.y())

            # take screenshot 
            img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            img.save('capture.png')
            
            # create image pixmap
            self.imagePixmap = QtGui.QPixmap('capture.png')

            # add image to label
            self.imageLabel.setPixmap(self.imagePixmap)

            # img = cv2.cvtColor(np.array(img), cv2.COLOR_BGR2RGB)
            # cv2.imshow('Captured Image', img)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            
            # restore elements 
            self.screenshotButton.show()
            self.imageLabel.show()
            
            QtWidgets.QApplication.restoreOverrideCursor()
            self.setWindowOpacity(1.0) #reset opacity.
            # self.setWindowFlags(QtCore.Qt.WindowFlags()) #reset window flags.

            # screenshot action over, set drawing flag
            self.isDrawing = False
            self.update()
            self.show()
        else:
            pass
        # reset drawing points  
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()
        # reset window settings
        QtCore.Qt.WindowFlags()
        self.update()
            

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    # window.show()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())