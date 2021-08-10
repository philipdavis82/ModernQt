# Left side navigator 


from qtapp import subwindows

import PyQt5.QtCore    as QtCore
import PyQt5.QtGui     as QtGui
import PyQt5.QtWidgets as QtWidgets

class _C_QNavButton(QtWidgets.QWidget):
    clicked = QtCore.pyqtSignal()
    def __init__(self,parent,name:str,img=None,*args,**kwargs):
        super().__init__(parent)
        self.__name = name
        self.__img  = img
        
        self.setMinimumHeight(80)
        # Visual Classes
        self.__brush = QtGui.QBrush(QtGui.QColor(0x2f2f2f))
        self.__outlinePen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(0x3f3f3f)),5)
        self.__highlightPen = QtGui.QPen(QtGui.QBrush(QtGui.QColor(0x5f5f5f)),5)
        
        # Internal State Machine
        self.__highlight = False

    def enterEvent(self,event):
        self.__highlight = True

    def leaveEvent(self,event):
        self.__highlight = False

    def mousePressEvent(self,event):
        self.clicked.emit()

    def paintEvent(self,event):
        painter = QtGui.QPainter(self)
        if self.__highlight: painter.setPen(self.__highlightPen) 
        else               : painter.setPen(self.__outlinePen)
        width = self.width()
        height = self.height()
        painter.fillRect(0,0,width,height,self.__brush)
        painter.drawRect(1,1,width-1,height-1)

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
        self.__layout.setSpacing(4)
        self.__layout.setContentsMargins(5,5,5,5)
        self.__layout.addItem(QtWidgets.QSpacerItem(0, 99, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding),99,0,1,1)

        # Visual Classes
        self.__brush = QtGui.QBrush(QtGui.QColor(0x1f1f1f))
        self.__outlinePen = QtGui.QPen(self.__brush,5)

        # State Machine information
        self.__repaint = False
        
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
        self.__buttonList[name] = _C_QNavButton(self,name)
        self.__widgetList[name] = widget
        self.__layout.addWidget(self.__buttonList[name],len(self.__buttonList)-1,0)
        self.__buttonList[name].clicked.connect(lambda: self.__buttonPressed(name))
        
    def __buttonPressed(self,name):
        self.onPress.emit(name)

class C_QNavigatorDock(QtWidgets.QDockWidget):
    def __init__(self,parent,nav):
        super().__init__(parent)
        self.__Nav = nav
        self.__parent = parent
        self.setContentsMargins(0,0,0,0)
        self.setWidget(self.__Nav)
        self.setFloating(False)
        self.setFeatures(QtWidgets.QDockWidget.NoDockWidgetFeatures)