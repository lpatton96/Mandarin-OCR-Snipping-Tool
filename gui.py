import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PIL import ImageGrab
from paddleocr import PaddleOCR
import numpy as np
import asyncio
from googletrans import Translator

class TranslationWorker(QThread):
    translation_finished = pyqtSignal(str)

    def __init__(self, text_to_translate,dest_language):
        super().__init__()
        self.text_to_translate = text_to_translate
        self.dest_language = dest_language

    def run(self):
        asyncio.run(self.translate())

    async def translate(self):
        try:
            async with Translator() as translator:
                result = await translator.translate(self.text_to_translate, dest=self.dest_language)
                print(f"recieved={self.text_to_translate}")
                # result = await translator.translate(self.text_to_translate)
                self.translation_finished.emit(result.text)
                print(f"translation done={result}")
        except Exception as e:
            self.translation_finished.emit(f"Translation failed: {str(e)}")


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()


        # create PaddleOCR instance
        # Paddleocr supports Chinese, English, French, German, Korean and Japanese.
        # You can set the parameter `lang` as `ch`, `en`, `french`, `german`, `korean`, `japan`
        # to switch the language model in order.
        self.ocr = PaddleOCR(use_angle_cls=True, lang='ch') # need to run only once to download and load model into memory

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
        
        # Create label for image
        self.imageLabel = QtWidgets.QLabel(self)

        # Create box for text
        self.textBox = QtWidgets.QTextEdit(self)
        
        # create and add copy button
        self.copyTextButton = QtWidgets.QPushButton("Copy Text")
        self.copyTextButton.clicked.connect(self.copyToClipboard)

        # create and add getText button
        self.getTextButton = QtWidgets.QPushButton("Get text")
        self.getTextButton.clicked.connect(self.getText)

        # create and add removeSpace button
        self.removeSpacesButton = QtWidgets.QPushButton("Remove Spaces")
        self.removeSpacesButton.clicked.connect(self.removeSpaces)
        
        # create and add translate button
        self.getTranslationButton = QtWidgets.QPushButton("Translate")
        self.getTranslationButton.clicked.connect(self.getTranslation)

        # Create box for translated text
        self.translatedTextBox = QtWidgets.QTextEdit(self)

        # add widgets
        self.mainLayout.addWidget(self.screenshotButton)
        self.mainLayout.addWidget(self.imageLabel)
        self.mainLayout.addWidget(self.getTextButton)
        self.mainLayout.addWidget(self.textBox)
        self.mainLayout.addWidget(self.copyTextButton)
        self.mainLayout.addWidget(self.removeSpacesButton)
        self.mainLayout.addWidget(self.getTranslationButton)
        self.mainLayout.addWidget(self.translatedTextBox)

        # No image, no show
        self.imageLabel.hide()

        # show blank textbox
        self.textBox.show()
        self.copyTextButton.show()
        self.removeSpacesButton.show()
        self.getTranslationButton.show()

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
        self.getTextButton.hide()
        self.textBox.hide()
        self.copyTextButton.hide()
        self.removeSpacesButton.hide()
        self.getTranslationButton.hide()
        self.translatedTextBox.hide()

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
            self.img = ImageGrab.grab(bbox=(x1, y1, x2, y2))
            self.img.save('capture.png')

            # create image pixmap
            self.imagePixmap = QtGui.QPixmap('capture.png')

            # add image to label
            self.imageLabel.setPixmap(self.imagePixmap)

            # Restore elements
            self.screenshotButton.show()
            self.imageLabel.show()
            self.getTextButton.show()
            self.textBox.show()
            self.copyTextButton.show()
            self.removeSpacesButton.show()
            self.getTranslationButton.show()
            self.translatedTextBox.show()

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

    # Recursive function to flatten list  
    def flatten(self,nested_list):  
        res = []  
        for x in nested_list:  
            if isinstance(x, list):  
                res.extend(self.flatten(x))  # Recursively flatten nested lists  
            else:  
                res.append(x)  # Append individual elements  
        return res 

    def getText(self):
        data = np.asarray(self.img)
        result = self.ocr.ocr(data)
        arr = self.flatten(result)
        textArr = []

        for item in arr:
            if isinstance(item,tuple):
                textArr.append(item[0])

        self.textBox.setText(' '.join(textArr))
        # print(' '.join(textArr))
        return ' '.join(textArr)
    
    def copyToClipboard(self):
        clipboard = QtWidgets.QApplication.clipboard() 
        clipboard.setText(self.textBox.toPlainText())

    def removeSpaces(self):
        text = self.textBox.toPlainText()
        text = text.replace(" ","")
        self.textBox.setPlainText(text)

    def getTranslation(self):
        print("translation requested")
        destinationLanguage = "en"
        self.worker = TranslationWorker(self.textBox.toPlainText(),destinationLanguage)
        # self.worker = TranslationWorker(self.textBox.toPlainText())
        self.worker.translation_finished.connect(self.updateOutput)
        self.worker.start()
    
    def updateOutput(self,translatedText):
        print(f"output={translatedText}")
        self.translatedTextBox.setPlainText(translatedText)
        
if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyWidget()
    app.aboutToQuit.connect(app.deleteLater)
    sys.exit(app.exec_())
