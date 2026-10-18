"""Search existing dropdown choices without creating new catalogue entries."""
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import QComboBox,QCompleter,QApplication

class SearchComboBox(QComboBox):
    def __init__(self,parent=None):
        super().__init__(parent);self.setEditable(True);self.setInsertPolicy(QComboBox.NoInsert);self.setProperty('_searchable_choices',True)
        completer=QCompleter(self.model(),self);completer.setCaseSensitivity(Qt.CaseInsensitive);completer.setFilterMode(Qt.MatchContains);completer.setCompletionMode(QCompleter.PopupCompletion);self.setCompleter(completer)
        completer.activated[str].connect(self.choose_completion)
        self.lineEdit().setPlaceholderText('Type to find an existing choice…')
        self.lineEdit().editingFinished.connect(lambda:QTimer.singleShot(0,self.restore_selection))
        self.lineEdit().setToolTip('Type part of a name, then choose a matching result. Typing alone does not apply a filter or create a new choice. Choose All groups or All types to reset.')
    def choose_completion(self,text):
        index=self.findText(text,Qt.MatchFixedString)
        if index>=0:self.setCurrentIndex(index);self.setEditText(self.itemText(index))
    def restore_selection(self):
        popup=self.completer().popup()
        if popup.isVisible():return
        if self.currentIndex()>=0:self.setEditText(self.itemText(self.currentIndex()))
