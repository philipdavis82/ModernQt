import __global__,os

import PyQt5.QtCore    as QtCore
import PyQt5.QtGui     as QtGui
import PyQt5.QtWidgets as QtWidgets

SCROLL_STYLE_SHEET = """

QScrollArea
{
    border: 1px solid #7d7d7d;
}
"""

WIDGET_STYLE_SHEET = """
QWidget
{
    background-color : #4d4d4d;
    border: 1px solid #ffa02f;
    border-radius: 6px;
}
QWidget:hover
{
    border: 3px solid #ffa02f;
}
QScrollArea
{
    border: 1px solid #7d7d7d;
}
"""

WIDGET_STYLE_SHEET_FLOATING = """
QWidget
{
    background: transparent;
    border: 0px solid #ffa02f;
}
QScrollArea
{
    border: 1px solid #7d7d7d;
}
"""

RENDER_AREA_STYLE_SHEET = """
QLabel
{
    background: transparent;
    border: 0px solid #ffa02f;
}
"""

CURRENT_MOUSE_SELECTION = None


class C_QRenderArea(QtWidgets.QLabel):
    def __init__(self,parent):
        super().__init__(parent)
        self.setGeometry(-1,-1,0,0)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet(RENDER_AREA_STYLE_SHEET)
        # self.installEventFilter(EVENT_HANDLER)
        # self.layout = QtWidgets.QGridLayout(self)
        self.Parent = parent
        #private
        self.__rendering = False
        self.__render = None
        self.__renderOffest = None
        self.__drawnWidget = None

    def render(self,widget):
        self.resize(widget.size())
        self.__render = QtGui.QPixmap(widget.size())
        widget.render(self.__render)
        self.setPixmap(self.__render)
        widget.setStyleSheet(WIDGET_STYLE_SHEET_FLOATING)
        # widget.repaint()
        self.__renderOffest = widget.mouseOffset()
        self.__drawnWidget = widget
        global CURRENT_MOUSE_SELECTION
        CURRENT_MOUSE_SELECTION = self
        self.__rendering = True
    
    def removeRender(self,*args):
        self.setGeometry(-1,-1,0,0)
        self.clear()
        global CURRENT_MOUSE_SELECTION
        CURRENT_MOUSE_SELECTION = None
        self.__rendering = False

    def moveSignal(self,event):
        self.move(event.globalPos() - self.Parent.pos() - self.__renderOffest)

class C_QScrollItem(QtWidgets.QWidget):
    moved = QtCore.pyqtSignal(QtGui.QMouseEvent)
    floating = QtCore.pyqtSignal(QtWidgets.QWidget)
    dropped  = QtCore.pyqtSignal(QtWidgets.QWidget)
    def __init__(self,parent):
        super().__init__(parent)
        self.Parent = parent
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet(WIDGET_STYLE_SHEET)

        self.setMinimumWidth(200)
        self.setMinimumHeight(200)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        # setup
        self.setAcceptDrops(True)
        
        self.__floating = False
        self.__posoffset = None

    def mouseOffset(self):
        return self.__posoffset

    def mousePressEvent(self,event):
        self.__posoffset = event.pos() #event.globalPos() - self.pos()
        self.raise_()
        
    def mouseReleaseEvent(self,event):
        self.setStyleSheet(WIDGET_STYLE_SHEET)
        print('Dropped')
        self.dropped.emit(self)
        self.__floating = False
        self.update()

    def mouseMoveEvent(self,event):
        if not self.__floating: self.enterFloating()
        self.moved.emit(event)
        event.accept()

    def enterFloating(self):
        self.__floating = True
        print("Grabbed")
        self.floating.emit(self)

    def dragEnterEvent(self,event):
        print(self,event)


class _C_QInnerScrollArea(QtWidgets.QWidget):
    def __init__(self,parent):
        self.__layoutDirection = "Horizontal"
        super().__init__(parent)

        self._spacing = 5

        self.layout = QtWidgets.QGridLayout(self)
        self.layout.setSpacing(self._spacing)
        self.setMinimumWidth(0)
        self.setMinimumHeight(0)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.__N = 0
        # self.
    
    def setDirection(self,direction):
        print(direction)
        self.__layoutDirection = direction

    def takeAt(self,N):
        child = self.layout.takeAt(N)
        if child is None: return child
        self.__N -= 1
        self.changeMinimumParameter( - child.widget().minimumHeight() - self._spacing)
        return child

    def minimumParameter(self):
        if self.__layoutDirection == "Horizontal" : 
            return self.minimumWidth()
        if self.__layoutDirection == "Vertical" : 
            return self.minimumHeight()
        raise Exception("Failed")

    def setMinimumParameter(self,min):
        if self.__layoutDirection == "Horizontal" : 
            return self.setMinimumWidth(min)
        if self.__layoutDirection == "Vertical" : 
            return self.setMinimumHeight(min)
        raise Exception("Failed")
    
    def changeMinimumParameter(self,min):
        assert( (self.minimumParameter() + min) >= 0 )
        self.setMinimumParameter(self.minimumParameter() + min)

    def addWidget(self,widget):
        if   self.__layoutDirection == "Horizontal" : 
            self.layout.addWidget(widget,0,self.__N)
            self.changeMinimumParameter( widget.minimumHeight() + self._spacing )
        elif self.__layoutDirection == "Vertical" : 
            self.layout.addWidget(widget,self.__N,0)
            self.changeMinimumParameter( widget.minimumWidth() + self._spacing )
        else: raise Exception(f"direction needs to be 'Horizontal' or 'Vertical'")
        self.__N += 1
         
