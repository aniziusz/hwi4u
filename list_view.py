"""Device-list presentation; UUIDs never depend on row order or visible columns."""
import json,itertools
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QVBoxLayout,QHBoxLayout,QLabel,QComboBox,QLineEdit,QListWidget,QListWidgetItem,QPushButton,QDialogButtonBox,QAbstractItemView)
from ui_i18n import tr
from location_store import location_summary
from update_runtime import atomic_json

COLUMNS=[('short_id','Short ID'),('name','Name'),('type_group','Group'),('device_type','Type'),('current_state','State'),('physical_condition','Condition'),('roles','Roles'),('location','Location'),('building','Building'),('floor','Floor'),('room','Room'),('hostname','Hostname'),('mac','MAC addresses'),('ip','IP addresses'),('purchased_at','Purchased at'),('purchase_date','Purchase date'),('installation_date','Installation date'),('scrapped_date','Scrapped date'),('purchase_price','Purchase price'),('purchase_currency','Currency'),('device_id','Device ID')]
KEYS=[k for k,_ in COLUMNS];DEFAULT=KEYS[:6]
GROUPABLE=['type_group','device_type','roles','current_state','physical_condition','building','floor','room','purchased_at']

def values(row,key):
    if key=='roles':return row.get('_roles',[]) or ['']
    if key in ('hostname','mac','ip'):
        network=row['_network']
        if key=='hostname':return [network.get('hostname') or '']
        return sorted(set(v for p in network['interfaces'] for v in ([p.get('mac_address')] if key=='mac' else p.get('addresses',[])) if v)) or ['']
    if key in ('building','floor','room'):return [str(row.get('_location',{}).get(key) or '')]
    if key=='location':return [location_summary(row['_location']) or row.get('location') or '']
    return [str(row.get(key) or '')]

def display(row,key):
    return ', '.join(tr(v) if key in ('current_state','physical_condition') else v for v in values(row,key)) or tr('Unknown')

def matches(row,filters,skip=None):
    return all(key==skip or bool(set(values(row,key))&set(wanted)) for key,wanted in filters.items())

def groups(rows,keys):
    if not keys:return [((),rows)]
    buckets={}
    for row in rows:
        for path in itertools.product(*(values(row,k) for k in keys)):
            buckets.setdefault(path,[]).append(row)
    return sorted(buckets.items(),key=lambda x:tuple(v.casefold() for v in x[0]))

class ChoiceDialog(QDialog):
    """Search hides choices; it never changes checked values. Cancel is inert."""
    def __init__(self,title,options,selected,parent=None,allow_all=False,add_choice=None):
        super().__init__(parent);self.setWindowTitle(tr(title));self.resize(430,480);self.options=dict(options);self.all_mode=selected is None;self.allowed_all=allow_all
        layout=QVBoxLayout(self);self.search=QLineEdit();self.search.setPlaceholderText(tr('Search choices…'));layout.addWidget(self.search)
        self.list=QListWidget();layout.addWidget(self.list,1)
        for value,label in options:
            item=QListWidgetItem(label,self.list);item.setData(Qt.UserRole,value);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked if selected is None or value in selected else Qt.Unchecked)
        actions=QHBoxLayout();layout.addLayout(actions)
        for label,callback in [('Select all',lambda:self.tick(True)),('Clear selection',lambda:self.tick(False))]:
            button=QPushButton(tr(label));button.clicked.connect(callback);actions.addWidget(button)
        if allow_all:
            button=QPushButton(tr('No restriction'));button.clicked.connect(self.unrestrict);actions.addWidget(button)
        if add_choice:
            button=QPushButton(tr('Add role…'));layout.addWidget(button)
            def add():
                value=add_choice()
                if value and value not in self.options:
                    self.options[value]=value;item=QListWidgetItem(value,self.list);item.setData(Qt.UserRole,value);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked)
            button.clicked.connect(add)
        self.buttons=QDialogButtonBox(QDialogButtonBox.Apply|QDialogButtonBox.Cancel);layout.addWidget(self.buttons);self.buttons.button(QDialogButtonBox.Apply).clicked.connect(self.accept);self.buttons.rejected.connect(self.reject)
        self.search.textChanged.connect(lambda text:[self.list.item(i).setHidden(text.casefold() not in self.list.item(i).text().casefold()) for i in range(self.list.count())])
        self.list.itemChanged.connect(lambda *_:setattr(self,'all_mode',False))
    def tick(self,on):
        self.all_mode=False
        for i in range(self.list.count()):self.list.item(i).setCheckState(Qt.Checked if on else Qt.Unchecked)
    def unrestrict(self):
        self.tick(True);self.all_mode=True
    def selected(self):
        if self.allowed_all and self.all_mode:return None
        return [self.list.item(i).data(Qt.UserRole) for i in range(self.list.count()) if self.list.item(i).checkState()==Qt.Checked]

