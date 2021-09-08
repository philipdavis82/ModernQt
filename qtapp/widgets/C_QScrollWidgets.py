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
    border: 4px solid #ffa02f;
    border-radius: 6px;
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

    def moveSignal(self,pos):
        self.move(pos - self.Parent.pos() - self.__renderOffest)

class C_QScrollItem(QtWidgets.QWidget):
    moved = QtCore.pyqtSignal(QtGui.QMouseEvent)
    floating = QtCore.pyqtSignal(QtWidgets.QWidget)
    dropped  = QtCore.pyqtSignal(QtWidgets.QWidget)
    def __init__(self,parent):
        super().__init__(parent)
        self.Parent = parent
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        
        self.setStyleSheet(WIDGET_STYLE_SHEET)

        self.setMinimumWidth(100)
        self.setMinimumHeight(100)

        self.setSizePolicy(QtWidgets.QSizePolicy.Expanding,QtWidgets.QSizePolicy.Expanding)
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
        # setup
        # self.setAcceptDrops(True)
        
        self.__floating = False
        self.__posoffset = None
        self.__defaultStyleSheet = WIDGET_STYLE_SHEET
        self.__floatingStyleSheet = WIDGET_STYLE_SHEET_FLOATING

        

    def mouseOffset(self):
        return self.__posoffset

    def mousePressEvent(self,event):
        self.__posoffset = event.pos() #event.globalPos() - self.pos()
        self.raise_()
        
    def mouseReleaseEvent(self,event):
        self.setStyleSheet(self.__defaultStyleSheet)
        # print('Dropped')
        # self.dropped.emit(self)
        self.__floating = False
        self.update()

    def mouseMoveEvent(self,event):
        if not self.__floating: self.enterFloating(event.pos())
        event.accept()

    def enterFloating(self,offset):
        
        # print("Grabbed")
        
        _drag = QtGui.QDrag(self)
        _mime = QtCore.QMimeData()
        _mime.setText("Floating Widget")
        _drag.setMimeData(_mime)
        _drag.setHotSpot(offset)
        
        __render = QtGui.QPixmap(self.size())
        self.render(__render)
        _drag.setPixmap(__render)

        self.setStyleSheet(self.__floatingStyleSheet)

        self.floating.emit(self)

        _drag.exec()

        self.setStyleSheet(self.__defaultStyleSheet)

    def setDefaultStyle(self,style:str):
        self.__defaultStyleSheet = style
    
    def setPreviewStyle(self,style:str):
        self.__floatingStyleSheet = style

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

        self.__widgets = []
        # self.
    
    def setDirection(self,direction):
        # print(direction)
        self.__layoutDirection = direction

    def takeAt(self,N):
        try: self.__widgets.pop(N)
        except: pass
        child = self.layout.takeAt(N)
        if child is None:
            minimum = 0 
            for widget in self.__widgets: minimum += (widget.minimumHeight() + self._spacing)
            self.setMinimumParameter(minimum)
            return child
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
        min += self._spacing
        if self.__layoutDirection == "Horizontal" : 
            self.setMaximumWidth(min)
            return self.setMinimumWidth(min)
        if self.__layoutDirection == "Vertical" :
            self.setMaximumHeight(min) 
            return self.setMinimumHeight(min)
        raise Exception("Failed")
    
    def changeMinimumParameter(self,min):
        assert( (self.minimumParameter() + min) >= 0 )
        self.setMinimumParameter(self.minimumParameter() + min)

    def addWidget(self,widget):
        self.__widgets.append(widget)
        if   self.__layoutDirection == "Horizontal" : 
            self.layout.addWidget(widget,0,self.__N)
            self.changeMinimumParameter( widget.minimumHeight() + self._spacing )
        elif self.__layoutDirection == "Vertical" : 
            self.layout.addWidget(widget,self.__N,0)
            self.changeMinimumParameter( widget.minimumWidth() + self._spacing )
        else: raise Exception(f"direction needs to be 'Horizontal' or 'Vertical'")
        self.__N += 1

    def getDropPosition(self,event,offset):
        # TODO both orientations
        i = 0
        if self.__layoutDirection == "Vertical":
            for i,widget in enumerate(self.__widgets):
                if (event.pos().y()+offset) < (widget.pos().y() + (widget.height()/2)): break
            else:
                return i+1
            return i
        elif self.__layoutDirection == "Horizontal":
            for i,widget in enumerate(self.__widgets):
                if (event.pos().x()+offset) < (widget.pos().x() + (widget.width()/2)): break
            else:
                return i+1
            return i

