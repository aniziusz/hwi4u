"""Wheel scrolling never edits closed choice/date/number fields implicitly."""
from PySide6.QtCore import QObject,QEvent
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QComboBox,QAbstractSpinBox,QAbstractScrollArea,QApplication,QWidget,QCalendarWidget

class WheelGuard(QObject):
    def eventFilter(self,obj,event):
        if event.type()!=QEvent.Wheel or not isinstance(obj,QWidget):return False
        field=obj
        while field is not None and not isinstance(field,(QComboBox,QAbstractSpinBox)):
            if isinstance(field,QCalendarWidget):return False
            field=field.parentWidget()
        if field is None:return False
        if isinstance(field,QComboBox) and field.view().isVisible():return False
        parent=field.parentWidget()
        while parent is not None:
            if isinstance(parent,QAbstractScrollArea):
                viewport=parent.viewport()
                forwarded=QWheelEvent(viewport.mapFromGlobal(event.globalPosition().toPoint()),event.globalPosition(),event.pixelDelta(),event.angleDelta(),event.buttons(),event.modifiers(),event.phase(),event.inverted())
                QApplication.sendEvent(viewport,forwarded)
                break
            parent=parent.parentWidget()
        event.accept();return True

def install_wheel_guard(app):
    if not hasattr(app,'inventory_wheel_guard'):
        app.inventory_wheel_guard=WheelGuard(app);app.installEventFilter(app.inventory_wheel_guard)