class ColumnsDialog(QDialog):
    def __init__(self,order,hidden,parent=None):
        super().__init__(parent);self.setWindowTitle(tr('Columns'));self.resize(420,520);layout=QVBoxLayout(self)
        note=QLabel(tr('Tick visible columns. Drag rows to change their order. Hiding never deletes data.'));note.setWordWrap(True);layout.addWidget(note)
        self.list=QListWidget();self.list.setDragDropMode(QAbstractItemView.InternalMove);layout.addWidget(self.list)
        labels=dict(COLUMNS)
        for key in order:
            item=QListWidgetItem(tr(labels[key]),self.list);item.setData(Qt.UserRole,key);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Unchecked if key in hidden else Qt.Checked)
        controls=QHBoxLayout();layout.addLayout(controls)
        for text,delta in [('Move up',-1),('Move down',1)]:
            b=QPushButton(tr(text));b.clicked.connect(lambda checked=False,d=delta:self.move(d));controls.addWidget(b)
        b=QPushButton(tr('Restore defaults'));b.clicked.connect(self.defaults);layout.addWidget(b)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def move(self,delta):
        i=self.list.currentRow();j=i+delta
        if i>=0 and 0<=j<self.list.count():item=self.list.takeItem(i);self.list.insertItem(j,item);self.list.setCurrentRow(j)
    def defaults(self):
        labels=dict(COLUMNS);self.list.clear()
        for key in KEYS:
            item=QListWidgetItem(tr(labels[key]),self.list);item.setData(Qt.UserRole,key);item.setFlags(item.flags()|Qt.ItemIsUserCheckable);item.setCheckState(Qt.Checked if key in DEFAULT else Qt.Unchecked)
    def result_view(self):
        order=[self.list.item(i).data(Qt.UserRole) for i in range(self.list.count())];hidden=[self.list.item(i).data(Qt.UserRole) for i in range(self.list.count()) if self.list.item(i).checkState()!=Qt.Checked]
        return order,hidden

class GroupDialog(QDialog):
    def __init__(self,selected,parent=None):
        super().__init__(parent);self.setWindowTitle(tr('Group by'));layout=QVBoxLayout(self);self.combos=[]
        note=QLabel(tr('Choose up to two levels. Roles can repeat devices; totals count unique devices.'));note.setWordWrap(True);layout.addWidget(note)
        for level in range(2):
            box=QComboBox();box.addItem(tr('Ungrouped'),None)
            for key,label in COLUMNS:
                if key in GROUPABLE:box.addItem(tr(label),key)
            box.setCurrentIndex(max(0,box.findData(selected[level] if len(selected)>level else None)));layout.addWidget(box);self.combos.append(box)
        buttons=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel);buttons.accepted.connect(self.accept);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
    def selected(self):return list(dict.fromkeys(c.currentData() for c in self.combos if c.currentData()))

def read_view(path):
    try:
        x=json.loads(Path(path).read_text());order=x['order'];hidden=x['hidden'];group=x.get('groups',[]);filters=x.get('filters',{})
        if set(order)!=set(KEYS) or len(order)!=len(KEYS) or not set(hidden)<=set(KEYS) or len(group)>2 or not set(group)<=set(GROUPABLE):raise ValueError()
        if not isinstance(filters,dict) or any(k not in KEYS or not isinstance(v,list) or any(not isinstance(a,str) for a in v) for k,v in filters.items()):raise ValueError()
        widths=x.get('widths',{})
        if not isinstance(widths,dict) or any(k not in KEYS or not isinstance(v,int) or not 40<=v<=2000 for k,v in widths.items()):widths={}
        return dict(order=order,hidden=hidden,groups=group,filters=filters,widths=widths)
    except (OSError,ValueError,TypeError,KeyError):return dict(order=KEYS[:],hidden=KEYS[6:],groups=[],filters={},widths={})

