"""Source library dialogs; immutable entries save immediately, assignments on device save."""
import sqlite3
import html
from pathlib import Path
from PySide6.QtCore import Qt,QUrl,Signal
from PySide6.QtGui import QDesktopServices
from PySide6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QPushButton,QLineEdit,QComboBox,QPlainTextEdit,QListWidget,QListWidgetItem,QDialogButtonBox,QFileDialog,QMessageBox)
from ui_i18n import tr,apply
from source_store import SourceStore,asset_path

STATUS_LABELS={'uncertain':'Uncertain','user_reported':'User reported','verified':'Verified'}

def explicit_buttons(layout,label,accepted,rejected):
    row=QHBoxLayout();row.addStretch();accept=QPushButton(label);accept.clicked.connect(accepted);cancel=QPushButton('Cancel');cancel.clicked.connect(rejected);row.addWidget(accept);row.addWidget(cancel)
    if isinstance(layout,QFormLayout):layout.addRow(row)
    else:layout.addLayout(row)
    return accept

KIND_LABELS={'website':'Website','document':'Document (PDF)','photo':'Photo','observation':'Observation','legacy_text':'Preserved source text'}


def open_source(parent,store,row):
    try:
        if row['kind'] in ('observation','legacy_text'):
            dialog=QDialog(parent);dialog.setWindowTitle(tr('Source text' if row['kind']=='legacy_text' else 'Source observation'));layout=QVBoxLayout(dialog)
            text=QPlainTextEdit();text.setPlainText(row['body'] or '');text.setReadOnly(True);layout.addWidget(text)
            close=QPushButton(tr('Close'));close.clicked.connect(dialog.accept);layout.addWidget(close);dialog.resize(680,400);dialog.exec();return
        if row['kind']=='website':
            from manual_store import validate_url
            url=QUrl(validate_url(row['url']))
        else:
            from photo_files import sha256
            file=asset_path(store.db.parent,row['relative_path'])
            if not file.is_file() or sha256(file)!=row['sha256']:raise ValueError('Source file is missing or changed.')
            url=QUrl.fromLocalFile(str(file))
        if not QDesktopServices.openUrl(url):raise ValueError('Could not open the selected source.')
    except (ValueError,OSError) as exc:QMessageBox.warning(parent,tr('Could not open source'),str(exc))


