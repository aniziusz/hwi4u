"""Lifecycle observation editing and explicit review of exact model suggestions."""
import copy,sqlite3,contextlib
from PySide6.QtCore import QDate,Qt,Signal
from PySide6.QtWidgets import (QWidget,QGroupBox,QVBoxLayout,QHBoxLayout,QFormLayout,QComboBox,QLineEdit,QLabel,QPushButton,QDialog,QListWidget,QListWidgetItem,QMessageBox,QDateEdit,QInputDialog,QCheckBox,QScrollArea,QPlainTextEdit)
from lifecycle import KINDS,validate_records,bounds,warnings,ModelStore
from source_ui import SourceSelector
from ui_i18n import tr,apply


def buttons(layout,label,save,cancel):
    row=QHBoxLayout();yes=QPushButton(label);yes.clicked.connect(save);row.addWidget(yes);no=QPushButton('Cancel changes');no.clicked.connect(cancel);row.addWidget(no);layout.addLayout(row);return yes

class LifecycleEditor(QDialog):
    def __init__(self,panel,original=None):
        super().__init__(panel);self.panel=panel;self.result_record=None
        self.setWindowTitle(tr('Lifecycle date'));self.resize(700,700)
        outer=QVBoxLayout(self);scroll=QScrollArea();scroll.setWidgetResizable(True);body=QWidget();form=QFormLayout(body);self.form=form;scroll.setWidget(body);outer.addWidget(scroll)
        self.kind=QComboBox()
        for k,label in KINDS.items():self.kind.addItem(tr(label),k)
        form.addRow('Property',self.kind)
        self.precision=QComboBox()
        for k,label in [('day','Exact day'),('month','Month'),('quarter','Quarter'),('year','Year')]:self.precision.addItem(label,k)
        form.addRow('Date precision',self.precision)
        self.day=QDateEdit(QDate.currentDate());self.day.setDateRange(QDate(1,1,1),QDate(9999,12,31));self.day.setCalendarPopup(True);self.day.setDisplayFormat('yyyy-MM-dd');form.addRow('Date',self.day)
        self.partial=QLineEdit();self.partial.setPlaceholderText('YYYY-MM / YYYY-Q1 / YYYY');form.addRow('Partial date',self.partial)
        self.fields={}
        for key,label in [('provider','Provider / manufacturer'),('product','Product / exact model'),('version','Version / support track'),('applicability','Variant / region / service or warranty scope'),('note','Lifecycle notes')]:
            w=QLineEdit();w.setMaxLength(2000 if key=='note' else 200);form.addRow(label,w);self.fields[key]=w
        self.status=QComboBox()
        for k,label in [('uncertain','Uncertain'),('user_reported','User reported'),('verified','Verified')]:self.status.addItem(label,k)
        form.addRow('Verification status',self.status);self.observed=panel.date_factory();form.addRow('Observed / accessed on',self.observed)
        self.sources=SourceSelector(panel.source_store,panel.date_factory);form.addRow('Sources and evidence',self.sources)
        hint=QLabel('Nothing is dated automatically. Verified observations need verified dated sources. Software dates need provider, product and version; hardware service and warranty need an explicit scope.');hint.setWordWrap(True);form.addRow(hint)
        self.precision.currentIndexChanged.connect(self.precision_changed);self.precision_changed()
        if original:
            self.kind.setCurrentIndex(self.kind.findData(original['kind']));v=original['date'];precision='day' if len(v)==10 else 'quarter' if '-Q' in v else 'month' if len(v)==7 else 'year';self.precision.setCurrentIndex(self.precision.findData(precision))
            if precision=='day':self.day.setDate(QDate.fromString(v,'yyyy-MM-dd'))
            else:self.partial.setText(v)
            for k,w in self.fields.items():w.setText(original.get(k,''))
            self.status.setCurrentIndex(self.status.findData(original['status']));self.observed.load(original.get('observed_on') or None);self.sources.load(original['sources'],panel.device_id)
        else:
            self.fields['provider'].setText(panel.manufacturer());self.fields['product'].setText(panel.model());self.sources.load([],panel.device_id)
        buttons(outer,'Use lifecycle date',self.save,self.reject);apply(self)
    def precision_changed(self,*_):
        day=self.precision.currentData()=='day';self.form.setRowVisible(self.day,day);self.form.setRowVisible(self.partial,not day)
    def save(self):
        try:
            value=self.day.date().toString('yyyy-MM-dd') if self.precision.currentData()=='day' else self.partial.text().strip()
            precision=self.precision.currentData()
            if (precision=='year' and len(value)!=4) or (precision=='month' and (len(value)!=7 or '-Q' in value)) or (precision=='quarter' and (len(value)!=7 or '-Q' not in value)):raise ValueError('The date must match the selected precision.')
            row=dict(kind=self.kind.currentData(),date=value,status=self.status.currentData(),observed_on=self.observed.value() or '',sources=self.sources.value(),**{k:w.text() for k,w in self.fields.items()})
            with contextlib.closing(self.panel.device_store.connect()) as c:self.result_record=validate_records(c,[row])[0]
            self.accept()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,tr('Could not save'),tr(str(exc)))

