import __global__,os

import PyQt5.QtWidgets as QtWidgets
import PyQt5.QtGui as QtGui

CONTROL_STYLE_SHEET = """
QPushButton
{
    font-size: 32px;
    border-width: 1px;
    border-color: #4d4d4d;
    border-style: solid;
    border-radius: 0;
    padding: 0px;
    font-size: 32px;
    padding-left: 0px;
    padding-right: 0px;
    min-width: 40px;
    background-color: #4d4d4d;
}

QPushButton:hover
{
    border: 2px solid QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
}

QPushButton:pressed
{
    background-color: QLinearGradient( x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #ffa02f, stop: 1 #d7801a);
}
"""

class C_QExitBtn(QtWidgets.QPushButton):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet(CONTROL_STYLE_SHEET)
        self.__icon = QtGui.QIcon(
            os.path.join(__global__.MEDIA_DIR,"cancel.svg")
        )
        self.setIcon(self.__icon)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Expanding)
    
    def resizeEvent(self,event):
        if self.width() != self.height():
            self.resize(self.height(),self.height())


class C_QMaxMinBtn(QtWidgets.QPushButton):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet(CONTROL_STYLE_SHEET)
        self.__icon = QtGui.QIcon(
            os.path.join(__global__.MEDIA_DIR,"max-window.svg")
        )
        self.setIcon(self.__icon)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Expanding)
    
    def resizeEvent(self,event):
        if self.width() != self.height():
            self.resize(self.height(),self.height())

            
class C_QMinimizeBtn(QtWidgets.QPushButton):
    def __init__(self,parent):
        super().__init__(parent)
        self.setStyleSheet(CONTROL_STYLE_SHEET)
        self.__icon = QtGui.QIcon(
            os.path.join(__global__.MEDIA_DIR,"min-window.svg")
        )
        self.setIcon(self.__icon)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred,QtWidgets.QSizePolicy.Expanding)
    
    def resizeEvent(self,event):
        if self.width() != self.height():
            self.resize(self.height(),self.height())

