"""Guided location editor. Dialog changes remain pending until Save device."""
from PySide6.QtCore import Qt,Signal
from PySide6.QtWidgets import (QWidget,QDialog,QVBoxLayout,QHBoxLayout,QFormLayout,
    QLabel,QLineEdit,QComboBox,QPushButton,QGroupBox,QScrollArea,QCompleter)
from location_store import (PLACE_FIELDS,empty_location,validate_location,location_summary)
from ui_i18n import tr,apply

LABELS={'country':'Country','postal_code':'Postal code','city':'City','street':'Street',
        'house_number':'House number','building':'Building / site','floor':'Floor / storey',
        'room':'Room','position':'Position / wall','height_m':'Mounting height (m)',
        'notes':'Placement notes'}
HELP={
 'building':'Optional building or site. Reuse a saved place or enter a new one.',
 'floor':'Optional floor label, for example basement, ground floor or first floor.',
 'room':'Optional room. All hierarchy levels can be left out when irrelevant.',
 'position':'Position for this device only, for example northwest wall or rack shelf.',
 'height_m':'Optional height in metres, from 0 to 10000. Both 1.8 and 1,8 are accepted. State the reference level.',
 'notes':'Optional placement details. Describe the reference here when choosing Other height reference.'}

class LocationDialog(QDialog):
    def __init__(self,store,value,parent=None):
        super().__init__(parent);self.setWindowTitle('Device location');self.resize(640,680)
        outer=QVBoxLayout(self);scroll=QScrollArea();scroll.setWidgetResizable(True)
        body=QWidget();layout=QVBoxLayout(body);layout.setAlignment(Qt.AlignTop);scroll.setWidget(body);outer.addWidget(scroll)
        title=QLabel('Where is this device?');layout.addWidget(title)
        self.state=QComboBox()
        for text,key in [('Unknown','unknown'),('Recorded location','recorded'),('Not applicable / portable','not_applicable')]:self.state.addItem(text,key)
        form=QFormLayout();form.addRow('Location status',self.state);layout.addLayout(form)
        self.editor=QWidget();editor=QVBoxLayout(self.editor);editor.setContentsMargins(0,0,0,0);layout.addWidget(self.editor)
        reuse_form=QFormLayout();self.reuse=QComboBox();self.reuse.addItem('Current form values',None);self.reuse.addItem('New location…','new')
        self.reuse.setToolTip('Reuse the address, building, floor and room. Precise placement is specific to this device. Existing places are never renamed here.')
        for place in store.places():
            data=empty_location();data.update({k:place[k] for k in PLACE_FIELDS});data['state']='recorded'
            self.reuse.addItem(location_summary(data),place)
            self.reuse.setItemData(self.reuse.count()-1,True,275)
        reuse_form.addRow('Reuse an existing location',self.reuse);editor.addLayout(reuse_form)
        main=QFormLayout();editor.addLayout(main);self.inputs={}
        for key in ('building','floor','room','position','height_m'):
            w=QLineEdit();w.setMaxLength(200);w.setToolTip(HELP[key]);self.inputs[key]=w;main.addRow(LABELS[key],w)
            if key=='floor':
                completer=QCompleter([tr(v) for v in ('Basement','Ground floor','First floor','Attic')],w);completer.setCaseSensitivity(Qt.CaseInsensitive);w.setCompleter(completer)
        self.reference=QComboBox();self.reference.addItem('Choose a height reference',None)
        for text,key in [('Above finished floor','finished_floor'),('Above ground level','ground_level'),('Other height reference','other')]:self.reference.addItem(text,key)
        self.reference.setToolTip('Height is independent of floor labels and X/Y position. Choose the actual reference level.')
        main.addRow('Height reference',self.reference)
        self.more=QGroupBox('Address and additional notes (optional)');self.more.setCheckable(True);self.more.setChecked(False)
        extra=QVBoxLayout(self.more);self.more_body=QWidget();address=QFormLayout(self.more_body);extra.addWidget(self.more_body);editor.addWidget(self.more)
        for key in ('country','postal_code','city','street','house_number','notes'):
            w=QLineEdit();w.setMaxLength(200);w.setToolTip(HELP.get(key,'Optional single-line Unicode text, maximum 200 characters.'))
            self.inputs[key]=w;address.addRow(LABELS[key],w)
        self.more.toggled.connect(self.more_body.setVisible)
        self.preview=QLabel();self.preview.setWordWrap(True);self.preview.setProperty('_literal_text',True);layout.addWidget(QLabel('Location preview'));layout.addWidget(self.preview)
        note=QLabel('Placement belongs to this device. Other devices are unchanged. Use location returns to the device form; Save device writes to the database.');note.setWordWrap(True);layout.addWidget(note)
        self.error=QLabel();self.error.setWordWrap(True);layout.addWidget(self.error)
        actions=QHBoxLayout();outer.addLayout(actions)
        self.use=QPushButton('Use location');self.use.setToolTip('Validate and return these pending details to the device form. Save device is still required.');self.use.clicked.connect(self.accept_location);actions.addWidget(self.use)
        cancel=QPushButton('Cancel');cancel.setToolTip('Keep the location values from before this dialog.');cancel.clicked.connect(self.reject);actions.addWidget(cancel)
        self.state.setCurrentIndex(self.state.findData(value['state']))
        for key,w in self.inputs.items():w.setText(value.get(key) or '');w.textChanged.connect(self.update_preview)
        self.reference.setCurrentIndex(max(0,self.reference.findData(value.get('height_reference'))))
        self.more.setChecked(any(value.get(k) for k in ('country','postal_code','city','street','house_number','notes')))
        self.more_body.setVisible(self.more.isChecked());self.state.currentIndexChanged.connect(self.update_preview);self.reference.currentIndexChanged.connect(self.update_preview);self.reuse.currentIndexChanged.connect(self.reuse_place)
        self.update_preview();apply(self)

    def value(self):
        if self.state.currentData()!='recorded':return dict(empty_location(),state=self.state.currentData())
        return dict(state='recorded',height_reference=self.reference.currentData(),**{k:w.text() or None for k,w in self.inputs.items()})

    def update_preview(self):
        self.editor.setVisible(self.state.currentData()=='recorded')
        try:
            data=validate_location(self.value());self.preview.setText(location_summary(data,tr));self.error.clear();self.use.setEnabled(True)
        except ValueError as exc:
            self.preview.setText(tr('Location details need attention.'));self.error.setText(tr(str(exc)));self.use.setEnabled(False)

    def reuse_place(self):
        value=self.reuse.currentData()
        if value is None:return
        keys=(*PLACE_FIELDS,'position','height_m','notes')
        for key in keys:self.inputs[key].setText((value.get(key) or '') if isinstance(value,dict) and key in PLACE_FIELDS else '')
        self.reference.setCurrentIndex(0)
        self.more.setChecked(any(self.inputs[k].text() for k in ('country','postal_code','city','street','house_number')))
        self.update_preview()

    def accept_location(self):
        try:self.result_location=validate_location(self.value());self.accept()
        except ValueError as exc:self.error.setText(tr(str(exc)))

class LocationPanel(QWidget):
    changed=Signal()
    def __init__(self,store,parent=None):
        super().__init__(parent);self.store=store;self.data=empty_location()
        layout=QVBoxLayout(self);layout.setContentsMargins(0,0,0,0)
        layout.addWidget(QLabel('Structured location'))
        self.summary=QLabel();self.summary.setWordWrap(True);self.summary.setProperty('_literal_text',True);layout.addWidget(self.summary)
        self.button=QPushButton('Guided location…');self.button.setToolTip('Choose or reuse a place, then enter device-specific position and mounting height. Existing location text is preserved.');self.button.clicked.connect(self.edit);layout.addWidget(self.button)
        self.load(self.data)
    def load(self,data):self.data=dict(data);self.refresh_text()
    def refresh_text(self):self.summary.setText(location_summary(self.data,tr))
    def value(self):return dict(self.data)
    def edit(self):
        dialog=LocationDialog(self.store,self.data,self)
        if dialog.exec()==QDialog.Accepted:self.load(dialog.result_location);self.changed.emit()