class SourceEditor(QDialog):
    def __init__(self,store,date_factory,original=None,parent=None):
        super().__init__(parent);self.store=store;self.original=original;self.saved_id=None
        self.setWindowTitle(tr('Revise source' if original else 'Add source'));self.resize(660,570);form=QFormLayout(self)
        self.kind=QComboBox()
        for value,label in KIND_LABELS.items():self.kind.addItem(label,value)
        self.title=QLineEdit();self.url=QLineEdit();self.file=QLineEdit();self.file.setReadOnly(True);self.body=QPlainTextEdit();self.body.setMaximumHeight(130);self.note=QLineEdit();self.date=date_factory();self.status=QComboBox()
        for value in ('uncertain','user_reported','verified'):self.status.addItem(STATUS_LABELS[value],value)
        for label,widget in [('Source kind',self.kind),('Title *',self.title),('Online URL',self.url),('Observation / notes',self.body),('Origin / provenance',self.note),('Observed / accessed on',self.date),('Verification status',self.status)]:form.addRow(label,widget)
        files=QHBoxLayout();files.addWidget(self.file,1);self.choose=QPushButton('Choose source file…');self.choose.clicked.connect(self.choose_file);files.addWidget(self.choose);form.addRow('Local file',files)
        self.note.setToolTip('Who supplied this source, or where it came from. A source does not independently verify a device or its installed state.')
        self.date.setToolTip('Actual observation or access date. Leave unknown if unavailable; no date is filled automatically.')
        self.status.setToolTip('Verified means you checked this source and requires a date. It does not automatically verify linked device assessments.')
        note=QLabel('Library entries save immediately. Revisions create a new entry; old sources and existing assignments remain unchanged. Assignments save with the parent form.');note.setWordWrap(True);form.addRow(note)
        self.save_button=explicit_buttons(form,'Save source',self.save,self.reject)
        self.kind.currentIndexChanged.connect(self.update_kind)
        if original:
            self.kind.setCurrentIndex(self.kind.findData(original['kind']));self.kind.setEnabled(False)
            self.title.setText(original['title']);self.url.setText(original['url'] or '');self.body.setPlainText(original['body'] or '');self.note.setText(original['source_note'] or '');self.date.load(original['observed_on']);self.status.setCurrentIndex(self.status.findData(original['evidence_status']));self.file.setText(original['original_name'] or '')
        self.update_kind();apply(self)
    def update_kind(self,*_):
        kind=self.kind.currentData();self.url.setEnabled(kind=='website');self.file.setEnabled(kind in ('document','photo'));self.choose.setEnabled(kind in ('document','photo') and self.original is None)
    def choose_file(self):
        path,_=QFileDialog.getOpenFileName(self,tr('Choose source file'),'', 'PDF (*.pdf)' if self.kind.currentData()=='document' else 'Images (*.jpg *.jpeg *.png)')
        if path:self.file.setText(path)
    def save(self):
        data=dict(kind=self.kind.currentData(),title=self.title.text(),url=self.url.text() if self.kind.currentData()=='website' else None,body=self.body.toPlainText(),source_note=self.note.text(),observed_on=self.date.value(),evidence_status=self.status.currentData())
        try:self.saved_id=self.store.save(data,self.file.text() or None,self.original);self.accept()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,tr('Could not save source'),str(exc))


class SourceLibrary(QDialog):
    def __init__(self,store,date_factory,selected,device=None,parent=None,read_only=False):
        super().__init__(parent);self.store=store;self.date_factory=date_factory;self.device=device;self.read_only=read_only
        self.setWindowTitle(tr('Sources and evidence'));self.resize(850,580);layout=QVBoxLayout(self)
        self.search=QLineEdit();self.search.setPlaceholderText('Search source titles, URLs or observations…');layout.addWidget(self.search)
        self.list=QListWidget();layout.addWidget(self.list,1);self.search.textChanged.connect(self.filter)
        self.list.itemDoubleClicked.connect(lambda *_:self.open_selected())
        actions=QHBoxLayout();layout.addLayout(actions)
        for label,callback in [('Add source…',self.add),('Reuse manual/photo…',self.reuse),('Revise source…',self.revise),('Open source',self.open_selected)]:
            button=QPushButton(label);button.clicked.connect(callback);actions.addWidget(button)
            if label!='Open source':button.setEnabled(not read_only and (label!='Reuse manual/photo…' or bool(device)))
        self.hint=QLabel('Tick sources for this section. Untick to remove an assignment. New/revised library entries save immediately; assignments apply only when the parent form is saved.');self.hint.setWordWrap(True);layout.addWidget(self.hint)
        self.use_button=explicit_buttons(layout,'Close' if read_only else 'Use selected sources',self.accept,self.reject)
        self.populate(selected);apply(self)
    def selection(self):return sorted(self.list.item(n).data(Qt.UserRole)['source_id'] for n in range(self.list.count()) if self.list.item(n).checkState()==Qt.Checked)
    def populate(self,selected):
        self.list.clear()
        for row in self.store.list():
            suffix=(' · '+tr('Revision')) if row['supersedes'] else ''
            item=QListWidgetItem(row['title']+'\n'+tr(KIND_LABELS[row['kind']])+' · '+tr(STATUS_LABELS[row['evidence_status']])+' · '+(row['observed_on'] or tr('Unknown'))+suffix)
            item.setData(Qt.UserRole,row);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked if row['source_id'] in selected else Qt.Unchecked)
            if self.read_only:item.setFlags(item.flags() & ~Qt.ItemIsUserCheckable)
            item.setToolTip('<pre>'+html.escape((row['url'] or row['original_name'] or row['body'] or '')+'\n'+row['source_id'])+'</pre>');self.list.addItem(item)
        self.filter()
    def filter(self,*_):
        query=self.search.text().casefold()
        for n in range(self.list.count()):
            item=self.list.item(n);row=item.data(Qt.UserRole);item.setHidden(query not in ' '.join(str(row.get(k) or '') for k in ('title','url','body','source_note','source_id')).casefold())
    def current(self):return self.list.currentItem().data(Qt.UserRole) if self.list.currentItem() else None
    def add(self):
        if self.read_only:return
        dialog=SourceEditor(self.store,self.date_factory,parent=self)
        if dialog.exec()==QDialog.Accepted:self.populate(self.selection()+[dialog.saved_id])
    def revise(self):
        if self.read_only:return
        row=self.current()
        if not row:return
        dialog=SourceEditor(self.store,self.date_factory,row,self)
        if dialog.exec()==QDialog.Accepted:self.populate(self.selection()+[dialog.saved_id])
    def open_selected(self):
        row=self.current()
        if row:open_source(self,self.store,row)
    def reuse(self):
        if self.read_only:return
        dialog=QDialog(self);dialog.setWindowTitle(tr('Reuse an existing manual or photo'));layout=QVBoxLayout(dialog);listing=QListWidget();layout.addWidget(listing)
        for kind,row in self.store.reusable(self.device):
            item=QListWidgetItem(row.get('title') or row.get('caption') or row['original_name']);item.setData(Qt.UserRole,(kind,row));listing.addItem(item)
        note=QLabel('Existing managed files are reused without copying. Source verification and observation date stay unknown until supplied.');note.setWordWrap(True);layout.addWidget(note)
        explicit_buttons(layout,'Reuse selected reference',dialog.accept,dialog.reject);apply(dialog)
        if dialog.exec()==QDialog.Accepted and listing.currentItem():
            try:
                kind,row=listing.currentItem().data(Qt.UserRole);ident=self.store.import_existing(kind,row);self.populate(self.selection()+[ident])
            except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,tr('Could not save source'),str(exc))