class DeviceListController:
    def __init__(self,window):
        from PySide6.QtWidgets import QInputDialog
        self.w=window;self.path=window.store.path.parent/('client-view-'+__import__('os').environ.get('INVENTORY_CHANNEL','production')+'.json');self.view=read_view(self.path);self.collapsed=set();self.sort_key='name';self.descending=False;self.rendering=False
        table=window.table;table.setProperty('_managed_columns',True);table.setColumnCount(len(COLUMNS));table.setHorizontalHeaderLabels([tr(v) for _,v in COLUMNS]);header=table.horizontalHeader();header.setSectionsMovable(True);header.setStretchLastSection(False);header.setSortIndicatorShown(True);header.setSortIndicator(1,Qt.AscendingOrder)
        header.sectionClicked.connect(self.sort);header.sectionMoved.connect(self.header_changed);header.sectionResized.connect(self.resized);table.itemClicked.connect(self.clicked);table.itemActivated.connect(self.clicked)
        self.controls=[];layout=window.filter_bar.layout()
        for i in range(layout.count()):
            widget=layout.itemAt(i).widget()
            if widget:widget.hide()
        for label,callback in [('Filters…',self.filters_dialog),('Columns…',self.columns_dialog),('Group by…',self.group_dialog),('Clear filters',self.clear_filters)]:
            b=QPushButton(tr(label));b.setProperty('_i18n_source_text',label);b.clicked.connect(callback);layout.addWidget(b);self.controls.append(b)
        self.summary=QLabel();self.summary.setWordWrap(True);self.summary.setProperty('_literal_text',True);layout.addWidget(self.summary,1)
        self.restore_header()
    def persist(self):
        try:atomic_json(self.path,self.view)
        except OSError as exc:self.w.status.setText(tr('Could not save view preferences: ')+str(exc))
    def restore_header(self):
        h=self.w.table.horizontalHeader();h.blockSignals(True)
        for visual,key in enumerate(self.view['order']):h.moveSection(h.visualIndex(KEYS.index(key)),visual)
        for key in KEYS:self.w.table.setColumnHidden(KEYS.index(key),key in self.view['hidden'])
        if all(k in self.view['hidden'] for k in ('name','short_id')):
            self.view['hidden']=[k for k in self.view['hidden'] if k!='name'];self.w.table.setColumnHidden(KEYS.index('name'),False)
        for key,width in self.view.get('widths',{}).items():self.w.table.setColumnWidth(KEYS.index(key),width)
        h.blockSignals(False)
    def header_changed(self,*_):
        if self.rendering:return
        h=self.w.table.horizontalHeader();self.view['order']=[KEYS[h.logicalIndex(i)] for i in range(h.count())];self.persist()
    def resized(self,index,old,new):
        if self.rendering or not 40<=new<=2000:return
        self.view.setdefault('widths',{})[KEYS[index]]=new;self.persist()
    def sort(self,index):
        key=KEYS[index];self.descending=not self.descending if key==self.sort_key else False;self.sort_key=key
        self.w.table.horizontalHeader().setSortIndicator(index,Qt.DescendingOrder if self.descending else Qt.AscendingOrder);self.render()
    def identity(self,row_number):
        item=self.w.table.item(row_number,0)
        ident=item.data(Qt.UserRole) if item else None
        return next((r for r in self.w.rows if r['device_id']==ident),None) if isinstance(ident,str) else None
    def query_matches(self,row):
        query=self.w.search.text().casefold()
        words=[display(row,key) for key in KEYS];words.extend(str(v) for v in row['_software'].values() if v is not None)
        words.extend(' '.join(a['supported']) for a in row['_connectivity'].values());words.append(row.get('location') or '')
        return query in ' '.join(words).casefold()
    def base_matches(self,row):
        group=self.w.group_filter.currentData();kind=self.w.type_filter.currentData()
        return self.query_matches(row) and (group is None or (not row['device_type'] if group=='__unknown__' else group==row['type_group'])) and (kind is None or (not row['device_type'] if kind=='__unknown__' else kind==row['device_type']))
    def render(self):
        if not hasattr(self.w,'rows'):return
        from PySide6.QtWidgets import QTableWidgetItem
        table=self.w.table;current=self.identity(table.currentRow()) if table.currentRow()>=0 else None;selected=current['device_id'] if current else None
        self.rendering=True;signals=table.blockSignals(True);table.clearSpans();table.setRowCount(0)
        try:
            from decimal import Decimal
            def order(row):
                value=Decimal(row.get('purchase_price') or '-1') if self.sort_key=='purchase_price' else display(row,self.sort_key).casefold()
                return value,row['device_id']
            rows=sorted(self.w.rows,key=order,reverse=self.descending)
            accepted=[r for r in rows if self.base_matches(r) and matches(r,self.view['filters'])]
            # Ungrouped view keeps hidden rows for legacy selection APIs and visible filtering semantics.
            def device(row,hidden=False):
                n=table.rowCount();table.insertRow(n)
                for c,(key,_) in enumerate(COLUMNS):
                    item=QTableWidgetItem(display(row,key));item.setData(Qt.UserRole,row['device_id']);item.setToolTip(row['device_id']);table.setItem(n,c,item)
                table.setRowHidden(n,hidden)
                if selected==row['device_id'] and not hidden and table.currentRow()<0:table.selectRow(n)
            def branch(members,level,path=(),ancestor_hidden=False):
                if level==len(self.view['groups']):
                    for row in members:device(row,ancestor_hidden)
                    return
                key=self.view['groups'][level]
                for (value,),bucket in groups(members,[key]):
                    prefix=path+((key,value),);n=table.rowCount();table.insertRow(n)
                    label=('  '*level)+('▸ ' if prefix in self.collapsed else '▾ ')+tr(dict(COLUMNS)[key])+': '+(tr(value) if key in ('current_state','physical_condition') else value or tr('Unknown'))+' ('+str(len({r['device_id'] for r in bucket}))+')'
                    first=next((KEYS.index(k) for k in self.view['order'] if k not in self.view['hidden']),1)
                    for c in range(len(COLUMNS)):
                        item=QTableWidgetItem(label if c==first else '');item.setToolTip(label);item.setData(Qt.UserRole,('group',prefix));item.setFlags(Qt.ItemIsEnabled|Qt.ItemIsSelectable);font=item.font();font.setBold(True);item.setFont(font);table.setItem(n,c,item)
                    table.setRowHidden(n,ancestor_hidden)
                    branch(bucket,level+1,prefix,ancestor_hidden or prefix in self.collapsed)
            if self.view['groups']:branch(accepted,0)
            else:
                for row in rows:device(row,row not in accepted)
            h=table.horizontalHeader();h.blockSignals(True)
            for i,(key,_) in enumerate(COLUMNS):
                table.setHorizontalHeaderItem(i,QTableWidgetItem(tr(dict(COLUMNS)[key])))
                if key not in self.view.get('widths',{}):table.setColumnWidth(i,180 if key in ('name','location','roles') else 140)
            h.blockSignals(False);self.restore_header()
            active='; '.join(tr(dict(COLUMNS)[k])+': '+((', '.join(x or tr('Unknown') for x in v[:3])+(' … ('+str(len(v))+')' if len(v)>3 else '')) if v else tr('No matches')) for k,v in self.view['filters'].items())
            self.summary.setText(str(len(accepted))+' / '+str(len(rows))+' '+tr('unique devices')+(' · '+active if active else '')+(' · '+tr('Role groups can repeat devices.') if 'roles' in self.view['groups'] else ''))
        finally:table.blockSignals(signals);self.rendering=False
    def clicked(self,item):
        value=item.data(Qt.UserRole)
        if isinstance(value,(tuple,list)) and value and value[0]=='group':
            path=tuple(tuple(p) for p in value[1]);self.collapsed.symmetric_difference_update({path});self.render()
    def filters_dialog(self):
        from PySide6.QtWidgets import QInputDialog
        labels=[tr(label) for _,label in COLUMNS];label,ok=QInputDialog.getItem(self.w,tr('Filters'),tr('Choose a column'),labels,0,False)
        if not ok:return
        key=KEYS[labels.index(label)];candidates=[r for r in self.w.rows if self.base_matches(r) and matches(r,self.view['filters'],skip=key)]
        counts={}
        for r in candidates:
            for v in set(values(r,key)):counts[v]=counts.get(v,0)+1
        for r in self.w.rows:
            for v in values(r,key):counts.setdefault(v,0)
        for v in self.view['filters'].get(key,[]):counts.setdefault(v,0)
        options=[(v,(tr(v) if key in ('current_state','physical_condition') else v or tr('Unknown'))+' ('+str(counts[v])+')') for v in sorted(counts)]
        dialog=ChoiceDialog('Filters',options,self.view['filters'].get(key),self.w,allow_all=True)
        if dialog.exec()!=QDialog.Accepted:return
        selected=dialog.selected()
        if selected is None:self.view['filters'].pop(key,None)
        else:self.view['filters'][key]=selected
        self.persist();self.render()
    def clear_filters(self):
        self.view['filters']={};self.w.search.clear();self.w.group_filter.setCurrentIndex(0);self.w.type_filter.setCurrentIndex(0);self.persist();self.render()
    def columns_dialog(self):
        dialog=ColumnsDialog(self.view['order'],self.view['hidden'],self.w)
        if dialog.exec()!=QDialog.Accepted:return
        self.view['order'],self.view['hidden']=dialog.result_view();self.restore_header();self.persist()
    def group_dialog(self):
        dialog=GroupDialog(self.view['groups'],self.w)
        if dialog.exec()!=QDialog.Accepted:return
        self.view['groups']=dialog.selected();self.collapsed.clear();self.persist();self.render()
