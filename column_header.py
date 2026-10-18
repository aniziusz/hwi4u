"""One-click accessible filter buttons attached to logical column identities."""
from PySide6.QtCore import Qt,QRect,QSize,Signal
from PySide6.QtWidgets import QHeaderView,QToolButton,QStyleOptionHeader,QStyle
from ui_i18n import tr

class FilterHeader(QHeaderView):
    filterRequested=Signal(int)
    def __init__(self,table):
        super().__init__(Qt.Horizontal,table);self.buttons={};self.active=set();self.setMinimumSectionSize(76)
        self.sectionResized.connect(self.position_buttons);self.sectionMoved.connect(self.position_buttons);self.geometriesChanged.connect(self.position_buttons)
        table.horizontalScrollBar().valueChanged.connect(self.position_buttons)
    def sync(self,labels,active):
        self.active=set(active)
        for index,label in enumerate(labels):
            if index not in self.buttons:
                button=QToolButton(self.viewport());button.setAutoRaise(True);button.setFocusPolicy(Qt.StrongFocus);button.clicked.connect(lambda checked=False,i=index:self.filterRequested.emit(i));self.buttons[index]=button
            button=self.buttons[index];is_active=index in self.active;button.setText('● ▾' if is_active else '▾');button.setAccessibleName(tr('Filter column: ')+label);button.setToolTip(tr('Filter column: ')+label+(' · '+tr('Filter active') if is_active else ''));button.setProperty('_literal_text',True);button.setProperty('_literal_tip',True)
        self.position_buttons();self.viewport().update()
    def position_buttons(self,*_):
        for index,button in self.buttons.items():
            x=self.sectionViewportPosition(index)+self.sectionSize(index)-32 if index<self.count() else -32
            visible=index<self.count() and not self.isSectionHidden(index) and x+30>0 and x<self.viewport().width()
            button.setVisible(visible)
            if visible:button.setGeometry(x,1,30,max(24,self.height()-2))
    def resizeEvent(self,event):
        super().resizeEvent(event);self.position_buttons()
    def sizeHint(self):
        size=super().sizeHint();return QSize(size.width(),max(30,size.height()))
    def paintSection(self,painter,rect,index):
        if not rect.isValid():return
        option=QStyleOptionHeader();self.initStyleOptionForIndex(option,index);option.rect=QRect(rect);option.rect.setWidth(max(0,rect.width()-32))
        painter.save();painter.fillRect(rect,self.palette().button());self.style().drawControl(QStyle.CE_Header,option,painter,self);painter.restore()
