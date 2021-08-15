# Left side navigator 
import __global__,os

from qtapp import subwindows

import PyQt5.QtCore    as QtCore
import PyQt5.QtGui     as QtGui
import PyQt5.QtWidgets as QtWidgets


NAVIGATION_STYLE_SHEET="""
QPushButton
{
    font-size: 32px;
    border: none;
    padding: 0px;
    font-size: 32px;
    padding-left: 0px;
    padding-right: 0px;
    background-color: #2f2f2f;
}
QPushButton:hover
{
    background-color: #5f5f5f;
}
QLabel
{
    background-color: transparent;
}
"""

NAVIGATION_STYLE_SHEET_ACTIVATED="""
QPushButton
{
    font-size: 32px;
    border: none;
    padding: 0px;
    font-size: 32px;
    padding-left: 0px;
    padding-right: 0px;
    background-color: #5f5f5f;
}
QPushButton:hover
{
    background-color: #5f5f5f;
}
QLabel
{
    background-color: transparent;
}
"""

class _C_QNavButton(QtWidgets.QPushButton):
    # clicked = QtCore.pyqtSignal()
    def __init__(self,parent,name:str,icon:str=None,*args,**kwargs):
        super().__init__(parent)
        self.setStyleSheet(NAVIGATION_STYLE_SHEET)
        self.__name = name
        self.setToolTip(name)
        # self.__img  = img
        
        self.setMinimumHeight(50)
        # Visual Classes
        self.__brush = QtGui.QBrush(QtGui.QColor(0x2f2f2f))
        self.__highlightbrush = QtGui.QBrush(QtGui.QColor(0x5f5f5f))
        self.__outlinePen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(0x2f2f2f)),5)
        self.__highlightPen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(0x5f5f5f)),5)
        
        # Internal State Machine
        self.__highlight = False

        self.__layout = QtWidgets.QHBoxLayout(self)
        if icon is None: self.__icon   = QtGui.QIcon( os.path.join(__global__.MEDIA_DIR,"broken.svg") )
        else           : self.__icon   = QtGui.QIcon( os.path.join(__global__.MEDIA_DIR,icon) )
        self.__iconlbl   = QtWidgets.QLabel(self)
        self.__iconlbl.setPixmap(self.__icon.pixmap(self.__iconlbl.size()))
        self.__layout.addWidget(self.__iconlbl)
        self.__layout.setContentsMargins(4,4,4,4)

    def activate(self):
        self.setStyleSheet(NAVIGATION_STYLE_SHEET_ACTIVATED)

    def deactivate(self):
        self.setStyleSheet(NAVIGATION_STYLE_SHEET)

    def resizeEvent(self,event):
        self.__iconlbl.setPixmap(self.__icon.pixmap(self.__iconlbl.size()))

    def enterEvent(self,event):
        self.__highlight = True

    def leaveEvent(self,event):
        self.__highlight = False

    def mousePressEvent(self,event):
        self.clicked.emit()

    # def paintEvent(self,event):
        # painter = QtGui.QPainter(self)
        # width = self.width()
        # height = self.height()
        # if self.__highlight: painter.fillRect(0,0,width,height,self.__highlightbrush)
        # else               : painter.fillRect(0,0,width,height,self.__brush)
        

    # Internal Functions
    def __buildButton(self):
        pass

class C_QNavigator(QtWidgets.QWidget):
    onPress = QtCore.pyqtSignal(str)
    onHover = QtCore.pyqtSignal(str)
    
    def __init__(self,parent,*args,**kwargs):
        super().__init__(parent)
        self.__buttonList = {}
        self.__widgetList = {}

        self.__layout = QtWidgets.QGridLayout(self) 
        self.__layout.setSpacing(0)
        self.__layout.setContentsMargins(0,0,0,0)
        self.__layout.addItem(QtWidgets.QSpacerItem(0, 99, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding),99,0,1,1)

        # Visual Classes
        self.__brush = QtGui.QBrush(QtGui.QColor(0x1f1f1f))
        self.__outlinePen = QtGui.QPen(self.__brush,5)

        # State Machine information
        self.__repaint = False
        self.__lastActive = None
        # Set Style
        self.setStyleSheet("background-color:#1f1f1f;")

    def resizeEvent(self,event):
        self.__repaint = True

    def paintEvent(self,event):
        if not self.__repaint : return
        self.__repaint = True
        painter = QtGui.QPainter(self)
        painter.setPen(self.__outlinePen)
        width = self.width()
        height = self.height()
        painter.fillRect(0,0,width,height,self.__brush)

    def addButton(self,name:str,widget):
        icon = None
        try     : icon = widget.icon()
        except  : print(f"Failed to call icon() method on widget {widget}")
        self.__buttonList[name] = _C_QNavButton(self,name,icon)
        self.__widgetList[name] = widget
        self.__layout.addWidget(self.__buttonList[name],len(self.__buttonList)-1,0)
        self.__buttonList[name].clicked.connect(lambda: self.__buttonPressed(name))
        
    def __buttonPressed(self,name):
        if self.__lastActive == name: return
        self.__buttonList[name].activate()
        if not self.__lastActive is None: self.__buttonList[self.__lastActive].deactivate()
        self.__lastActive = name
        self.onPress.emit(name)

    def setWidget(self,name):
        return self.__buttonPressed(name)

class C_QNavigatorDock(QtWidgets.QDockWidget):
    def __init__(self,parent,nav):
        super().__init__(parent)
        self.__Nav = nav
        self.__parent = parent
        self.setContentsMargins(0,0,0,0)
        self.setWidget(self.__Nav)
        self.setFloating(False)
        self.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)