#!/usr/bin/env python3
"""Offline hardware inventory desktop editor. Launch: python3 desktop.py"""
import argparse
from pathlib import Path
import datetime as dt
import sqlite3
import sys
import os
import json
import uuid
import re
try:
    from PySide6.QtCore import QDate, Qt, QSize, QUrl, QTimer, QProcess, Signal
    from PySide6.QtGui import QIcon, QPixmap, QImageReader, QActionGroup, QAction, QDesktopServices
    from PySide6.QtWidgets import (QApplication,QMainWindow,QWidget,QVBoxLayout,QHBoxLayout,
        QFormLayout,QLineEdit,QComboBox,QCheckBox,QDateEdit,QTableWidget,QTableWidgetItem,
        QPushButton,QLabel,QMessageBox,QSplitter,QAbstractItemView,QScrollArea,QListWidget,QListWidgetItem,QFileDialog,QDialog,QDialogButtonBox,QGroupBox,QToolButton)
except ImportError:
    raise SystemExit('PySide6 is required. On Arch Linux install python-pyside6; see GUIDE.en.md.')
from device_store import DeviceStore, DATES
from source_store import SourceStore,SCOPES
from source_ui import SourceSelector
from photo_store import PhotoStore
from manual_store import ManualStore,manual_path,validate_url
from photo_files import managed_path, backup_bundle
from connectivity import empty_profile,missing_sources
from software import empty_software
from network_identity import empty_network,missing_source as missing_network_source
from ui_i18n import tr,apply,install,read_language,write_language,LANGUAGES,APP_VERSION,RELEASE_DATE,localized
from ui_help import FIELDS as FIELD_HELP,TIPS,BUTTONS
import html
import platform
import PySide6

from search_combo import SearchComboBox
from list_view import DeviceListController,ChoiceDialog
from lifecycle_ui import LifecyclePanel,ModelDialog
from lifecycle import ModelStore,warnings as lifecycle_warnings
from location_ui import LocationPanel
from location_store import empty_location,location_summary

class CollapsibleSection(QWidget):
    def __init__(self,title,body):
        super().__init__();layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        self.header=QToolButton();self.header.setText(title);self.header.setCheckable(True)
        self.header.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        self.header.setSizePolicy(body.sizePolicy().horizontalPolicy(),body.sizePolicy().verticalPolicy())
        self.body=body;body.setTitle('');layout.addWidget(self.header);layout.addWidget(body)
        self.header.toggled.connect(self.expand);self.expand(False)
    def expand(self,expanded):
        self.header.setArrowType(Qt.DownArrow if expanded else Qt.RightArrow);self.body.setVisible(expanded)

class TypeDialog(QDialog):
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.original=None
        self.setWindowTitle('Manage device types');self.resize(540,520)
        layout=QVBoxLayout(self)
        note=QLabel('Add types or rename/move an existing type. Changes apply to every device using that type. Names are stored in lowercase.');note.setWordWrap(True);layout.addWidget(note)
        self.rows=store.types();self.list=QListWidget()
        for row in self.rows:self.list.addItem(row['group_name']+' / '+row['type_name'])
        self.list.currentRowChanged.connect(self.select);layout.addWidget(self.list)
        form=QFormLayout();self.name=QLineEdit();self.name.setToolTip(TIPS['type_name']);self.group=QComboBox();self.group.setEditable(True);self.group.setToolTip(TIPS['manage_group']);self.group.addItems(store.groups())
        form.addRow('Type name *',self.name);form.addRow('Group *',self.group);self.code=QLineEdit();self.code.setMaxLength(2);self.code.setPlaceholderText('Two-letter code; automatic if blank');form.addRow('Type code',self.code);layout.addLayout(form)
        controls=QHBoxLayout()
        new=QPushButton('New type');new.clicked.connect(self.new);controls.addWidget(new)
        save=QPushButton('Save type');save.clicked.connect(self.save);controls.addWidget(save)
        close=QPushButton('Close');close.clicked.connect(self.reject);controls.addWidget(close);layout.addLayout(controls)
        self.new()
    def select(self,n):
        if n<0:return
        self.original=self.rows[n];self.name.setText(self.original['type_name']);self.group.setCurrentText(self.original['group_name']);self.code.setText(self.original['prefix']);self.code.setReadOnly(True)
    def new(self):
        self.list.setCurrentRow(-1);self.original=None;self.name.clear();self.group.setCurrentText('');self.code.clear();self.code.setReadOnly(False);self.name.setFocus()
    def save(self):
        if self.original is not None and QMessageBox.question(self,'Update shared type','Rename or move this type for all devices that use it?',QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)!=QMessageBox.Yes:return
        try:self.store.save_type(self.name.text(),self.group.currentText(),self.original,prefix=self.code.text());self.accept()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,'Could not save type',str(exc))

class OptionalDate(QWidget):
    def __init__(self):
        super().__init__()
        self.known=QCheckBox('Known');self.known.setToolTip(TIPS['date'])
        self.editor=QDateEdit(QDate.currentDate())
        self.editor.setCalendarPopup(True);self.editor.setToolTip(TIPS['date'])
        self.editor.setDisplayFormat('yyyy-MM-dd')
        self.editor.setDateRange(QDate(1,1,1),QDate(9999,12,31))
        self.editor.setEnabled(False)
        self.known.toggled.connect(self.editor.setEnabled)
        layout=QHBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        layout.addWidget(self.known);layout.addWidget(self.editor,1)
    def value(self):
        return self.editor.date().toString('yyyy-MM-dd') if self.known.isChecked() else None
    def load(self,value):
        self.known.setChecked(value is not None)
        self.editor.setDate(QDate.fromString(value,'yyyy-MM-dd') if value else QDate.currentDate())

class ConnectionPanel(QGroupBox):
    def __init__(self,title,options):
        super().__init__(title);self.loading=False
        form=QFormLayout(self)
        self.supported=QComboBox();self.usage=QComboBox()
        for combo in (self.supported,self.usage):
            for value,label in (('unknown','unknown'),('none','none'),('recorded','recorded below')):combo.addItem(label,value)
        form.addRow('Supported capabilities',self.supported);form.addRow('Currently in use',self.usage)
        self.table=QTableWidget(0,3);self.table.setHorizontalHeaderLabels(['Choice','Supported','In use'])
        self.table.horizontalHeader().setStretchLastSection(True);self.table.setMinimumHeight(180);self.table.setMaximumHeight(230)
        form.addRow(self.table)
        self.source=QLineEdit();self.source.setPlaceholderText('Recommended source; missing information warns but does not block saving')
        form.addRow('Information source',self.source);self.assessed=OptionalDate();form.addRow('Assessment date',self.assessed)
        self.warning=QLabel();self.warning.setWordWrap(True);self.warning.setStyleSheet('color:#ad5b00');form.addRow(self.warning)
        self.source.textChanged.connect(self.update_warning)
        hint=QLabel('Choose recorded below to tick multiple choices. In use implies supported. Recorded choices need not be an exhaustive capability list.');hint.setWordWrap(True);form.addRow(hint)
        self.supported.currentIndexChanged.connect(lambda:self.status_changed('supported'))
        self.usage.currentIndexChanged.connect(lambda:self.status_changed('usage'))
        self.table.itemChanged.connect(self.choice_changed);self.set_options(options)
    def set_options(self,options):
        self.loading=True;self.options=options;self.table.setRowCount(len(options))
        for n,value in enumerate(options):
            item=QTableWidgetItem(value);item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable);self.table.setItem(n,0,item)
            for col in (1,2):
                item=QTableWidgetItem();item.setFlags(Qt.ItemIsUserCheckable|Qt.ItemIsEnabled);item.setCheckState(Qt.Unchecked);self.table.setItem(n,col,item)
        self.table.resizeColumnsToContents();self.loading=False;self.update_enabled()
    def update_enabled(self):
        self.loading=True
        for n in range(len(self.options)):
            for col,combo in ((1,self.supported),(2,self.usage)):
                flags=Qt.ItemIsUserCheckable
                if combo.currentData()=='recorded':flags|=Qt.ItemIsEnabled
                self.table.item(n,col).setFlags(flags)
        self.loading=False;self.update_warning()
    def update_warning(self):
        missing=(self.supported.currentData(),self.usage.currentData())!=('unknown','unknown') and not self.source.text().strip() and not (hasattr(self,'source_selector') and self.source_selector.value())
        self.warning.setText('Warning: connectivity source is missing. Saving is allowed.' if missing else '');apply(self.warning)
    def status_changed(self,which):
        if self.loading:return
        self.loading=True
        if which=='supported' and self.supported.currentData()!='recorded':
            for n in range(len(self.options)):
                self.table.item(n,1).setCheckState(Qt.Unchecked);self.table.item(n,2).setCheckState(Qt.Unchecked)
            if self.supported.currentData()=='none':self.usage.setCurrentIndex(self.usage.findData('none'))
            elif self.usage.currentData()=='recorded':self.usage.setCurrentIndex(self.usage.findData('unknown'))
        if which=='usage':
            if self.usage.currentData()=='recorded':self.supported.setCurrentIndex(self.supported.findData('recorded'))
            else:
                for n in range(len(self.options)):self.table.item(n,2).setCheckState(Qt.Unchecked)
                if self.supported.currentData()=='none' and self.usage.currentData()!='none':self.supported.setCurrentIndex(self.supported.findData('unknown'))
        self.loading=False;self.update_enabled()
    def choice_changed(self,item):
        if self.loading or item.column()==0:return
        self.loading=True;n=item.row()
        if item.column()==2 and item.checkState()==Qt.Checked:self.table.item(n,1).setCheckState(Qt.Checked)
        if item.column()==1 and item.checkState()!=Qt.Checked:self.table.item(n,2).setCheckState(Qt.Unchecked)
        self.loading=False
    def value(self):
        return {'supported_status':self.supported.currentData(),'usage_status':self.usage.currentData(),
                'supported':sorted(self.options[n] for n in range(len(self.options)) if self.table.item(n,1).checkState()==Qt.Checked),
                'in_use':sorted(self.options[n] for n in range(len(self.options)) if self.table.item(n,2).checkState()==Qt.Checked),
                'source':self.source.text().strip() or None,'assessed_on':self.assessed.value()}
    def load(self,value):
        self.loading=True
        self.supported.setCurrentIndex(self.supported.findData(value['supported_status']));self.usage.setCurrentIndex(self.usage.findData(value['usage_status']))
        self.source.setText(value['source'] or '');self.assessed.load(value['assessed_on'])
        for n,choice in enumerate(self.options):
            self.table.item(n,1).setCheckState(Qt.Checked if choice in value['supported'] else Qt.Unchecked)
            self.table.item(n,2).setCheckState(Qt.Checked if choice in value['in_use'] else Qt.Unchecked)
        self.loading=False;self.update_enabled()