class C_QScrollArea(QtWidgets.QScrollArea):
    def __init__(self,parent,name=None,renderArea=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)
        self.setStyleSheet(SCROLL_STYLE_SHEET)
        self.setMouseTracking(True)
        self.__name = name

        # setup
        self.setAcceptDrops(True)

        #private
        self.__innerWidget = _C_QInnerScrollArea(self)
        self.setWidget(self.__innerWidget)
        self.__innerWidget.setVisible(True)
        self.__heldWidgets = []
        self.__layoutDirection = None
        self.__scrollTimer = QtCore.QTimer(self)
        self.__dragTrack = None
        self.__sliderVal = 0
        self.__previewWidget = C_QScrollItem(self)
        self.__previewWidget.setDefaultStyle(WIDGET_STYLE_SHEET_FLOATING)

        self.setVertical()
        
    def dragLeaveEvent(self,event):
        if self.__scrollTimer.isActive(): 
            self.__scrollTimer.stop()
        if not self.__dragTrack is None: 
            II = self.getIndex(self.__dragTrack)
            if not II is None: self.removeWidget(self.__dragTrack)
        self.resetLayout()
        self.__dragTrack = None
        event.accept()

    def dragEnterEvent(self,event):
        if self.__scrollTimer.isActive(): 
            self.__scrollTimer.stop()
        self.__dragTrack = event.source()
        self.addWidget(self.__dragTrack)
        self.resetLayout()
        event.accept()

    def dragMoveEvent(self,event):
        # TODO Make this work for horizontal areas
        self.__dragTrack = event.source()
        if self.__layoutDirection == "Vertical":
            if event.pos().y() < 20:
                if not self.__scrollTimer.isActive():
                    self.__scrollTimer = QtCore.QTimer(self) 
                    self.__scrollTimer.timeout.connect(self.scrollUp)
                    self.__scrollTimer.start(25)
            elif event.pos().y() > self.height()-20:
                if not self.__scrollTimer.isActive():
                    self.__scrollTimer = QtCore.QTimer(self) 
                    self.__scrollTimer.timeout.connect(self.scrollDown)
                    self.__scrollTimer.start(25)
            elif self.__scrollTimer.isActive(): 
                self.__scrollTimer.stop()
            I = self.__innerWidget.getDropPosition(event,self.verticalScrollBar().value())
        if self.__layoutDirection == "Horizontal":
            if event.pos().x() < 20:
                if not self.__scrollTimer.isActive():
                    self.__scrollTimer = QtCore.QTimer(self) 
                    self.__scrollTimer.timeout.connect(self.scrollLeft)
                    self.__scrollTimer.start(25)
            elif event.pos().x() > self.width()-20:
                if not self.__scrollTimer.isActive():
                    self.__scrollTimer = QtCore.QTimer(self) 
                    self.__scrollTimer.timeout.connect(self.scrollRight)
                    self.__scrollTimer.start(25)
            elif self.__scrollTimer.isActive(): 
                self.__scrollTimer.stop()
            I = self.__innerWidget.getDropPosition(event,self.horizontalScrollBar().value())
        # I = self.__innerWidget.getDropPosition(event,self.verticalScrollBar().value())
        II = self.getIndex(event.source())
        if I != II:
            if not II is None: self.removeWidget(event.source())
            self.insertWidget(I,event.source())
        event.accept()
    
    def dropEvent(self,event):
        if self.__scrollTimer.isActive(): 
            self.__scrollTimer.stop()
        self.__dragTrack = None

        # self.__innerWidget.dropWidget(event.source())
        event.accept()

    def scrollDown(self):
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.value()+15)
        self.__sliderVal = scrollbar.value()

    def scrollUp(self):
        scrollbar = self.verticalScrollBar()
        scrollbar.setValue(scrollbar.value()-15)
        self.__sliderVal = scrollbar.value() 
    
    def scrollRight(self):
        scrollbar = self.horizontalScrollBar()
        scrollbar.setValue(scrollbar.value()+15)
        self.__sliderVal = scrollbar.value()

    def scrollLeft(self):
        scrollbar = self.horizontalScrollBar()
        scrollbar.setValue(scrollbar.value()-15)
        self.__sliderVal = scrollbar.value() 

    def resizeEvent(self,event):
        if self.__layoutDirection == 'Horizontal':
            self.__innerWidget.resize(self.__innerWidget.width(),self.height()-10)
        if self.__layoutDirection == 'Vertical':
            self.__innerWidget.resize(self.width()-10,self.__innerWidget.height())

    def getIndex(self,widget):
        try: return self.__heldWidgets.index(widget)
        except: return None
    
    def addWidget(self,widget):
        self.__heldWidgets.append(widget)
        widget.floating.connect(self.widgetEnteredFloating)
        self.resetLayout()


    def widgetEnteredFloating(self,widget):
        self.__dragTrack = None
        self.removeWidget(widget)

    def removeWidget(self,widget):
        widget.setVisible(False)
        self.__heldWidgets.pop(self.getIndex(widget))
        widget.floating.disconnect(self.widgetEnteredFloating)
        self.resetLayout()

    def insertWidget(self,index,widget):
        self.__heldWidgets.insert(index,widget)
        self.resetLayout()

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

    def removeWidget(self,widget):
        try: self.__heldWidgets.pop(self.__heldWidgets.index(widget))
        except: print(f"Failed To Remove Widget {widget}")
    
    def getWidget(self,name):
        return self.__heldWidgetTable.get(name)

    def __clearLayout(self):
        child = True
        while(child):
            child = self.__innerWidget.takeAt(0)
            if child is None: return 
            child.widget().setVisible(False)
    
    def __setUpLayout(self):
        for i,widget in enumerate(self.__heldWidgets):
            self.__innerWidget.addWidget(widget)
            widget.setVisible(True) 
        if not self. __dragTrack is None: self.verticalScrollBar().setValue(self.__sliderVal)

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
