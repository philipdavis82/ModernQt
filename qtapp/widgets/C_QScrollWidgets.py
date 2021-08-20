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
    background-color : #3d3d3d;
    border: 1px solid #ffa02f;
}
QScrollArea
{
    border: 1px solid #7d7d7d;
}
"""

class C_QScrollItem(QtWidgets.QWidget):
    moved = QtCore.pyqtSignal(QtGui.QMouseEvent)
    floating = QtCore.pyqtSignal()
    dropped  = QtCore.pyqtSignal()
    def __init__(self,parent):
        super().__init__(parent)
        self.Parent = parent
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet(WIDGET_STYLE_SHEET)

        self.setMinimumWidth(200)
        self.setMinimumHeight(200)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        self.__floating = False
        self.__posoffset = None

    def mousePressEvent(self,event):
        self.__posoffset = event.globalPos() - self.pos()
        self.raise_()
        
        
    
    def mouseReleaseEvent(self,event):
        print('Dropped')
        self.dropped.emit()
        self.__floating = False
        self.update()
    
    def mouseMoveEvent(self,event):
        if not self.__floating: 
            self.__floating = True
            print("Grabbed")
            self.floating.emit()
        self.move(event.globalPos() - self.__posoffset)
        self.moved.emit(event)

class _C_QInnerScrollArea(QtWidgets.QWidget):
    def __init__(self,parent):
        self.__layoutDirection = "Horizontal"
        super().__init__(parent)

        self.layout = QtWidgets.QGridLayout(self)

        self.setMinimumWidth(0)
        self.setMinimumHeight(0)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)

        self.__N = 0
        
    
    def setDirection(self,direction):
        print(direction)
        self.__layoutDirection = direction

    def takeAt(self,N):
        child = self.layout.takeAt(N)
        if child is None: return child
        self.__N -= 1
        self.changeMinimumParameter( - child.widget().minimumHeight() )
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
            self.changeMinimumParameter( widget.minimumHeight() )
        elif self.__layoutDirection == "Vertical" : 
            self.layout.addWidget(widget,self.__N,0)
            self.changeMinimumParameter( widget.minimumWidth() )
        else: raise Exception(f"direction needs to be 'Horizontal' or 'Vertical'")
        self.__N += 1
        
        

class C_QScrollArea(QtWidgets.QScrollArea):
    def __init__(self,parent,name=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet(SCROLL_STYLE_SHEET)
        self.__name = name

        self.__innerWidget = _C_QInnerScrollArea(self)
        self.setWidget(self.__innerWidget)
        self.__innerWidget.setVisible(True)
        # self.layout = QtWidgets.QGridLayout(self.__innerWidget)

        #private
        self.__heldWidgets = {}
        self.__layoutDirection = None
        self.setVertical()
        
    def resizeEvent(self,event):
        if self.__layoutDirection == 'Horizontal':
            self.__innerWidget.resize(self.__innerWidget.width(),self.height()-10)
        if self.__layoutDirection == 'Vertical':
            self.__innerWidget.resize(self.width()-10,self.__innerWidget.height())
            
    def mouseMoveEvent(self,event):
        print(self.__name)

    def addWidget(self,name:str,widget:C_QScrollItem):
        assert(type(widget) == C_QScrollItem)
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