class SourceSelector(QWidget):
    changed=Signal()
    def __init__(self,store,date_factory):
        super().__init__();self.store=store;self.date_factory=date_factory;self.device=None;self.ids=[];self.read_only=False
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0);self.summary=QLabel('No sources selected');self.summary.setTextFormat(Qt.PlainText);self.summary.setWordWrap(True);layout.addWidget(self.summary)
        button=QPushButton('Choose sources…');self.button=button;button.setToolTip('Select several existing sources or add evidence. Source assignments save together with the parent form.');button.clicked.connect(self.choose);layout.addWidget(button)
    def value(self):return list(self.ids)
    def load(self,ids,device=None):
        self.ids=sorted(ids);self.device=device;rows={r['source_id']:r for r in self.store.list()}
        titles=[rows[i]['title'] for i in self.ids if i in rows]
        display='; '.join(title if len(title)<=70 else title[:67]+'…' for title in titles[:2])
        if len(titles)>2:display+=' (+'+str(len(titles)-2)+')'
        self.summary.setProperty('_literal_text',bool(self.ids));self.summary.setText(display if self.ids else 'No sources selected')
        self.summary.setToolTip('<pre>'+html.escape(tr('Selected sources:')+'\n'+'\n'.join(titles))+'</pre>' if titles else '')
        apply(self)
    def set_read_only(self,value):
        self.read_only=bool(value);self.button.setText('View sources…' if value else 'Choose sources…');self.button.setEnabled(True);apply(self)
    def choose(self):
        dialog=SourceLibrary(self.store,self.date_factory,self.ids,self.device,self,read_only=self.read_only)
        if dialog.exec()==QDialog.Accepted and not self.read_only:self.load(dialog.selection(),self.device);self.changed.emit()
