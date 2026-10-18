"""Explicitly saved connection editor; no automatic discovery or live status claims."""
import sqlite3
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,QLabel,QPushButton,QComboBox,QLineEdit,QPlainTextEdit,QTableWidget,QTableWidgetItem,QAbstractItemView,QMessageBox
from topology_store import TopologyStore
from source_store import SourceStore
from source_ui import SourceSelector,explicit_buttons,STATUS_LABELS
from ui_i18n import tr,apply

def port_label(row):return row['short_id']+' · '+row['name']+' / '+row['label']

class LinkEditor(QDialog):
    def __init__(self,store,date_factory,original=None,parent=None):
        super().__init__(parent);self.store=store;self.original=original;self.saved_id=None
        self.setWindowTitle('Edit connection' if original else 'Add connection');self.resize(740,620);form=QFormLayout(self)
        self.a=QComboBox();self.b=QComboBox()
        for combo in (self.a,self.b):
            combo.addItem('Choose a saved interface',None)
            for row in store.endpoints():combo.addItem(port_label(row),row['interface_id'])
            combo.setToolTip('Save actual interfaces in Network identity first. Unknown MAC/IP addresses may remain blank.')
        form.addRow('Endpoint A',self.a);form.addRow('Endpoint B',self.b)
        self.medium=QComboBox();self.medium.addItem('Choose a connection medium',None)
        for value,label in [('ethernet','Ethernet'),('fiber','Fiber'),('wi-fi','Wi-Fi'),('powerline','Powerline'),('other','Other')]:self.medium.addItem(label,value)
        self.state=QComboBox()
        for value,label in [('planned','Planned'),('observed','Observed'),('retired','Retired')]:self.state.addItem(label,value)
        self.state.setToolTip('Observed means reported at a date, not currently online. Planned links are not installed links.')
        self.speed=QLineEdit();self.speed.setPlaceholderText('Unknown — leave blank');self.speed.setToolTip('Observed or planned link rate in Mbit/s, not measured throughput. Describe its meaning in Notes.')
        self.source=QLineEdit();self.date=date_factory();self.evidence=QComboBox()
        for value in ('uncertain','user_reported','verified'):self.evidence.addItem(STATUS_LABELS[value],value)
        self.sources=SourceSelector(SourceStore(store.path),date_factory);self.notes=QPlainTextEdit();self.notes.setMaximumHeight(90)
        for label,widget in [('Connection medium',self.medium),('Connection state',self.state),('Link rate (Mbit/s)',self.speed),('Information source / notes',self.source),('Observed / accessed on',self.date),('Verification status',self.evidence),('Sources and evidence',self.sources),('Notes',self.notes)]:form.addRow(label,widget)
        note=QLabel('Save connection commits this record immediately. Cancel leaves the record unchanged. Library entries created in the chooser save separately. Missing evidence warns; Verified requires evidence and a date.');note.setWordWrap(True);form.addRow(note)
        self.save_button=explicit_buttons(form,'Save connection',self.save,self.reject)
        if original:
            for combo,key in [(self.a,'endpoint_a'),(self.b,'endpoint_b'),(self.medium,'medium'),(self.state,'state'),(self.evidence,'evidence_status')]:combo.setCurrentIndex(combo.findData(original[key]))
            self.speed.setText('' if original['speed_mbps'] is None else str(original['speed_mbps']));self.source.setText(original['source'] or '');self.date.load(original['observed_on']);self.sources.load(original['source_ids']);self.notes.setPlainText(original['notes'] or '')
        apply(self)
    def value(self):return dict(endpoint_a=self.a.currentData(),endpoint_b=self.b.currentData(),medium=self.medium.currentData(),state=self.state.currentData(),speed_mbps=self.speed.text(),source=self.source.text(),observed_on=self.date.value(),evidence_status=self.evidence.currentData(),source_ids=self.sources.value(),notes=self.notes.toPlainText())
    def save(self):
        try:
            data=self.value()
            if not data['source'].strip() and not data['source_ids']:
                if QMessageBox.question(self,tr('Missing connection evidence'),tr('No evidence source is selected. Save this unverified connection anyway?'),QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)!=QMessageBox.Yes:return
            self.saved_id=self.store.save(data,self.original);self.accept()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,tr('Could not save connection'),tr(str(exc)))

class LinkManager(QDialog):
    def __init__(self,path,date_factory,parent=None):
        super().__init__(parent);self.store=TopologyStore(path);self.date_factory=date_factory
        self.setWindowTitle('Network connections');self.resize(1000,520);layout=QVBoxLayout(self)
        note=QLabel('Recorded topology, not a live network scan. Save device changes before opening this list. Double-click a connection to edit.');note.setWordWrap(True);layout.addWidget(note)
        self.table=QTableWidget(0,5);self.table.setHorizontalHeaderLabels(['Endpoint A','Endpoint B','Connection medium','Connection state','Link rate (Mbit/s)']);self.table.setSelectionBehavior(QAbstractItemView.SelectRows);self.table.setSelectionMode(QAbstractItemView.SingleSelection);self.table.setEditTriggers(QAbstractItemView.NoEditTriggers);self.table.horizontalHeader().setStretchLastSection(True);layout.addWidget(self.table)
        buttons=QHBoxLayout()
        for label,callback in [('Add connection…',self.add),('Edit connection…',self.edit),('Remove connection…',self.remove),('Refresh',self.refresh),('Close',self.accept)]:
            button=QPushButton(label);button.clicked.connect(callback);buttons.addWidget(button)
        layout.addLayout(buttons);self.table.doubleClicked.connect(self.edit);self.refresh();apply(self)
    def current(self):
        n=self.table.currentRow();return self.table.item(n,0).data(Qt.UserRole) if n>=0 else None
    def refresh(self):
        try:
            ports={r['interface_id']:port_label(r) for r in self.store.endpoints()};rows=self.store.list();self.table.setRowCount(len(rows))
            for n,row in enumerate(rows):
                for col,value in enumerate([ports[row['endpoint_a']],ports[row['endpoint_b']],row['medium'],tr({'planned':'Planned','observed':'Observed','retired':'Retired'}[row['state']]),'—' if row['speed_mbps'] is None else str(row['speed_mbps'])]):
                    item=QTableWidgetItem(value);item.setData(Qt.UserRole,row);self.table.setItem(n,col,item)
            self.table.resizeColumnsToContents()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,tr('Network connections'),tr(str(exc)))
    def add(self):
        if LinkEditor(self.store,self.date_factory,parent=self).exec()==QDialog.Accepted:self.refresh()
    def edit(self,*_):
        row=self.current()
        if row and LinkEditor(self.store,self.date_factory,row,self).exec()==QDialog.Accepted:self.refresh()
    def remove(self):
        row=self.current()
        if not row:return
        if QMessageBox.question(self,tr('Remove connection'),tr('Remove this connection record? Devices stay unchanged; connection history is retained.'),QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)!=QMessageBox.Yes:return
        try:self.store.remove(row);self.refresh()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,tr('Could not save connection'),tr(str(exc)))
