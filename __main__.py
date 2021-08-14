# Python based Gemini File Reader
#
#
#

import sys,os

# Setup globals
import __global__
__global__.HOME_DIR = os.path.abspath(os.path.split(__file__)[0])
__global__.MEDIA_DIR = os.path.join(__global__.HOME_DIR,"qtapp","media")


# import PyQt5.QtCore as QtCore
# import PyQt5.QtGui as QtGui
import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtCore as QtCore
import qtapp
if __name__ == "__main__":
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_Use96Dpi)
    qapp = QtWidgets.QApplication(sys.argv)
    with open(os.path.join("qtapp","css","dark.qss"),'r') as file:
        styletxt = file.read()
    qapp.setStyleSheet(styletxt)
    win = qtapp.mainWindow(qapp)
    win.show()
    qapp.exec()