class ConnectionDialog(QDialog):
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.original=None
        self.setWindowTitle('Manage connection choices');self.resize(500,450)
        layout=QVBoxLayout(self);self.kind=QComboBox();self.kind.addItem('Connection interfaces','interface');self.kind.addItem('Communication protocols','protocol');layout.addWidget(self.kind)
        self.list=QListWidget();layout.addWidget(self.list);self.name=QLineEdit();self.name.setPlaceholderText('Lowercase choice name');self.name.setToolTip(TIPS['manage_connections']);layout.addWidget(self.name)
        note=QLabel('Renaming a shared choice updates every device using it. No interface-to-protocol compatibility is inferred.');note.setWordWrap(True);layout.addWidget(note)
        buttons=QHBoxLayout()
        for label,callback in [('New choice',self.new),('Save choice',self.save),('Close',self.reject)]:
            button=QPushButton(label);button.clicked.connect(callback);buttons.addWidget(button)
        layout.addLayout(buttons);self.kind.currentIndexChanged.connect(self.reload);self.list.currentRowChanged.connect(self.select);self.reload()
    def reload(self):
        self.list.blockSignals(True);self.list.clear();self.rows=self.store.connection_options(self.kind.currentData());self.list.addItems(self.rows);self.list.blockSignals(False);self.new()
    def new(self):self.list.setCurrentRow(-1);self.original=None;self.name.clear()
    def select(self,n):
        if n>=0:self.original=self.rows[n];self.name.setText(self.original)
    def save(self):
        if self.original is not None and QMessageBox.question(self,'Rename shared choice','Update this choice for every assigned device?',QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)!=QMessageBox.Yes:return
        try:self.store.save_connection_option(self.kind.currentData(),self.name.text(),self.original);self.accept()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,'Could not save choice',str(exc))

class NetworkPanel(QGroupBox):
    def __init__(self):
        super().__init__('Network identity');form=QFormLayout(self);form.setRowWrapPolicy(QFormLayout.WrapLongRows);form.setLabelAlignment(Qt.AlignLeft)
        self.hostname=QLineEdit();self.hostname.setPlaceholderText('Unknown, or actual hostname / FQDN')
        self.hostname.setToolTip('Separate from the descriptive inventory name. DNS labels use letters, digits and hyphens; IDNs are stored as ASCII IDNA. No DNS lookup is performed.')
        form.addRow('Hostname',self.hostname)
        self.table=QTableWidget(0,3);self.table.setHorizontalHeaderLabels(['Interface / port','MAC address','IP addresses'])
        self.table.setMinimumHeight(160);self.table.setMaximumHeight(250);self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setToolTip('One row per interface, for example igc0 or WAN. MAC may be unknown. Enter multiple IPv4/IPv6 addresses separated by commas; optional /prefix is allowed. Same IP on different interfaces is allowed.')
        form.addRow(self.table)
        actions=QHBoxLayout();add=QPushButton('Add interface');add.clicked.connect(lambda:self.add_row());actions.addWidget(add)
        remove=QPushButton('Remove interface');remove.clicked.connect(self.remove_row);actions.addWidget(remove);form.addRow(actions)
        self.source=QLineEdit();self.source.setPlaceholderText('Recommended: device settings or your observation')
        form.addRow('Information source',self.source)
        self.observed=OptionalDate();form.addRow('Observed on',self.observed)
        self.evidence=QComboBox()
        for value in ('user_reported','verified','uncertain'):self.evidence.addItem(value,value)
        self.evidence.setToolTip('Verified means you checked the actual values; it requires a source and observation date. Saving does not independently verify the device.')
        form.addRow('Evidence status',self.evidence)
        hint=QLabel('Optional values stay unknown. Network edits save with Save device; previous saved assessments remain in the observation history.');hint.setWordWrap(True);form.addRow(hint)
        self.warning=QLabel();self.warning.setWordWrap(True);self.warning.setStyleSheet('color:#ad5b00');form.addRow(self.warning)
        self.hostname.textChanged.connect(self.update_warning);self.source.textChanged.connect(self.update_warning)
        self.table.itemChanged.connect(lambda *_:self.update_warning())
        self.table.itemChanged.connect(lambda item:self.table.resizeColumnToContents(1) if item.column()==1 else None)
        for row in range(form.rowCount()):
            item=form.itemAt(row,QFormLayout.LabelRole)
            if item and item.widget():item.widget().setWordWrap(True);item.widget().setAlignment(Qt.AlignLeft|Qt.AlignVCenter)
    def add_row(self,row=None):
        row=row or {};n=self.table.rowCount();self.table.insertRow(n)
        for col,key in enumerate(('label','mac_address','addresses')):
            value=', '.join(row.get(key,[])) if key=='addresses' else row.get(key) or ''
            item=QTableWidgetItem(value)
            if col==0:item.setData(Qt.UserRole,row.get('interface_id') or uuid.uuid4().hex)
            self.table.setItem(n,col,item)
        self.update_warning()
    def remove_row(self):
        n=self.table.currentRow()
        if n>=0:self.table.removeRow(n);self.update_warning()
    def value(self):
        rows=[]
        for n in range(self.table.rowCount()):
            text=lambda col:self.table.item(n,col).text() if self.table.item(n,col) else ''
            rows.append(dict(interface_id=self.table.item(n,0).data(Qt.UserRole),label=text(0),mac_address=text(1).strip() or None,addresses=[v for v in re.split(r'[,;\s]+',text(2).strip()) if v]))
        return dict(hostname=self.hostname.text().strip() or None,interfaces=rows,source=self.source.text().strip() or None,observed_on=self.observed.value(),evidence_status=self.evidence.currentData())
    def load(self,data):
        self.table.setRowCount(0);self.hostname.setText(data['hostname'] or '');self.source.setText(data['source'] or '')
        self.observed.load(data['observed_on']);self.evidence.setCurrentIndex(max(0,self.evidence.findData(data['evidence_status'])))
        for row in data['interfaces']:self.add_row(row)
        self.table.resizeColumnsToContents();self.update_warning()
    def update_warning(self):
        missing=(self.hostname.text().strip() or self.table.rowCount()) and not self.source.text().strip() and not (hasattr(self,'source_selector') and self.source_selector.value())
        self.warning.setText('Warning: network information source is missing. Saving unverified details is allowed.' if missing else '');apply(self.warning)

