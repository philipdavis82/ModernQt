import PyQt5.QtCore    as QtCore
import PyQt5.QtGui     as QtGui
import PyQt5.QtWidgets as QtWidgets

# Get App specific widgets
from qtapp.appwidgets.C_QNavigator import C_QNavigatorDock,C_QNavigator
from qtapp.appwidgets.C_QFileTree  import C_QFileTree
from . import subwindows

class Action(QtWidgets.QAction):
    def __init__(self,*args,shortcut=None):
        super(Action,self).__init__(*args)
        if not shortcut is None:
            self.setShortcut(shortcut) 
    
    def connect(self,fn):
        self.triggered.connect(fn)
        return self


class mainWindow(QtWidgets.QMainWindow):
    def __init__(self,application,sysargs = None):
        super().__init__()

        #Widget Layout
        self.setGeometry(100,100,1000,500)
        self.centralWidget = QtWidgets.QWidget(self)
        self.layout = QtWidgets.QGridLayout(self.centralWidget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0,0,0,0)
        self.setContentsMargins(0,0,0,0)

        self.setCentralWidget(self.centralWidget)

        # TODO: Add Drag function
        self.setWindowFlags(QtCore.Qt.Window | QtCore.Qt.FramelessWindowHint)
  
        # Internal Memory
        self.mainWidgetMap = {}
        self.currentMainWidget = None

        # Grips
        self.grips = []
        self.gripSize = 16
        
        # Build the gui
        self.createMenu()
        self.createInputs()
        self.buildInteractions()
        
        #Private States
        # Objects
        self.__qtapplication = application
        self.__oneshotTimer  = QtCore.QTimer()
        # States
        self.__isMaximized = False
        self.__disableDrag = False
        self.__lastHeight = 0
        self.__lastWidth  = 0
        self.__lastXPos   = 0
        self.__lastYPos   = 0

     
    def createMenu(self):
        self.mainMenu = self.menuBar()
       

        self.mainMenu.installEventFilter(self)
        
        #
        ## File Menu
        #
        fileMenu = self.mainMenu.addMenu('&File')

        # Actions
        # loadAct = Action("load",self).connect(self.openFile)
        # self.mainMenu.addAction(loadAct)

        #exit
        exitAct = Action("Exit",self).connect(self.close)
        self.mainMenu.addAction(exitAct)
        pass

    def createWidgets(self):
        # self.searchWidget = subwindows.SearchWidget(self)
        # self.searchWidget.setVisible(False)
        # self.mainWidgetMap['search'] = self.searchWidget
        self.mainWidgetMap['tree'] = C_QFileTree(self)
        self.mainWidgetMap['tree'].setVisible(False)

        self.mainWidgetMap['dummy'] = QtWidgets.QWidget(self)
        self.mainWidgetMap['dummy'].setVisible(False)
        pass

    def buildInteractions(self):
        for i in range(4):
            grip = QtWidgets.QSizeGrip(self)
            grip.resize(self.gripSize, self.gripSize)
            self.grips.append(grip)
    
    def resizeEvent(self,event):
        rect = self.rect()
        self.__isMaximized = False
        # top left grip doesn't need to be moved...
        # top right
        self.grips[1].move(rect.right() - self.gripSize, 0)
        # bottom right
        self.grips[2].move(
            rect.right() - self.gripSize, rect.bottom() - self.gripSize)
        # bottom left
        self.grips[3].move(0, rect.bottom() - self.gripSize)

    def createInputs(self):
        self.createWidgets()
        # Left Side
        self.leftNavigator = C_QNavigator(self)
        for name,widget in self.mainWidgetMap.items(): self.leftNavigator.addButton(name,widget)
        self.leftNavigator.setMaximumWidth(200)
        self.leftNavigator.setMinimumWidth(200)
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea,C_QNavigatorDock(self,self.leftNavigator))
        self.leftNavigator.onPress.connect(self.mainWidgetChanged)
        # self.layout.addWidget(self.leftNavigator,0,0)

        self.mainWidgetChanged('dummy')
        # self.layout.addWidget(self.searchWidget,0,1)

        
        pass

        
    def eventFilter(self,watched,event):
        if(watched == self.mainMenu):
            if (event.type() == QtCore.QEvent.MouseButtonPress):
                if (event.button() == QtCore.Qt.LeftButton):
                    self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
                    return False
            elif (event.type() == QtCore.QEvent.MouseButtonDblClick):
                self.toggleMaximized()
            elif (event.type() == QtCore.QEvent.MouseMove):
                if (event.buttons() & QtCore.Qt.LeftButton) and not self.__disableDrag:
                    if self.__isMaximized:
                        self.toggleMaximized()
                    self.move(event.globalPos() - self.dragPosition)
                    return False
        return super(mainWindow, self).eventFilter(watched, event)
    
    def toggleMaximized(self):
        if self.__isMaximized:
            # self.showNormal()
            self.__disableDrag = True
            self.setGeometry(
                self.__lastXPos,
                self.__lastYPos,
                self.__lastWidth,
                self.__lastHeight)
            self.__isMaximized = False
            self.__oneshotTimer.singleShot(100,lambda : self.setDrag(True))
        else:
            self.__lastHeight = self.height()
            self.__lastWidth  = self.width()
            self.__lastXPos   = self.pos().x()
            self.__lastYPos   = self.pos().y()
            self.move(0,0)
            self.resize(self.__qtapplication.primaryScreen().size())
            # self.showMaximized()
            self.__isMaximized = True
            self.__disableDrag = True
            self.__oneshotTimer.singleShot(100,lambda : self.setDrag(True))

    def setDrag(self,en):
        self.__disableDrag = not en

    def mainWidgetChanged(self,widgetName):
        if not self.currentMainWidget is None: 
            self.layout.removeWidget(self.currentMainWidget)
            self.currentMainWidget.setVisible(False)
        self.currentMainWidget = self.mainWidgetMap[widgetName]
        self.layout.addWidget(self.currentMainWidget,0,1)
        self.currentMainWidget.setVisible(True)