class LifecyclePanel(QGroupBox):
    changed=Signal()
    warning_changed=Signal()
    def __init__(self,device_store,source_store,date_factory,manufacturer,model,purchase):
        super().__init__('Lifecycle dates');self.device_store=device_store;self.source_store=source_store;self.date_factory=date_factory;self.manufacturer=manufacturer;self.model=model;self.purchase=purchase;self.records=[];self.device_id=None;self.read_only=False
        layout=QVBoxLayout(self);self.list=QListWidget();self.list.setToolTip('Calendar dates allow purchase from one calendar year before release. Partial dates retain their original precision.');self.list.setMinimumHeight(130);self.list.setMaximumHeight(220);layout.addWidget(self.list)
        row=QHBoxLayout()
        for label,hint,fn in [('Add…','Add lifecycle date…',self.add),('Edit…','Edit lifecycle date…',self.edit),('Remove','Remove lifecycle date',self.remove)]:
            button=QPushButton(label);button.setToolTip(hint);button.clicked.connect(fn);row.addWidget(button)
        layout.addLayout(row);self.list.itemDoubleClicked.connect(lambda *_:self.edit())
        self.feedback=QLabel();self.feedback.setWordWrap(True);self.feedback.setStyleSheet('color:#ad5b00');layout.addWidget(self.feedback)
        hint=QLabel('Separate release, firmware security, OS security, hardware service, production and individual warranty dates. Unknown values remain blank. Changes save with Save device.');hint.setWordWrap(True);layout.addWidget(hint)
    def value(self):return copy.deepcopy(self.records)
    def load(self,records,device=None):self.records=copy.deepcopy(records);self.device_id=device;self.render()
    def render(self):
        self.list.clear()
        for kind,label in KINDS.items():
            entries=[(i,r) for i,r in enumerate(self.records) if r['kind']==kind]
            if not entries:
                item=QListWidgetItem(tr(label)+' — '+tr('Unknown'));item.setData(Qt.UserRole,('new',kind));self.list.addItem(item)
            for i,r in entries:
                item=QListWidgetItem(tr(label)+' — '+r['date']+' · '+' / '.join(x for x in (r['provider'],r['product'],r['version']) if x)+' · '+tr({'uncertain':'Uncertain','verified':'Verified','user_reported':'User reported'}[r['status']]));item.setData(Qt.UserRole,('edit',i));item.setToolTip(item.text()+'\n'+r['applicability']+'\n'+r['note']);self.list.addItem(item)
        self.update_warning()
    def update_warning(self,*_):
        try:notes=warnings(self.purchase(),self.records,self.manufacturer(),self.model())
        except ValueError:notes=[]
        self.feedback.setText('\n'.join(tr(s) for s in notes));self.feedback.setProperty('_literal_text',True);self.warning_changed.emit()
    def add(self):
        if self.read_only:return
        dialog=LifecycleEditor(self)
        if dialog.exec()==QDialog.Accepted:self.records.append(dialog.result_record);self.render();self.changed.emit()
    def edit(self):
        if self.read_only:return
        item=self.list.currentItem()
        if not item:return
        action,value=item.data(Qt.UserRole);dialog=LifecycleEditor(self,self.records[value] if action=='edit' else None)
        if action=='new':dialog.kind.setCurrentIndex(dialog.kind.findData(value))
        if dialog.exec()==QDialog.Accepted:
            if action=='edit':self.records[value]=dialog.result_record
            else:self.records.append(dialog.result_record)
            self.render();self.changed.emit()
    def remove(self):
        if self.read_only:return
        item=self.list.currentItem()
        if item and item.data(Qt.UserRole)[0]=='edit':
            del self.records[item.data(Qt.UserRole)[1]];self.render();self.changed.emit()