class SoftwarePanel(QGroupBox):
    def __init__(self,families):
        super().__init__('Software');self.loading=False;form=QFormLayout(self)
        self.os_status=QComboBox();self.firmware_status=QComboBox()
        for combo in (self.os_status,self.firmware_status):
            for value,label in (('unknown','unknown'),('not_applicable','not applicable'),('recorded','recorded')):combo.addItem(label,value)
        self.family=QComboBox();self.family.addItem('Unknown',None)
        for value in families:self.family.addItem(value,value)
        self.name=QLineEdit();self.name.setPlaceholderText('For example: arch linux, debian or proxmox ve')
        self.version=QLineEdit();self.version.setPlaceholderText('Exact installed version, if known')
        self.firmware=QLineEdit();self.firmware.setPlaceholderText('Exact installed firmware version, if known')
        self.source=QLineEdit();self.source.setPlaceholderText('For example: system settings, command output or management interface')
        self.checked=OptionalDate()
        for label,field in (('Operating system',self.os_status),('OS family',self.family),('OS name / distribution',self.name),('OS version',self.version),('Firmware',self.firmware_status),('Firmware version',self.firmware),('Information source',self.source),('Checked on',self.checked)):form.addRow(label,field)
        note=QLabel('One current OS per device. Unknown is different from not applicable. Firmware can be recorded independently.');note.setWordWrap(True);form.addRow(note)
        version_help=QPushButton('Find installed versions…');version_help.clicked.connect(self.show_version_help);form.addRow(version_help)
        self.os_status.currentIndexChanged.connect(self.status_changed);self.firmware_status.currentIndexChanged.connect(self.status_changed)
        self.os_status.setToolTip(TIPS['software_status']);self.firmware_status.setToolTip(TIPS['software_status'])
        self.family.setToolTip(TIPS['os_family']);self.name.setToolTip(TIPS['os_name']);self.version.setToolTip(TIPS['os_version']);self.firmware.setToolTip(TIPS['firmware_version'])
        self.source.setToolTip(TIPS['software_source']);self.checked.setToolTip(TIPS['date'])
        self.load(empty_software())
    def show_version_help(self):
        QMessageBox.information(self,'Installed OS and firmware versions',tr('For pfSense, open Dashboard → System Information: Version shows pfSense and its underlying FreeBSD version. BIOS may show the installed BIOS vendor/version/date. If absent, read it in BIOS setup. Choose Firmware: recorded to enter the exact installed BIOS/UEFI version. A manufacturer download is not proof of the installed version. SSD firmware needs a reading from that disk. Leave unavailable values unknown.'))
    def status_changed(self,*_):
        if self.loading:return
        self.loading=True
        known=self.os_status.currentData()=='recorded'
        for widget in (self.family,self.name,self.version):widget.setEnabled(known)
        if not known:self.family.setCurrentIndex(0);self.name.clear();self.version.clear()
        known=self.firmware_status.currentData()=='recorded';self.firmware.setEnabled(known)
        if not known:self.firmware.clear()
        self.loading=False
    def value(self):
        return {'os_status':self.os_status.currentData(),'os_family':self.family.currentData(),
                'os_name':self.name.text().strip() or None,'os_version':self.version.text().strip() or None,
                'firmware_status':self.firmware_status.currentData(),'firmware_version':self.firmware.text().strip() or None,
                'source':self.source.text().strip() or None,'checked_on':self.checked.value()}
    def load(self,value):
        self.loading=True
        self.os_status.setCurrentIndex(self.os_status.findData(value['os_status']));self.firmware_status.setCurrentIndex(self.firmware_status.findData(value['firmware_status']))
        self.family.setCurrentIndex(max(0,self.family.findData(value['os_family'])))
        self.name.setText(value['os_name'] or '');self.version.setText(value['os_version'] or '');self.firmware.setText(value['firmware_version'] or '')
        self.source.setText(value['source'] or '');self.checked.load(value['checked_on'])
        self.loading=False;self.status_changed()

class ManualDialog(QDialog):
    def __init__(self,store,device,original=None,parent=None):
        super().__init__(parent);self.store=store;self.device=device;self.original=original
        self.setWindowTitle('Edit manual reference' if original else 'Add manual reference');self.resize(640,470)
        form=QFormLayout(self);self.inputs={}
        self.kind=QComboBox();self.kind.addItem('Online link','online');self.kind.addItem('Local PDF','local');form.addRow('Reference kind',self.kind)
        for key,label in (('title','Title *'),('url','Online URL'),('language','Language code'),('edition','Edition / version'),('applicable_model','Applicable model'),('source','Information source / notes'),('notes','Notes')):
            field=QLineEdit();self.inputs[key]=field;form.addRow(label,field)
        self.file=QLineEdit();self.file.setReadOnly(True);self.choose=QPushButton('Choose PDF…');self.choose.clicked.connect(self.choose_file)
        files=QHBoxLayout();files.addWidget(self.file,1);files.addWidget(self.choose);form.addRow('Local file',files)
        self.inputs['url'].setPlaceholderText('https://manufacturer.example/manual.pdf')
        self.inputs['language'].setPlaceholderText('en, de, hu, fr…; leave blank if unknown')
        self.inputs['edition'].setPlaceholderText('Exact document edition or version, if known')
        self.inputs['applicable_model'].setPlaceholderText('Model(s) this document applies to, if known')
        self.inputs['source'].setPlaceholderText('For example: manufacturer website or document supplied with the device')
        for key,field in self.inputs.items():field.setToolTip(TIPS['manual_'+key])
        self.file.setToolTip(TIPS['manual_file']);self.choose.setToolTip(TIPS['manual_file']);self.kind.setToolTip(TIPS['manual_kind'])
        note=QLabel('References save immediately. Online links are opened only on request; no document is downloaded automatically. Local PDFs are copied into managed storage.');note.setWordWrap(True);form.addRow(note)
        controls=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);controls.accepted.connect(self.save);controls.rejected.connect(self.reject);form.addRow(controls)
        self.kind.currentIndexChanged.connect(self.update_kind)
        if original:
            self.kind.setCurrentIndex(self.kind.findData(original['kind']));self.kind.setEnabled(False)
            for key,field in self.inputs.items():field.setText(original.get(key) or '')
            self.file.setText(original['original_name'] or '');self.file.setToolTip(original['relative_path'] or TIPS['manual_file']);self.choose.setEnabled(False)
        self.update_kind()
    def update_kind(self,*_):
        online=self.kind.currentData()=='online';self.inputs['url'].setEnabled(online)
        self.file.setEnabled(not online);self.choose.setEnabled(not online and self.original is None)
    def choose_file(self):
        path,_=QFileDialog.getOpenFileName(self,'Choose local manual','','PDF documents (*.pdf)')
        if path:self.file.setText(path)
    def save(self):
        data={key:field.text() for key,field in self.inputs.items() if key!='url'}
        location=self.inputs['url'].text() if self.kind.currentData()=='online' else self.file.text()
        try:self.store.save(self.device,self.kind.currentData(),data,location,self.original);self.accept()
        except (ValueError,OSError,sqlite3.Error) as exc:QMessageBox.warning(self,'Could not save manual reference',str(exc))

