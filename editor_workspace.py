"""Adaptive expanded editor: reparent the original controls, never duplicate values."""
from PySide6.QtCore import Qt,QTimer
from PySide6.QtWidgets import (QWidget,QHBoxLayout,QVBoxLayout,QGridLayout,QFormLayout,QGroupBox,QTreeWidget,QTreeWidgetItem,QLabel,QSizePolicy,QSplitter)
from ui_i18n import tr

TITLES={'identity':'General','location':'Hardware & location','purchase':'Purchase & lifecycle','lifecycle':'Lifecycle dates','condition':'State & condition','network':'Network identity','software':'Software','interface':'Connection interfaces','protocol':'Communication protocols','photos':'Device photos','manuals':'Manuals and references','evidence':'Sources and evidence'}
BRANCHES=[('Device',['identity','location']),('Purchase & lifecycle',['purchase','lifecycle','condition']),('Network & connectivity',['network','interface','protocol']),('Software',['software']),('Files & evidence',['photos','manuals','evidence'])]

class TileGrid(QWidget):
    def __init__(self):
        super().__init__();self.grid=QGridLayout(self);self.grid.setContentsMargins(8,8,12,12);self.grid.setSpacing(16);self.cards=[];self.columns=0;self.pending=False;self.timer=QTimer(self);self.timer.setSingleShot(True);self.timer.timeout.connect(self.reflow)
        self.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Preferred)
    def resizeEvent(self,event):
        super().resizeEvent(event);self.schedule()
    def schedule(self):
        if self.pending:return
        self.pending=True;self.timer.start(0)
    def reflow(self):
        self.pending=False;columns=max(1,min(4,(self.width()-20+16)//456))
        if columns==self.columns:return
        self.columns=columns
        while self.grid.count():self.grid.takeAt(0)
        for c in range(4):self.grid.setColumnStretch(c,1 if c<columns else 0)
        for i,card in enumerate(self.cards):self.grid.addWidget(card,i//columns,i%columns,Qt.AlignTop)
        self.updateGeometry()

class EditorWorkspace(QWidget):
    def __init__(self,window):
        super().__init__();self.window=window;self.tree=QTreeWidget();self.tree.setHeaderHidden(True);self.tree.setMinimumWidth(170);self.tree.setMaximumWidth(300);self.tree.setIndentation(16)
        self.tree.setToolTip(tr('Expand navigation groups. Select a section to find its tile; other sections remain available.'))
        self.tiles=TileGrid();self.cards={};self.forms={};self.items={}
        for key,title in TITLES.items():
            card=QGroupBox(title.replace('&','&&'));card.setMinimumWidth(0);card.setSizePolicy(QSizePolicy.Ignored,QSizePolicy.Preferred);form=QFormLayout(card);form.setRowWrapPolicy(QFormLayout.WrapLongRows);form.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow);form.setContentsMargins(14,20,14,14);form.setSpacing(10);self.cards[key]=card;self.forms[key]=form;self.tiles.cards.append(card)
        for title,keys in BRANCHES:
            branch=QTreeWidgetItem(self.tree,[title]);branch.setData(0,Qt.UserRole,title)
            for key in keys:
                item=QTreeWidgetItem(branch,[TITLES[key]]);item.setData(0,Qt.UserRole,key);self.items[key]=item
            branch.setExpanded(title in ('Device','Purchase & lifecycle','Network & connectivity'))
        window.lifecycle_panel.setTitle('')
        self.old_panel=window.form_scroll.takeWidget();self.old_panel.setParent(self);self.old_panel.hide();old=self.old_panel.layout();self.footer=QWidget();footer_layout=QVBoxLayout(self.footer);footer_layout.setContentsMargins(0,0,0,0)
        # Direct widget mapping avoids relying on translated field labels.
        mapping={id(window.lifecycle_panel):'lifecycle',id(window.model_button):'identity',id(window.short_id):'identity',id(window.type_group):'identity',id(window.name_feedback):'identity',id(window.role_button):'identity',id(window.location_panel):'location',id(window.source_selectors['device'].parentWidget()):'evidence',id(window.merchant_hint):'purchase',id(window.merchant_fix):'purchase'}
        for key,widget in window.inputs.items():
            mapping[id(widget)]=('identity' if key in ('device_id','name','device_type') else 'location' if key in ('manufacturer','model','serial_number','location') else 'evidence' if key=='source' else 'condition' if key in ('current_state','physical_condition') else 'purchase')
        sections={id(section):key for section,key in zip(window.sections,('network','software','interface','protocol'))}
        mode='identity'
        while old.rowCount():
            row=old.takeRow(0);label=row.labelItem.widget() if row.labelItem else None;field=row.fieldItem;widget=field.widget() if field else None;layout=field.layout() if field else None
            if widget is window.form_title:widget.hide();continue
            if widget and id(widget) in sections:
                key=sections[id(widget)];body=widget.body;body.setParent(self.cards[key]);self.forms[key].addRow(body);body.show();widget.hide();continue
            text=(widget.property('_i18n_source_text') or widget.text()) if isinstance(widget,QLabel) else ''
            if text in ('Device photos','Manuals and references'):
                mode='photos' if text=='Device photos' else 'manuals';widget.hide();continue
            if layout and mode=='identity':
                # Save/cancel row appears after the assessment note, before attachment sections.
                names=[layout.itemAt(i).widget().property('_i18n_source_text') or layout.itemAt(i).widget().text() for i in range(layout.count()) if layout.itemAt(i).widget() and hasattr(layout.itemAt(i).widget(),'text')]
                if 'Save device' in names:footer_layout.addLayout(layout);continue
            key=mapping.get(id(widget),mode) if widget else mode
            if isinstance(widget,QLabel) and str(text).startswith('Uncheck Known'):key='evidence'
            if widget and (widget.property('_i18n_source_text') or getattr(widget,'text',lambda:'' )())=='Manage connection choices…':key='interface'
            form=self.forms[key]
            if label and widget:form.addRow(label,widget)
            elif widget:form.addRow(widget)
            elif layout:form.addRow(layout)
        window.form_scroll.setWidget(self.tiles)
        splitter=QSplitter();splitter.addWidget(self.tree);splitter.addWidget(window.form_scroll);splitter.setStretchFactor(0,0);splitter.setStretchFactor(1,1);splitter.setSizes([220,1500]);self.splitter=splitter
        outer=QVBoxLayout(self);outer.setContentsMargins(0,0,0,0);outer.addWidget(splitter,1);outer.addWidget(self.footer)
        self.tree.currentItemChanged.connect(self.navigate);self.translate();self.tiles.schedule()
    def navigate(self,item,previous=None):
        key=item.data(0,Qt.UserRole) if item else None
        if key not in self.cards:return
        card=self.cards[key]
        self.window.form_scroll.ensureWidgetVisible(card,12,12)
        for k,c in self.cards.items():c.setProperty('activeTile',k==key);c.style().unpolish(c);c.style().polish(c)
        self.setStyleSheet('QGroupBox[activeTile="true"] { border: 2px solid palette(highlight); border-radius: 5px; margin-top: 8px; } QGroupBox[activeTile="true"]::title { subcontrol-origin: margin; left: 10px; }')
    def translate(self):
        for key,card in self.cards.items():card.setTitle(tr(TITLES[key]).replace('&','&&'));self.items[key].setText(0,tr(TITLES[key]))
        for i,(title,keys) in enumerate(BRANCHES):self.tree.topLevelItem(i).setText(0,tr(title))