class ModelDialog(QDialog):
    def __init__(self,window):
        super().__init__(window);self.window=window;self.store=ModelStore(window.store.path);self.applied=None
        self.setWindowTitle(tr('Model suggestions'));self.resize(740,620);layout=QVBoxLayout(self)
        hint=QLabel('Exact manufacturer/model matches only. Select the applicable variant and review the proposed values. Applying changes only this form; Save device commits them. Existing values are replaced only after explicit confirmation.');hint.setWordWrap(True);layout.addWidget(hint)
        self.list=QListWidget();layout.addWidget(self.list);self.preview=QPlainTextEdit();self.preview.setReadOnly(True);layout.addWidget(self.preview)
        self.confirm=QCheckBox('I reviewed the variant, classification, roles and lifecycle dates.');layout.addWidget(self.confirm)
        self.save_button=QPushButton('Save current values as model profile…');self.save_button.clicked.connect(self.save_profile);layout.addWidget(self.save_button)
        library_hint=QLabel('Model library changes save immediately with a full backup. Device changes remain pending until Save device.');library_hint.setWordWrap(True);layout.addWidget(library_hint)
        self.apply_button=buttons(layout,'Apply suggestion',self.use,self.reject);self.apply_button.setEnabled(False)
        self.confirm.toggled.connect(self.ready);self.list.currentRowChanged.connect(self.preview_profile);self.reload();apply(self)
    def reload(self):
        self.rows=self.store.list(self.window.inputs['manufacturer'].text(),self.window.inputs['model'].text());self.list.clear()
        for row in self.rows:
            item=QListWidgetItem(row['manufacturer']+' / '+row['model']+' / '+row['variant']);item.setData(Qt.UserRole,row);self.list.addItem(item)
        if not self.rows:self.preview.setPlainText(tr('No reviewed model profile matches. You can save sourced current values as a reusable profile.'))
        self.confirm.setChecked(False);self.ready()
    def current(self):return self.list.currentItem().data(Qt.UserRole) if self.list.currentItem() else None
    def preview_profile(self,*_):
        row=self.current();self.confirm.setChecked(False)
        if not row:return
        dates='\n'.join(tr(KINDS[r['kind']])+': '+r['date']+' / '+r['provider']+' / '+r['product']+' / '+r['version']+' / '+tr({'uncertain':'Uncertain','user_reported':'User reported','verified':'Verified'}[r['status']])+'\n'+r['applicability']+' / '+r['observed_on']+' / '+', '.join(r['sources'])+'\n'+r['note'] for r in row['lifecycle'])
        self.preview.setPlainText(tr('Group')+': '+(row['group_name'] or tr('Unknown'))+'\n'+tr('Device type')+': '+(row['device_type'] or tr('Unknown'))+'\n'+tr('Roles')+': '+', '.join(row['roles'])+'\n'+dates+'\n'+row['note']+'\n'+tr('Source IDs')+': '+', '.join(row['sources']));self.ready()
    def ready(self,*_):self.apply_button.setEnabled(self.current() is not None and self.confirm.isChecked())
    def use(self):
        if self.current() is not None and self.confirm.isChecked():self.applied=copy.deepcopy(self.current());self.accept()
    def save_profile(self):
        w=self.window;selected=self.current()
        variant,ok=QInputDialog.getText(self,tr('Model applicability'),tr('Variant / region / hardware revision'),text=selected['variant'] if selected else '')
        if not ok:return
        note,ok=QInputDialog.getText(self,tr('Model evidence'),tr('Describe the evidence and applicability'),text=selected['note'] if selected else '')
        if not ok:return
        try:
            records=[r for r in w.lifecycle_panel.value() if r['kind']!='warranty_expiry']
            data=dict(manufacturer=w.inputs['manufacturer'].text(),model=w.inputs['model'].text(),variant=variant,device_type=w.inputs['device_type'].currentData(),roles=list(w.role_values),lifecycle=records,sources=w.source_selectors['device'].value(),note=note)
            if selected and variant==selected['variant']:
                if QMessageBox.question(self,tr('Revise model profile'),tr('Save a new immutable revision? Existing devices will not be changed.'),QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)!=QMessageBox.Yes:return
                original=selected
            else:original=None
            self.store.save(data,original);self.reload()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,tr('Could not save'),tr(str(exc)))