class Window(QMainWindow):
    device_changed=Signal(str)
    def __init__(self,store,language=None,editor_owner=None):
        super().__init__(editor_owner);self.editor_owner=editor_owner;self.editors={};self.bound_device_id=None;self.skip_close_prompt=False;
        if editor_owner is not None:self.setWindowFlag(Qt.Window,True)
        install(language or read_language(store.path.parent));self.store=store;self.source_store=SourceStore(store.path);self.source_selectors={};self.photo_store=PhotoStore(store.path);self.manual_store=ManualStore(store.path);self.original=None;self.baseline=None;self.loading=False
        self.type_rows=store.types()
        self.build_menus()
        self.setWindowTitle('HWI4U TEST' if os.environ.get('INVENTORY_CHANNEL')=='test' else 'HWI4U');self.resize(1180,760)
        root=QWidget();outer=QVBoxLayout(root);outer.setContentsMargins(20,20,20,20);outer.setSpacing(12)
        title=QLabel('HWI4U TEST' if os.environ.get('INVENTORY_CHANNEL')=='test' else 'HWI4U');title.setStyleSheet('font-size: 24px; font-weight: 600;')
        self.header_title=title;heading=QHBoxLayout();heading.addWidget(title,1)
        self.client_button=QPushButton('Open production client' if os.environ.get('INVENTORY_CHANNEL')=='test' else 'Open test client')
        self.client_button.setToolTip('Open the other client in a separate window. Unsaved edits stay in this window; no data is copied.')
        self.client_button.clicked.connect(self.open_other_client);heading.addWidget(self.client_button)
        self.connections_button=QPushButton('Network connections…');self.connections_button.clicked.connect(self.manage_network_links);heading.addWidget(self.connections_button);outer.addLayout(heading)
        subtitle=QLabel('hardware inventory database client');self.subtitle=subtitle;outer.addWidget(subtitle)
        if os.environ.get('INVENTORY_CHANNEL')=='test':
            banner=QLabel('TEST ENVIRONMENT — changes affect only the test copy.');banner.setStyleSheet('background:#ffd166;color:#332600;padding:10px;font-weight:bold;');outer.addWidget(banner)
        self.search=QLineEdit();self.search.setPlaceholderText('Search devices, software, interfaces or protocols…')
        toolbar=QHBoxLayout();toolbar.addWidget(self.search,1);self.toolbar_buttons={}
        for label,callback in [('New device',self.new),('Save device',self.save),('Delete device…',self.delete_device),('Refresh',self.refresh),('Full backup',self.full_backup),('Manage types',self.manage_types)]:
            button=QPushButton(label);button.clicked.connect(callback);toolbar.addWidget(button);self.toolbar_buttons[label]=button
        self.update_button=QPushButton('Apply update');self.update_button.setToolTip('Save or discard edits, then restart into the tested update. A database write lock defers migration.');self.update_button.hide();self.update_button.clicked.connect(self.apply_update);toolbar.addWidget(self.update_button)
        outer.addLayout(toolbar)
        self.filter_bar=QWidget();filters=QHBoxLayout(self.filter_bar);filters.setContentsMargins(0,0,0,0);filters.addWidget(QLabel('Filter group'))
        self.group_filter=SearchComboBox();self.group_filter.addItem('All groups',None);self.group_filter.addItem('Unknown','__unknown__')
        for group in store.groups():self.group_filter.addItem(group,group)
        filters.addWidget(self.group_filter);filters.addWidget(QLabel('Type'))
        self.type_filter=SearchComboBox();filters.addWidget(self.type_filter,1);outer.addWidget(self.filter_bar)
        split=QSplitter();self.splitter=split;outer.addWidget(split,1)
        self.table=QTableWidget(0,6);self.table.setHorizontalHeaderLabels(['Short ID','Name','Group','Type','State','Condition'])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows);self.table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers);self.table.horizontalHeader().setStretchLastSection(True)
        split.addWidget(self.table)
        scroll=QScrollArea();self.form_scroll=scroll;scroll.setWidgetResizable(True);panel=QWidget();form=QFormLayout(panel);form.setContentsMargins(20,12,12,12);form.setSpacing(14)
        self.form_title=QLabel('New device');self.form_title.setStyleSheet('font-size:18px;font-weight:600;');form.addRow(self.form_title)
        self.inputs={}
        for key,label in [('device_id','Device ID *'),('name','Name *'),('manufacturer','Manufacturer'),('model','Model'),('serial_number','Serial number'),('location','Location text / additional description'),('source','Information source / notes (or selected sources) *')]:
            widget=QLineEdit();self.inputs[key]=widget;form.addRow(label,widget)
            if key=='name':self.name_feedback=QLabel();self.name_feedback.setWordWrap(True);form.addRow(self.name_feedback)
        self.location_panel=LocationPanel(store);form.addRow(self.location_panel)
        sources_group=QGroupBox('Device evidence * — text above or sources below');sources_layout=QVBoxLayout(sources_group)
        self.source_selectors['device']=SourceSelector(self.source_store,OptionalDate);sources_layout.addWidget(self.source_selectors['device']);form.addRow(sources_group)
        self.evidence_feedback=QLabel();self.evidence_feedback.setWordWrap(True);sources_layout.addWidget(self.evidence_feedback)
        self.inputs['source'].textChanged.connect(self.check_device_evidence)
        self.source_selectors['device'].changed.connect(self.check_device_evidence)
        self.inputs['device_id'].setPlaceholderText('Generated automatically when saved')
        self.short_id=QLineEdit();self.short_id.setReadOnly(True);self.short_id.setPlaceholderText('Generated automatically when saved');form.insertRow(1,'Short ID',self.short_id)
        self.short_id.setToolTip('Two-letter type code and five random digits. Reclassification gives a new label; old labels still resolve to this full ID.')
        self.inputs['name'].setPlaceholderText('Example: backup-server-office-01')
        self.inputs['location'].setToolTip('Optional physical location, for example building / room / rack / shelf. Unicode allowed; maximum 200 characters. Leave unknown blank. This is not a network address or purchased-at value.')
        self.inputs['source'].setPlaceholderText('For example: device label or invoice filename')
        self.type_group=QComboBox();self.type_group.addItem('Unknown / choose a type',None)
        for group in store.groups():self.type_group.addItem(group,group)
        form.addRow('Type group',self.type_group)
        self.inputs['device_type']=QComboBox();form.addRow('Device type',self.inputs['device_type'])
        self.type_group.currentIndexChanged.connect(self.group_changed)
        self.inputs['device_type'].currentIndexChanged.connect(self.type_changed)
        self.fill_types(None)
        for key,label in [('purchase_date','Purchase date'),('installation_date','Installation date'),('scrapped_date','Scrapped date')]:
            self.inputs[key]=OptionalDate();form.addRow(label,self.inputs[key])
        self.inputs['purchased_at']=QLineEdit();form.addRow('Purchased at',self.inputs['purchased_at'])
        self.inputs['purchased_at'].setToolTip('Shop, marketplace or seller. Optional text; spelling suggestions never change it automatically.')
        self.merchant_hint=QLabel();form.addRow(self.merchant_hint)
        self.merchant_fix=QPushButton('Use suggested spelling');form.addRow(self.merchant_fix);self.merchant_fix.hide()
        self.merchant_fix.clicked.connect(self.apply_merchant_suggestion)
        self.inputs['purchased_at'].textChanged.connect(self.check_merchant)
        self.inputs['purchase_price']=QLineEdit();self.inputs['purchase_price'].setPlaceholderText('Unknown — or amount such as 129.90')
        form.addRow('Purchase price',self.inputs['purchase_price'])
        currency=QComboBox();currency.setEditable(True);currency.addItem('')
        currency.addItems(['EUR','HUF','USD','GBP','CHF','CAD','AUD','JPY']);currency.setToolTip('Choose a currency or type a three-letter uppercase code. Blank means unknown.')
        self.inputs['purchase_currency']=currency;form.addRow('Currency',currency)
        for key,label,table in [('current_state','Current state','device_states'),('physical_condition','Physical condition','physical_conditions')]:
            widget=QComboBox();widget.addItem('Unknown',None)
            for value in store.choices(table):widget.addItem(value,value)
            self.inputs[key]=widget;form.addRow(label,widget)
        self.role_values=[];self.role_button=QPushButton();self.role_button.setProperty('_literal_text',True);self.role_button.clicked.connect(self.choose_roles);form.addRow('Roles',self.role_button)
        self.model_button=QPushButton('Model suggestions…');self.model_button.clicked.connect(self.model_suggestions);self.model_button.setToolTip('Review exact manufacturer/model matches or save a sourced reusable model profile. No classification is changed automatically.');form.addRow(self.model_button)
        self.lifecycle_panel=LifecyclePanel(store,self.source_store,OptionalDate,lambda:self.inputs['manufacturer'].text(),lambda:self.inputs['model'].text(),lambda:self.inputs['purchase_date'].value());form.addRow(self.lifecycle_panel)
        for key in ('manufacturer','model'):self.inputs[key].textChanged.connect(self.lifecycle_panel.update_warning)
        self.inputs['purchase_date'].known.toggled.connect(self.lifecycle_panel.update_warning);self.inputs['purchase_date'].editor.dateChanged.connect(self.lifecycle_panel.update_warning)
        self.sections=[]
        self.network_panel=NetworkPanel();self.network_section=CollapsibleSection('Network identity',self.network_panel);self.sections.append(self.network_section);form.addRow(self.network_section)
        self.software_panel=SoftwarePanel(store.os_families());section=CollapsibleSection('Software',self.software_panel);self.sections.append(section);form.addRow(section)
        self.connection_panels={}
        manage=QPushButton('Manage connection choices…');manage.clicked.connect(self.manage_connections);form.addRow(manage)
        for kind,title in (('interface','Connection interfaces'),('protocol','Communication protocols')):
            panel_widget=ConnectionPanel(title,store.connection_options(kind));self.connection_panels[kind]=panel_widget;section=CollapsibleSection(title,panel_widget);self.sections.append(section);form.addRow(section)
        for scope,assessment in [('software',self.software_panel),('network',self.network_panel),*self.connection_panels.items()]:
            selector=SourceSelector(self.source_store,OptionalDate);self.source_selectors[scope]=selector;assessment.layout().addRow('Sources and evidence',selector);assessment.source_selector=selector
            if hasattr(assessment,'update_warning'):selector.changed.connect(assessment.update_warning)
        note=QLabel('Uncheck Known to keep a date unknown. No date is saved automatically.\n* Required fields. Group follows the selected type; choose a type to save a classification.\nExisting IDs stay fixed; components and facts use the existing tool.');note.setWordWrap(True);form.addRow(note)
        buttons=QHBoxLayout();save=QPushButton('Save device');save.setDefault(True);save.clicked.connect(self.save)
        cancel=QPushButton('Cancel changes');cancel.clicked.connect(self.cancel)
        buttons.addWidget(save);buttons.addWidget(cancel);form.addRow(buttons)
        photo_title=QLabel('Device photos');photo_title.setStyleSheet('font-size:18px;font-weight:600;');form.addRow(photo_title)
        self.photo_hint=QLabel('Save a device before attaching photos.');self.photo_hint.setWordWrap(True);form.addRow(self.photo_hint)
        self.photo_list=QListWidget();self.photo_list.setIconSize(QSize(120,90));self.photo_list.setMinimumHeight(140);self.photo_list.setMaximumHeight(230)
        self.photo_list.itemDoubleClicked.connect(lambda item:self.open_photo());form.addRow(self.photo_list)
        photo_buttons=QHBoxLayout()
        self.add_photo_button=QPushButton('Add photo…');self.add_photo_button.clicked.connect(self.add_photo);photo_buttons.addWidget(self.add_photo_button)
        open_button=QPushButton('Open image');open_button.clicked.connect(self.open_photo);photo_buttons.addWidget(open_button)
        remove_button=QPushButton('Detach');remove_button.clicked.connect(self.detach_photo);photo_buttons.addWidget(remove_button)
        form.addRow(photo_buttons)
        manual_title=QLabel('Manuals and references');manual_title.setStyleSheet('font-size:18px;font-weight:600;');form.addRow(manual_title)
        self.manual_hint=QLabel('Save a device before adding references.');self.manual_hint.setWordWrap(True);form.addRow(self.manual_hint)
        self.manual_list=QListWidget();self.manual_list.setMinimumHeight(130);self.manual_list.setMaximumHeight(230);self.manual_list.setToolTip(TIPS['manual_list'])
        self.manual_list.itemDoubleClicked.connect(lambda item:self.open_manual());form.addRow(self.manual_list)
        actions=QHBoxLayout();self.add_manual_button=QPushButton('Add reference…');self.add_manual_button.clicked.connect(self.add_manual);actions.addWidget(self.add_manual_button)
        edit=QPushButton('Edit reference…');edit.clicked.connect(self.edit_manual);actions.addWidget(edit);form.addRow(actions)
        open_actions=QHBoxLayout()
        for label,callback in [('Open reference',self.open_manual),('Detach reference',self.detach_manual)]:
            button=QPushButton(label);button.clicked.connect(callback);open_actions.addWidget(button)
        form.addRow(open_actions)
        scroll.setWidget(panel);split.addWidget(scroll);split.setSizes([580,560])
        self.update_notice=QWidget();notice=QHBoxLayout(self.update_notice);notice.setContentsMargins(0,0,0,0)
        self.update_notice_text=QLabel('A tested local update is ready. Use Apply update when convenient.');self.update_notice_text.setWordWrap(True);notice.addWidget(self.update_notice_text,1)
        self.footer_apply=QPushButton('Apply update');self.footer_apply.setToolTip('Save or discard edits, then restart into the tested update. A database write lock defers migration.');self.footer_apply.clicked.connect(self.apply_update);notice.addWidget(self.footer_apply)
        self.footer_abort=QPushButton('Abort');self.footer_abort.setToolTip('Postpone this update. Keep the current client and all unsaved edits.');self.footer_abort.clicked.connect(self.abort_update);notice.addWidget(self.footer_abort)
        self.dismissed_update=None;self.ready_update=None;self.update_notice.hide();outer.addWidget(self.update_notice)
        self.status=QLabel();self.status.setWordWrap(True);outer.addWidget(self.status)
        path=QLabel(str(store.path));path.setTextInteractionFlags(Qt.TextSelectableByMouse);outer.addWidget(path)
        self.setCentralWidget(root)
        self.list_controller=DeviceListController(self)
        self.search.textChanged.connect(self.filter_rows);self.table.itemSelectionChanged.connect(self.select)
        self.table.itemDoubleClicked.connect(lambda item:self.open_device_editor(item.row()))
        self.table.setToolTip('Double-click a device to edit it in a large window. The quick editor remains available.')
        self.group_filter.currentIndexChanged.connect(self.filter_group_changed)
        self.type_filter.currentIndexChanged.connect(self.filter_rows)
        self.filter_group_changed();self.reload();self.load(None);self.install_help();apply(self)
        self.name_timer=QTimer(self);self.name_timer.setSingleShot(True);self.name_timer.setInterval(200);self.name_timer.timeout.connect(self.check_name);self.inputs['name'].textChanged.connect(lambda *_:self.name_timer.start())
        self.update_timer=QTimer(self);self.update_timer.setInterval(3000);self.update_timer.timeout.connect(self.check_update);self.update_timer.start();self.check_update()
        self.update_timer.timeout.connect(self.check_name)
        if os.environ.get('INVENTORY_UPDATE_ERROR'):self.status.setText(tr('Update deferred. Finish open database transactions, then retry Apply update.')+' '+os.environ['INVENTORY_UPDATE_ERROR'])

    def open_other_client(self):
        root=Path(os.environ.get('INVENTORY_PROJECT_ROOT',Path(__file__).resolve().parent))
        arguments=[str(root/'run_desktop.py')]
        if os.environ.get('INVENTORY_CHANNEL')!='test':arguments.append('test')
        opened,_pid=QProcess.startDetached(sys.executable,arguments,str(root))
        if not opened:
            QMessageBox.warning(self,tr('Could not open client'),tr('Could not open the other client.'));return
        self.status.setText(tr('The other client opened in a separate window. Unsaved changes remain here.'))

    def check_device_evidence(self):
        ready=bool(self.inputs['source'].text().strip() or self.source_selectors['device'].value())
        self.evidence_feedback.setText('Device evidence ready: text or selected sources supplied.' if ready else 'Required: enter device evidence text above OR choose at least one device source below.')
        apply(self.evidence_feedback)
        return ready

    def check_name(self):
        name=self.inputs['name'].text()
        if not name:self.name_feedback.clear();return
        try:issue=self.store.name_issue(name,self.original['device_id'] if self.original else None)
        except (OSError,sqlite3.Error,ValueError):issue='Name check is unavailable; Save will validate again.'
        self.name_feedback.setText(issue or 'No duplicate name found.')
        self.name_feedback.setStyleSheet('color:#ad5b00' if issue else 'color:#327447');apply(self.name_feedback)

    def check_update(self):
        root=os.environ.get('INVENTORY_PROJECT_ROOT');running=os.environ.get('INVENTORY_RELEASE_ID')
        if not root or not running:
            self.update_notice.hide();self.update_button.hide();return
        try:
            from update_runtime import channel_pointer
            pointer=json.loads(channel_pointer(root,os.environ.get('INVENTORY_CHANNEL','production')).read_text())
            self.ready_update=pointer['release_id'] if pointer['release_id']!=running else None
            self.update_button.setVisible(self.ready_update is not None)
            self.update_notice.setVisible(self.ready_update is not None and self.ready_update!=self.dismissed_update)
        except (OSError,ValueError,KeyError):return
    def abort_update(self):
        self.dismissed_update=self.ready_update;self.update_notice.hide()
        self.status.setText(tr('Update postponed. Your unsaved changes are kept.'))

    def show_update_status(self):
        self.dismissed_update=None
        self.check_update()
        if not os.environ.get('INVENTORY_RELEASE_ID'):
            self.status.setText(tr('Use launch-desktop.sh for managed updates.'))
        elif self.update_button.isHidden():self.status.setText(tr('No newer published local release.'))
        else:self.status.clear()
    def apply_update(self):
        from update_runtime import UPDATE_EXIT
        if not os.environ.get('INVENTORY_RELEASE_ID'):return
        if QApplication.activeModalWidget() is not None:
            QMessageBox.information(self,'Finish the current dialog','Save or cancel the open dialog before applying the update.');return
        if not self.editor_root().approve_all_edits():return
        QApplication.instance().exit(UPDATE_EXIT)

    def build_menus(self):
        info=self.menuBar().addMenu('Info')
        self.about_action=info.addAction('About HWI4U…');self.about_action.triggered.connect(self.show_about)
        self.about_action.setToolTip('Application version, data location, license and backup information.')
        guide=info.addAction('Open user guide');guide.triggered.connect(self.open_guide)
        update=info.addAction('Check for local updates');update.triggered.connect(self.show_update_status)
        quit_action=info.addAction('Quit HWI4U');quit_action.setMenuRole(QAction.QuitRole);quit_action.triggered.connect(lambda:self.editor_root().close())
        self.language_menu=self.menuBar().addMenu('Language');self.language_actions={};group=QActionGroup(self);group.setExclusive(True)
        for code,label in LANGUAGES.items():
            action=self.language_menu.addAction(label);action.setCheckable(True);action.setChecked(code==QApplication.instance().inventory_language)
            group.addAction(action);action.triggered.connect(lambda checked=False,key=code:self.set_language(key));self.language_actions[code]=action
    def set_language(self,code):
        if code not in LANGUAGES:raise ValueError('Unsupported interface language')
        install(code)
        for key,action in self.language_actions.items():action.setChecked(key==code)
        self.refresh_photos();self.refresh_manuals();self.translate_state_cells();self.filter_rows();self.location_panel.refresh_text();self.lifecycle_panel.render();apply(self)
        for view in [self.editor_root(),*list(self.editor_root().editors.values())]:
            if view is self:continue
            for key,action in view.language_actions.items():action.setChecked(key==code)
            view.refresh_photos();view.refresh_manuals();view.translate_state_cells();view.filter_rows();view.location_panel.refresh_text();view.lifecycle_panel.render();apply(view)
        try:write_language(self.store.path.parent,code)
        except OSError as exc:QMessageBox.warning(self,'Could not save language preference',str(exc))
    def refresh_roles(self):
        self.role_button.setText(', '.join(self.role_values) or tr('Choose roles…'))
    def choose_roles(self):
        from PySide6.QtWidgets import QInputDialog
        def add_choice():
            value,ok=QInputDialog.getText(self,tr('Add role'),tr('Role name (catalogue saves immediately)'))
            if not ok:return None
            try:return self.store.add_role(value)
            except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc);return None
        dialog=ChoiceDialog('Roles',[(v,v) for v in self.store.roles()],self.role_values,self,add_choice=add_choice)
        if dialog.exec()==QDialog.Accepted:self.role_values=sorted(dialog.selected());self.refresh_roles()
    def translate_state_cells(self):
        self.list_controller.render();self.refresh_roles()
        if hasattr(self,'workspace'):self.workspace.translate()

    def about_text(self):
        with self.store.connect() as c:schema=c.execute('PRAGMA user_version').fetchone()[0]
        c.close()
        def line(label,value):return '<b>'+html.escape(tr(label))+':</b> '+html.escape(str(value))+'<br>'
        text='<h2>'+html.escape(tr('HWI4U'))+'</h2><p>'+html.escape(tr('Local, offline hardware inventory'))+'</p>'
        text+=line('Environment',os.environ.get('INVENTORY_CHANNEL','production'))
        text+=line('Application version',APP_VERSION)+line('Release date',RELEASE_DATE)+line('Database schema',schema)
        text+=line('Database location',self.store.path)+line('Photo folder',self.store.path.parent/'photos')+line('Manual folder',self.store.path.parent/'manuals')
        text+=line('License','MIT — LICENSE-desktop.txt')+line('Python',platform.python_version())+line('PySide6 / Qt',PySide6.__version__)+line('SQLite',sqlite3.sqlite_version)
        for source in ('Current operating system and firmware assessments, with evidence and checked date.','Devices, dates, types, connection assessments and local photo attachments.','No network service or cloud account is required.','Full backup includes the database, attached photos and local manuals. Automatic snapshots contain only the database.','Shared catalogue values and your entries remain unchanged when switching language.'):
            text+='<p>'+html.escape(tr(source))+'</p>'
        return text
    def show_about(self):
        box=QMessageBox(self);box.setWindowTitle(tr('About HWI4U'));box.setTextFormat(Qt.RichText);box.setText(self.about_text());box.setStandardButtons(QMessageBox.Ok);box.exec()
    def open_guide(self):
        code=QApplication.instance().inventory_language
        path=Path(os.environ.get('INVENTORY_PROJECT_ROOT',Path(__file__).resolve().parent))/f'GUIDE.{code}.md'
        if not path.is_file():path=path.with_name('GUIDE.en.md')
        if not QDesktopServices.openUrl(QUrl.fromLocalFile(str(path))):QMessageBox.warning(self,'Could not open guide',str(path))
    def install_help(self):
        for key,widget in self.inputs.items():
            widget.setToolTip(FIELD_HELP[key])
            if isinstance(widget,OptionalDate):widget.known.setToolTip(TIPS['date']);widget.editor.setToolTip(FIELD_HELP[key])
        for widget,key in ((self.type_group,'type_group'),(self.search,'search'),(self.group_filter,'filter'),(self.type_filter,'filter'),(self.photo_list,'photo_list')):widget.setToolTip(TIPS[key])
        for button in self.findChildren(QPushButton):
            label=button.property('_i18n_source_text') or button.text()
            if label in BUTTONS:button.setToolTip(BUTTONS[label][0])
        for panel in self.connection_panels.values():
            panel.supported.setToolTip(TIPS['supported']);panel.usage.setToolTip(TIPS['usage']);panel.source.setToolTip(TIPS['assessment_source'])
            panel.table.setToolTip(TIPS['supported']+' '+TIPS['usage']);panel.assessed.setToolTip(TIPS['date']);panel.assessed.known.setToolTip(TIPS['date']);panel.assessed.editor.setToolTip(TIPS['date'])
        for form in self.findChildren(QFormLayout):
            for row in range(form.rowCount()):
                item=form.itemAt(row,QFormLayout.FieldRole)
                widget=item.widget() if item else None
                label=form.labelForField(widget) if widget else None
                if label and widget.toolTip():label.setToolTip(widget.toolTip())

    def values(self):
        data={}
        for key,w in self.inputs.items():
            if key in DATES:data[key]=w.value()
            elif key in ('current_state','physical_condition','device_type'):data[key]=w.currentData()
            elif key=='purchase_currency':data[key]=w.currentText().strip() or None
            else:data[key]=w.text().strip() if key in ('device_id','name','source') else (w.text().strip() or None)
        data['lifecycle']=self.lifecycle_panel.value()
        data['roles']=list(self.role_values)
        data['location_details']=self.location_panel.value()
        data['sources']={scope:selector.value() for scope,selector in self.source_selectors.items()}
        data['network']=self.network_panel.value()
        data['software']=self.software_panel.value()
        data['connectivity']={kind:panel.value() for kind,panel in self.connection_panels.items()}
        return data
    def unsaved_choice(self):
        box=QDialog(self);box.setWindowTitle(tr('Unsaved changes'));layout=QVBoxLayout(box)
        message=QLabel(tr('Save writes the form to the database. Discard leaves the saved database record unchanged. Keep editing returns to the form.'));message.setWordWrap(True);layout.addWidget(message)
        actions=QHBoxLayout();layout.addLayout(actions)
        for label,value,hint in [
            ('Save changes',QMessageBox.Save,'Write these device changes to the database, then continue.'),
            ('Discard unsaved changes',QMessageBox.Discard,'Ignore changes in this form. Do not delete the saved device.'),
            ('Keep editing',QMessageBox.Cancel,'Return to the form without saving or discarding changes.')]:
            button=QPushButton(tr(label));button.setToolTip(tr(hint));actions.addWidget(button)
            button.setAutoDefault(False);button.clicked.connect(lambda checked=False,value=value:box.done(int(value)))
            if value==QMessageBox.Cancel:button.setDefault(True);button.setFocus()
        result=box.exec();return result if result in (QMessageBox.Save,QMessageBox.Discard) else QMessageBox.Cancel

    def check_merchant(self):
        from difflib import get_close_matches
        value=self.inputs['purchased_at'].text().strip().casefold()
        known=['amazon','ebay','aliexpress','alternate','conrad','reichelt','media markt','saturn','ikea']
        known+= [r['purchased_at'] for r in getattr(self,'rows',[]) if r.get('purchased_at')]
        matches=get_close_matches(value,known,n=1,cutoff=0.78) if len(value)>=4 and value not in known else []
        self.merchant_suggestion=matches[0] if matches else None
        self.merchant_hint.setText((tr('Suggested spelling: ')+self.merchant_suggestion) if matches else '')
        self.merchant_fix.setVisible(bool(matches))
    def apply_merchant_suggestion(self):
        if self.merchant_suggestion:self.inputs['purchased_at'].setText(self.merchant_suggestion)

    def delete_device(self):
        if not self.original:
            QMessageBox.information(self,tr('Delete device'),tr('Select a saved device first.'));return
        if not self.discard_ok():return
        original=dict(self.original)
        box=QDialog(self);box.setWindowTitle(tr('Delete device'));layout=QVBoxLayout(box)
        title=QLabel(tr('Delete this device?')+'\n'+original['short_id']+' — '+original['name']);title.setProperty('_literal_text',True);layout.addWidget(title)
        note=QLabel(tr('A verified full backup is required. Device facts, attachments, network details and assembly links will be removed from current records. Other devices remain. A deletion history and reserved IDs are retained; local attachment files remain on disk.'));note.setWordWrap(True);layout.addWidget(note)
        actions=QHBoxLayout();layout.addLayout(actions)
        remove=QPushButton(tr('Delete device'));remove.setAutoDefault(False);remove.clicked.connect(box.accept);actions.addWidget(remove)
        keep=QPushButton(tr('Keep device'));keep.setDefault(True);keep.clicked.connect(box.reject);actions.addWidget(keep)
        if box.exec()!=QDialog.Accepted:return
        try:
            backup=self.store.delete(original);self.reload();self.load(None)
            self.status.setText(tr('Device deleted. Full backup: ')+str(backup));self.device_changed.emit(original['device_id'])
        except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc)

    def discard_ok(self):
        if self.baseline is None or self.values()==self.baseline:return True
        answer=self.unsaved_choice()
        if answer==QMessageBox.Save:return bool(self.save())
        return answer==QMessageBox.Discard
    @localized
    def load(self,row):
        if self.bound_device_id and row is None:
            row=next((r for r in self.rows if r['device_id']==self.bound_device_id),None)
            if row is None:
                self.form_scroll.setEnabled(False)
                if hasattr(self,'workspace'):self.workspace.setEnabled(False)
                for label in ('Save device','Delete device…'):self.toolbar_buttons[label].setEnabled(False)
                self.status.setText(tr('This device was deleted. Close this editor.'));return
        self.original=dict(row) if row else None
        self.form_title.setText('Edit device' if row else 'New device')
        if self.editor_owner is not None and row:
            self.header_title.setProperty('_literal_text',True);self.header_title.setText(row['short_id']+' — '+row['name']);self.header_title.setStyleSheet('font-size:18px;font-weight:600;');self.subtitle.hide()
        group=row.get('type_group') if row else None
        self.type_group.blockSignals(True);self.type_group.setCurrentIndex(max(0,self.type_group.findData(group)));self.type_group.blockSignals(False)
        self.fill_types(group)
        for key,w in self.inputs.items():
            value=row.get(key) if row else None
            if key in DATES:w.load(value)
            elif key in ('current_state','physical_condition','device_type'):w.setCurrentIndex(max(0,w.findData(value)))
            elif key=='purchase_currency':w.setCurrentText(value or '')
            else:w.setText(value or '')
        self.inputs['device_id'].setReadOnly(True)
        self.short_id.setText(row.get('short_id','') if row else '')
        self.lifecycle_panel.load(row.get('_lifecycle',[]) if row else [],row['device_id'] if row else None)
        self.role_values=list(row.get('_roles',[]) if row else []);self.refresh_roles()
        self.location_panel.load(row.get('_location',empty_location()) if row else empty_location())
        self.network_panel.load(row.get('_network',empty_network()) if row else empty_network())
        self.software_panel.load(row.get('_software',empty_software()) if row else empty_software())
        profile=row.get('_connectivity',empty_profile()) if row else empty_profile()
        for kind,panel in self.connection_panels.items():panel.load(profile[kind])
        for scope,selector in self.source_selectors.items():selector.load(row.get('_sources',{}).get(scope,[]) if row else [],row['device_id'] if row else None)
        self.network_panel.update_warning()
        for panel in self.connection_panels.values():panel.update_warning()
        self.baseline=self.values();self.refresh_photos();self.refresh_manuals();self.check_name();self.check_device_evidence()
    @localized
    def reload(self):
        self.loading=True
        try:
            self.rows=self.store.devices();self.list_controller.render()
        finally:self.loading=False
    def filter_rows(self):
        if hasattr(self,'list_controller'):self.list_controller.render()
    def select(self):
        if self.bound_device_id:return
        if self.loading:return
        n=self.table.currentRow()
        if n<0:return
        selected=self.list_controller.identity(n)
        if selected is None:return
        selected_id=selected['device_id']
        if self.discard_ok():self.load(next(row for row in self.rows if row['device_id']==selected_id));self.status.clear()
        else:
            self.loading=True;self.table.clearSelection();self.loading=False
    @localized
    def new(self):
        if self.bound_device_id:return
        if self.discard_ok():
            self.loading=True;self.table.clearSelection();self.loading=False
            self.load(None);self.status.clear();self.inputs['name'].setFocus()
    @localized
    def refresh(self):
        if not self.discard_ok():return
        try:self.reload_catalogue();self.reload();self.load(None);self.status.setText('Device list and types refreshed.')
        except (OSError,sqlite3.Error,ValueError) as exc:self.error(exc)
    @localized
    def cancel(self):
        if self.discard_ok():self.load(self.original);self.status.setText('Unsaved changes cancelled.')
    def error(self,exc):
        message=str(exc)
        if 'locked' in message.lower():message='Database busy. Finish or cancel changes in DB Browser, close it, and try again.'
        QMessageBox.warning(self,'Could not save',message)
    @localized
    def save(self):
        try:
            data=self.values()
            if not self.check_device_evidence():
                if hasattr(self,'workspace'):
                    self.workspace.tree.setCurrentItem(self.workspace.items['evidence'])
                self.form_scroll.ensureWidgetVisible(self.inputs['source'])
                self.inputs['source'].setFocus()
                raise ValueError('Device evidence is required: enter source text OR choose at least one device source. Sources in other sections do not satisfy this requirement.')
            if self.type_group.currentData() is not None and data['device_type'] is None:
                raise ValueError('Choose a device type for this group, or choose Unknown / choose a type to leave classification unknown.')
            backup=self.store.save(data,self.original)
            self.reload();row=next(r for r in self.rows if r['device_id']==data['device_id']);self.load(row)
            self.status.setText(f'Saved {row["short_id"]}. Pre-save backup: {backup.name}')
            if missing_sources(row['_connectivity']):self.status.setText(self.status.text()+' '+tr('Warning: connectivity source is missing. Saving is allowed.'))
            if missing_network_source(row['_network']):self.status.setText(self.status.text()+' '+tr('Warning: network information source is missing. Saving unverified details is allowed.'))
            notes=lifecycle_warnings(row['purchase_date'],row['_lifecycle'],row['manufacturer'] or '',row['model'] or '')
            if notes:self.status.setText(self.status.text()+' '+' '.join(tr(n) for n in notes))
            self.device_changed.emit(row['device_id'])
            return True
        except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc);return False
    @localized
    def fill_types(self,group,selected=None):
        combo=self.inputs['device_type'];combo.blockSignals(True);combo.clear();combo.addItem('Unknown',None)
        for row in self.type_rows:
            if group is None or row['group_name']==group:combo.addItem(row['type_name'],row['type_name'])
        combo.setCurrentIndex(max(0,combo.findData(selected)));combo.blockSignals(False)
    def group_changed(self):
        self.fill_types(self.type_group.currentData())
    def type_changed(self):
        kind=self.inputs['device_type'].currentData()
        if kind is None:return
        group=next(r['group_name'] for r in self.type_rows if r['type_name']==kind)
        self.type_group.blockSignals(True);self.type_group.setCurrentIndex(self.type_group.findData(group));self.type_group.blockSignals(False)
        self.fill_types(group,kind)
    @localized
    def filter_group_changed(self):
        group=self.group_filter.currentData();self.type_filter.blockSignals(True);self.type_filter.clear()
        self.type_filter.addItem('All types',None);self.type_filter.addItem('Unknown','__unknown__')
        for row in self.type_rows:
            if group is None or row['group_name']==group:self.type_filter.addItem(row['type_name'],row['type_name'])
        self.type_filter.blockSignals(False)
        if hasattr(self,'rows'):self.filter_rows()
    def model_suggestions(self):
        try:
            dialog=ModelDialog(self)
            if dialog.exec()!=QDialog.Accepted or dialog.applied is None:return
            self.apply_model_profile(dialog.applied)
        except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc)
    def apply_model_profile(self,profile):
        # Recheck exact identity and revision at acceptance; never apply a stale catalogue row.
        rows=ModelStore(self.store.path).list(self.inputs['manufacturer'].text(),self.inputs['model'].text())
        if profile not in rows:raise ValueError('Model profile changed; reopen the catalogue.')
        kind=profile['device_type']
        self.reload_catalogue()
        self.type_group.blockSignals(True);self.type_group.setCurrentIndex(max(0,self.type_group.findData(profile['group_name'])));self.type_group.blockSignals(False)
        self.fill_types(profile['group_name'],kind)
        self.role_values=list(profile['roles']);self.refresh_roles()
        warranty=[r for r in self.lifecycle_panel.value() if r['kind']=='warranty_expiry']
        self.lifecycle_panel.load(profile['lifecycle']+warranty,self.original['device_id'] if self.original else None)
        ids=sorted(set(self.source_selectors['device'].value()+profile['sources']))
        self.source_selectors['device'].load(ids,self.original['device_id'] if self.original else None)
        self.status.setText(tr('Model suggestion applied to the form. Review and Save device to commit; Cancel changes restores the saved device.'))

    def manage_types(self):
        if not self.discard_ok():return
        if TypeDialog(self.store,self).exec()!=QDialog.Accepted:return
        self.reload_catalogue();self.reload();self.load(None);self.status.setText('Device types updated. Select a device to assign its type.')
    @localized
    def reload_catalogue(self):
        for kind,panel in self.connection_panels.items():panel.set_options(self.store.connection_options(kind))
        self.type_rows=self.store.types()
        for combo,placeholder in ((self.type_group,'Unknown / choose a type'),(self.group_filter,'All groups')):
            selected=combo.currentData();combo.blockSignals(True);combo.clear();combo.addItem(placeholder,None)
            if combo is self.group_filter:combo.addItem('Unknown','__unknown__')
            for group in self.store.groups():combo.addItem(group,group)
            combo.setCurrentIndex(max(0,combo.findData(selected)));combo.blockSignals(False)
        self.filter_group_changed()

    def manage_connections(self):
        if not self.discard_ok():return
        if ConnectionDialog(self.store,self).exec()!=QDialog.Accepted:return
        self.reload_catalogue();self.reload();self.load(None);self.status.setText('Connection choices updated.')

    @localized
    def refresh_photos(self):
        self.photo_list.clear();self.add_photo_button.setEnabled(self.original is not None)
        if self.original is None:
            self.photo_hint.setText('Save a device before attaching photos.');return
        try:
            rows=self.photo_store.list(self.original['device_id'])
            self.photo_hint.setText('JPEG / PNG • up to 25 MiB and 16 megapixels. Attachments save immediately. Double-click to open.')
            for row in rows:
                text=(row['caption'] or row['original_name'])+'\n'+tr('Source: ')+row['source']
                item=QListWidgetItem(text);item.setData(Qt.UserRole,row)
                thumb=managed_path(self.store.path.parent,row['thumbnail_path'])
                if thumb.is_file():item.setIcon(QIcon(str(thumb)))
                else:item.setText(text+'\nThumbnail missing')
                self.photo_list.addItem(item)
        except (ValueError,OSError,sqlite3.Error) as exc:self.status.setText('Photo list unavailable: '+str(exc))
    def add_photo(self):
        if not self.original:return
        if self.values()!=self.baseline:
            QMessageBox.information(self,'Save changes first','Save or cancel device changes before adding a photo.');return
        filename,_=QFileDialog.getOpenFileName(self,'Choose device photo','','Images (*.jpg *.jpeg *.png)')
        if not filename:return
        dialog=QDialog(self);dialog.setWindowTitle('Photo details');layout=QFormLayout(dialog)
        filename_label=QLabel(Path(filename).name);filename_label.setProperty('_literal_text',True);layout.addRow(filename_label)
        caption=QLineEdit();caption.setPlaceholderText('For example: front view or device label')
        source=QLineEdit();source.setPlaceholderText('For example: my photograph, 2026-10-18')
        layout.addRow('Description (optional)',caption);layout.addRow('Information source *',source)
        buttons=QDialogButtonBox(QDialogButtonBox.Save|QDialogButtonBox.Cancel);buttons.accepted.connect(dialog.accept);buttons.rejected.connect(dialog.reject);layout.addRow(buttons)
        while dialog.exec()==QDialog.Accepted:
            try:
                self.photo_store.add(self.original['device_id'],filename,caption.text(),source.text())
                self.refresh_photos();self.status.setText('Photo copied and attached. Use Full backup to include database and photos in one archive.');return
            except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc)
    def open_photo(self):
        item=self.photo_list.currentItem()
        if item is None:return
        row=item.data(Qt.UserRole)
        try:
            path=managed_path(self.store.path.parent,row['relative_path'])
            from photo_files import sha256
            if not path.is_file() or sha256(path)!=row['sha256']:raise ValueError('Original photo is missing or changed. Restore it from a full backup.')
            reader=QImageReader(str(path));reader.setAutoTransform(True);image=reader.read()
            if image.isNull():raise ValueError('Could not open the original image.')
            dialog=QDialog(self);dialog.setProperty('_literal_title',True);dialog.setWindowTitle(row['caption'] or row['original_name']);dialog.resize(900,650)
            layout=QVBoxLayout(dialog);scroll=QScrollArea();label=QLabel();label.setPixmap(QPixmap.fromImage(image));scroll.setWidget(label);layout.addWidget(scroll)
            layout.addWidget(QLabel('Original image • '+str(path)))
            dialog.exec()
        except (ValueError,OSError) as exc:self.error(exc)
    def detach_photo(self):
        item=self.photo_list.currentItem()
        if item is None:return
        if self.values()!=self.baseline:
            QMessageBox.information(self,'Save changes first','Save or cancel device changes before detaching a photo.');return
        if QMessageBox.question(self,'Detach photo','Remove this attachment from the device? Files remain on disk to support older backups.',QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)!=QMessageBox.Yes:return
        try:
            self.photo_store.detach(item.data(Qt.UserRole)['photo_id']);self.refresh_photos();self.status.setText('Photo detached; files retained for older backups.')
        except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc)
    @localized
    def refresh_manuals(self):
        self.manual_list.clear();self.add_manual_button.setEnabled(self.original is not None)
        if self.original is None:self.manual_hint.setText('Save a device before adding references.');return
        try:
            rows=self.manual_store.list(self.original['device_id'])
            self.manual_hint.setText('Multiple online links or local PDFs. References save immediately. Double-click to open.')
            for row in rows:
                meta=[row['title'],tr('Online link' if row['kind']=='online' else 'Local PDF')]
                for key in ('language','edition','applicable_model'):
                    if row[key]:meta.append(row[key])
                item=QListWidgetItem(' • '.join(meta));item.setData(Qt.UserRole,row)
                item.setToolTip((row['url'] or row['relative_path'])+'\n'+tr('Source: ')+row['source']);self.manual_list.addItem(item)
        except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc)
    def manual_edit_ready(self):
        if self.original is None:return False
        if self.values()!=self.baseline:
            QMessageBox.information(self,'Save changes first','Save or cancel device changes before editing manual references.');return False
        return True
    def add_manual(self):
        if not self.manual_edit_ready():return
        if ManualDialog(self.manual_store,self.original['device_id'],parent=self).exec()==QDialog.Accepted:
            self.refresh_manuals();self.status.setText(tr('Manual reference saved. Full backup includes attached local PDFs.'))
    def edit_manual(self):
        if not self.manual_edit_ready():return
        item=self.manual_list.currentItem()
        if item is None:return
        if ManualDialog(self.manual_store,self.original['device_id'],original=item.data(Qt.UserRole),parent=self).exec()==QDialog.Accepted:
            self.refresh_manuals();self.status.setText(tr('Manual reference saved.'))
    def open_manual(self):
        item=self.manual_list.currentItem()
        if item is None:return
        row=item.data(Qt.UserRole)
        try:
            if row['kind']=='online':url=QUrl(validate_url(row['url']))
            else:
                from photo_files import sha256
                path=manual_path(self.store.path.parent,row['relative_path'])
                if not path.is_file() or sha256(path)!=row['sha256']:raise ValueError('Manual file is missing or changed. Restore it from a full backup.')
                url=QUrl.fromLocalFile(str(path))
            if not QDesktopServices.openUrl(url):raise ValueError('Could not open the reference. Check your browser or PDF file association.')
        except (ValueError,OSError) as exc:self.error(exc)
    def detach_manual(self):
        if not self.manual_edit_ready():return
        item=self.manual_list.currentItem()
        if item is None:return
        if QMessageBox.question(self,'Detach manual reference','Remove this reference? Managed local files remain for older backups.',QMessageBox.Yes|QMessageBox.Cancel,QMessageBox.Cancel)!=QMessageBox.Yes:return
        try:self.manual_store.detach(item.data(Qt.UserRole));self.refresh_manuals();self.status.setText(tr('Reference detached; managed files retained.'))
        except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc)

    def manage_network_links(self):
        if self.values()!=self.baseline:
            QMessageBox.information(self,'Save changes first','Save or cancel device changes before editing network connections.');return
        from topology_ui import LinkManager
        LinkManager(self.store.path,OptionalDate,self).exec()

    def full_backup(self):
        if self.values()!=self.baseline:
            QMessageBox.information(self,'Save changes first','Save or cancel device changes before backing up.');return
        default=self.store.path.parent/'backups'/('inventory-with-files-'+dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')+'.zip')
        filename,_=QFileDialog.getSaveFileName(self,'Save full inventory backup',str(default),'ZIP archive (*.zip)')
        if not filename:return
        try:
            backup_bundle(self.store.path,Path(filename));self.status.setText('Verified full backup saved: '+filename)
        except (ValueError,OSError,sqlite3.Error) as exc:self.error(exc)

    def editor_root(self):
        return self.editor_owner or self

    def approve_all_edits(self):
        return all(view.discard_ok() for view in [self,*list(self.editors.values())])

    def open_device_editor(self,row_number):
        if self.bound_device_id:return None
        selected_row=self.list_controller.identity(row_number)
        if selected_row is None:return None
        device_id=selected_row['device_id']
        if not self.discard_ok():return None
        # Save can reorder the list. Match by immutable ID, never the old row index.
        self.reload()
        selected=next((r for r in self.rows if r['device_id']==device_id),None)
        if selected is None:return None
        current_id=self.original['device_id'] if self.original else None
        self.load(next((r for r in self.rows if r['device_id']==current_id),None))
        if device_id in self.editors:
            editor=self.editors[device_id];editor.showMaximized();editor.raise_();editor.activateWindow();return editor
        editor=Window(self.store,language=QApplication.instance().inventory_language,editor_owner=self)
        editor.bound_device_id=device_id;editor.load(selected)
        from editor_workspace import EditorWorkspace
        editor.workspace=EditorWorkspace(editor)
        editor.splitter.addWidget(editor.workspace)
        editor.splitter.setSizes([0,1500])
        editor.table.hide();editor.filter_bar.hide();editor.search.hide()
        for label in ('New device','Manage types','Save device'):editor.toolbar_buttons[label].hide()
        editor.client_button.hide();editor.connections_button.hide()
        editor.setProperty('_literal_title',True)
        editor.setWindowTitle('HWI4U — '+selected['short_id']+' — '+selected['name'])
        editor.setAttribute(Qt.WA_DeleteOnClose)
        self.editors[device_id]=editor
        editor.destroyed.connect(lambda *_:self.editors.pop(device_id,None) if self.editors.get(device_id) is editor else None)
        editor.device_changed.connect(lambda ident:self.synchronize_editors(ident,editor))
        if not getattr(self,'_editor_sync_connected',False):
            self.device_changed.connect(lambda ident:self.synchronize_editors(ident,self));self._editor_sync_connected=True
        editor.showMaximized();return editor

    def synchronize_editors(self,device_id,origin):
        for view in [self,*list(self.editors.values())]:
            if view is origin:continue
            selected=view.original['device_id'] if view.original else None
            pending=view.baseline is not None and view.values()!=view.baseline
            view.reload()
            if selected!=device_id:continue
            if pending:
                view.status.setText(tr('This device changed in another window. Your unsaved edits are kept. Cancel and refresh before saving.'))
            else:
                row=next((r for r in view.rows if r['device_id']==device_id),None)
                view.load(row)
                if row:view.status.setText(tr('Device refreshed after changes in another window.'))

    def closeEvent(self,event):
        if self.skip_close_prompt:event.accept();return
        allowed=self.discard_ok() if self.editor_owner else self.approve_all_edits()
        if not allowed:event.ignore();return
        if self.editor_owner:
            self.editor_owner.editors.pop(self.bound_device_id,None)
        else:
            for editor in list(self.editors.values()):editor.skip_close_prompt=True;editor.close()
        event.accept()

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=Path(__file__).resolve().parent/'hardware.sqlite3')
    parser.add_argument('--language',choices=tuple(LANGUAGES))
    args=parser.parse_args();app=QApplication(sys.argv[:1]);app.setStyle('Fusion')
    try:
        if os.environ.get('INVENTORY_CHANNEL')=='test':
            from environments import validate_test_database
            validate_test_database(Path(os.environ['INVENTORY_PROJECT_ROOT']),args.db)
        window=Window(DeviceStore(args.db),language=args.language)
    except (OSError,sqlite3.Error,ValueError) as exc:
        QMessageBox.critical(None,'Cannot open inventory',str(exc));return 1
    window.show();return app.exec()
if __name__=='__main__':sys.exit(main())