class C_QScrollArea(QtWidgets.QScrollArea):
    def __init__(self,parent,name=None,renderArea=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet(SCROLL_STYLE_SHEET)
        self.setMouseTracking(True)
        # self.installEventFilter(__EVENT_HANDLER)
        self.__name = name

        # setup
        self.setAcceptDrops(True)

        #private
        self.__innerWidget = _C_QInnerScrollArea(self)
        self.setWidget(self.__innerWidget)
        self.__innerWidget.setVisible(True)
        self.__heldWidgets = {}
        self.__layoutDirection = None

        if renderArea is None: self.__renderArea = C_QRenderArea(self)
        else: self.__renderArea = renderArea

        self.setVertical()
        
    def dropEvent(self,event):
        print(self, event)

    def resizeEvent(self,event):
        if self.__layoutDirection == 'Horizontal':
            self.__innerWidget.resize(self.__innerWidget.width(),self.height()-10)
        if self.__layoutDirection == 'Vertical':
            self.__innerWidget.resize(self.width()-10,self.__innerWidget.height())

    def addWidget(self,name:str,widget:C_QScrollItem):
        assert(type(widget) == C_QScrollItem)
        
        widget.floating.connect(self.__renderArea.render)
        widget.dropped.connect(self.__renderArea.removeRender)
        widget.moved.connect(self.__renderArea.moveSignal)

        self.__heldWidgets[name] = widget
        self.resetLayout()

    def removeWidget(self,name:str):
        self.__heldWidgets.pop(name).setVisible(False)

    def setVertical(self):
        if self.__layoutDirection == "Vertical": return
        self.__layoutDirection = "Vertical"
        self.__innerWidget.setDirection(self.__layoutDirection)
        self.resetLayout()
        
    def setHorizontal(self):
        if self.__layoutDirection == "Horizontal": return
        self.__layoutDirection = "Horizontal"
        self.__innerWidget.setDirection(self.__layoutDirection)
        self.resetLayout()

    def resetLayout(self):
        self.__clearLayout()
        self.__setUpLayout()

    def getWidget(self,name):
        return self.__heldWidgets.get(name)

    def __clearLayout(self):
        child = True
        while(child):
            child = self.__innerWidget.takeAt(0)
            if child is None: return 
            child.widget().setVisible(False)
    
    def __setUpLayout(self):
        for i,widget in enumerate(self.__heldWidgets.values()):
            self.__innerWidget.addWidget(widget)
            widget.setVisible(True) 

class C_QMultiScrollArea(QtWidgets.QScrollArea):
    def __init__(self,parent):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.layout = QtWidgets.QGridLayout(self)

        #private
        self.__heldWidgets = {}
        self.__layoutDirection = "Vertical"

    def addScrollArea(self,name:str,widget:C_QScrollArea):
        assert(type(widget) == C_QScrollArea)
        self.__heldWidgets[name] = widget
        self.resetLayout()

    def removeScrollArea(self,name:str):
        self.__heldWidgets[name].setVisible(False)

    def setVertical(self):
        if self.__layoutDirection == "Vertical": return
        self.__layoutDirection = "Vertical"
        self.resetLayout()
        
    def setHorizontal(self):
        if self.__layoutDirection == "Horizontal": return
        self.__layoutDirection = "Horizontal"
        self.resetLayout()

    def resetLayout(self):
        self.__clearLayout()
        self.__setUpLayout()

    def getWidget(self,name):
        return self.__heldWidgets.get(name)

    def __clearLayout(self):
        child = True
        while(child):
            child = self.layout.takeAt(0)
            if child is None: return 
            child.widget().setVisible(False)
    
    def __setUpLayout(self):
        for i,widget in enumerate(self.__heldWidgets.values()):
            if self.__layoutDirection == "Horizontal":
                self.layout.addWidget(widget,i,0)
            if self.__layoutDirection == "Vertical":
                self.layout.addWidget(widget,0,i)
            widget.setVisible(True)
