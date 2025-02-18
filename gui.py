import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PIL import ImageGrab

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Set window size to cover entire screen
        # screen = QtWidgets.QApplication.primaryScreen()
        # screen_geometry = screen.geometry()
        # # This will ensure the window covers the whole screen including the title bar area
        # self.setGeometry(screen_geometry)  

        # Set window size
        screen = QtWidgets.QApplication.primaryScreen()
        screen_width = screen.size().width()
        screen_height = screen.size().height()
        self.setGeometry(0, 0, screen_width, screen_height)

        # Default window settings
        self.setWindowFlags(QtCore.Qt.Widget)
        self.setWindowTitle(' ')

        # Initialize drawing points
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()

        # Screenshot flag
        self.isDrawing = False

        # Create base layout
        self.mainLayout = QtWidgets.QVBoxLayout(self)

        # Create and add screenshot button
        self.screenshotButton = QtWidgets.QPushButton("Take Screenshot")
        self.screenshotButton.clicked.connect(self.takeScreenshot)
        self.mainLayout.addWidget(self.screenshotButton)

        # Create label for image
        self.imageLabel = QtWidgets.QLabel(self)
        self.mainLayout.addWidget(self.imageLabel)

        # No image, no show
        self.imageLabel.hide()

        # Update the layout
        self.setLayout(self.mainLayout)

        # Show updated window with new layout
        self.show()

    def takeScreenshot(self):
        # Screenshot action has begun
        self.isDrawing = True

        # Hide elements for clean screenshot
        self.screenshotButton.hide()
        self.imageLabel.hide()

        # Borderless for perfect screenshot
        self.showFullScreen()
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # self.show()
        # Borderless for perfect screenshot
        # self.setWindowFlags(QtCore.Qt.FramelessWindowHint)

        # Reduce opacity to see screenshot region
        self.setWindowOpacity(0.4)
        QtWidgets.QApplication.setOverrideCursor(
            QtGui.QCursor(QtCore.Qt.CrossCursor)
        )

        # Show screenshot overlay
        self.show()

    def paintEvent(self, event):
        if self.isDrawing:
            qp = QtGui.QPainter(self)
            qp.setPen(QtGui.QPen(QtGui.QColor('black'), 3))
            qp.setBrush(QtGui.QColor(128, 128, 255, 128))
            qp.drawRect(QtCore.QRect(self.begin, self.end))
        else:
            super().paintEvent(event)  # Important: call super class paint event to keep the widget functional.

    def mousePressEvent(self, event):
        self.begin = event.pos()
        self.end = self.begin
        self.update()

    def mouseMoveEvent(self, event):
        self.end = event.pos()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.isDrawing:
            # Hide entire overlay for screenshot
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

            # Restore elements
            self.screenshotButton.show()
            self.imageLabel.show()

            QtWidgets.QApplication.restoreOverrideCursor()
            self.setWindowOpacity(1.0)  # Reset opacity
            self.showMaximized()
            # self.setWindowFlags(QtCore.Qt.Widget)  # Reset window flags

            # Screenshot action over, set drawing flag
            self.isDrawing = False
            # self.show()

        # Reset drawing points  
        self.begin = QtCore.QPoint()
        self.end = QtCore.QPoint()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
