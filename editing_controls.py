"""Shared view/edit actions and Basic/Details visibility; never duplicate form values."""
import sys
from PySide6.QtCore import Qt
from PySide6.QtGui import QAction,QActionGroup,QKeySequence
from PySide6.QtWidgets import (QWidget,QHBoxLayout,QPushButton,QLabel,QLineEdit,
    QComboBox,QCheckBox,QDateEdit,QTableWidget,QAbstractItemView,QFormLayout)
from ui_i18n import tr,apply,LANGUAGES

BASIC_FIELDS={'name','manufacturer','model','device_type','location','source','current_state','physical_condition'}
BASIC_CARDS={'identity','location','condition','evidence'}


def build_menus(w):
    bar=w.menuBar();bar.setNativeMenuBar(sys.platform=='darwin')
    w.actions={};menus={name:bar.addMenu(name) for name in ('File','Edit','View','Tools','Help')}
    for menu in menus.values():menu.setToolTipsVisible(True)
    def action(menu,key,label,callback,shortcut=None):
        a=QAction(label,w);a.triggered.connect(lambda checked=False:callback());menus[menu].addAction(a)
        if shortcut:a.setShortcut(shortcut)
        w.actions[key]=a;return a
    action('File','new','New device',w.new,QKeySequence.New)
    action('File','save','Save changes',w.save,QKeySequence.Save)
    from ui_help import BUTTONS
    w.actions['save'].setToolTip(BUTTONS.get('Save device',('Save changes',))[0])
    action('File','backup','Full backup',w.full_backup)
    quit_action=action('File','quit','Quit HWI4U',lambda:w.editor_root().close(),QKeySequence.Quit);quit_action.setMenuRole(QAction.QuitRole)
    action('Edit','edit','Edit device',w.begin_edit,'Ctrl+E')
    action('Edit','cancel','Cancel changes',w.cancel,'Esc')
    w.actions['cancel'].setToolTip(BUTTONS.get('Cancel changes',('Cancel changes',))[0])
    action('Edit','delete','Delete device…',w.delete_device)
    group=QActionGroup(w);group.setExclusive(True)
    for key,label,details in [('basic','Basic',False),('details','Details',True)]:
        a=action('View',key,label,lambda value=details:w.set_details(value));a.setCheckable(True);group.addAction(a);a.setChecked(not details)
    action('View','search','Find devices',lambda:w.search.setFocus(),QKeySequence.Find)
    action('View','filters','Filters…',lambda:w.list_controller.filters_dialog())
    action('View','columns','Columns…',lambda:w.list_controller.columns_dialog())
    action('View','group','Group by…',lambda:w.list_controller.group_dialog())
    action('View','clear_filters','Clear filters',lambda:w.list_controller.clear_filters())
    action('View','refresh','Refresh',w.refresh,QKeySequence.Refresh)
    action('Tools','types','Manage types',w.manage_types)
    action('Tools','connections','Manage connection choices…',w.manage_connections)
    action('Tools','links','Network connections…',w.manage_network_links)
    action('Tools','other','Open the other client',w.open_other_client)
    w.language_menu=menus['Tools'].addMenu('Language');w.language_actions={};languages=QActionGroup(w);languages.setExclusive(True)
    from PySide6.QtWidgets import QApplication
    for code,label in LANGUAGES.items():
        a=w.language_menu.addAction(label);a.setCheckable(True);a.setChecked(code==QApplication.instance().inventory_language);languages.addAction(a)
        a.triggered.connect(lambda checked=False,key=code:w.set_language(key));w.language_actions[code]=a
    w.about_action=action('Help','about','About HWI4U…',w.show_about);w.about_action.setMenuRole(QAction.AboutRole)
    w.about_action.setToolTip('Application version, data location, license and backup information.')
    action('Help','guide','Open user guide',w.open_guide,QKeySequence.HelpContents)
    action('Help','updates','Check for local updates',w.show_update_status)


def action_button(action,parent):
    button=QPushButton(parent);button.setAutoDefault(False);button.setProperty('_literal_text',True)
    def sync():
        button.setText(action.text());button.setEnabled(action.isEnabled())
        button.setCheckable(action.isCheckable());button.setChecked(action.isChecked())
        button.setToolTip(action.toolTip())
    action.changed.connect(sync);button.clicked.connect(lambda checked=False:(action.trigger(),sync()));sync()
    return button


def install_controls(w,outer):
    w.mode_bar=QWidget();row=QHBoxLayout(w.mode_bar);row.setContentsMargins(0,0,0,0)
    for key in ('basic','details'):row.addWidget(action_button(w.actions[key],w.mode_bar))
    w.mode_hint=QLabel();w.mode_hint.setWordWrap(True);row.addWidget(w.mode_hint,1)
    w.edit_button=action_button(w.actions['edit'],w.mode_bar);row.addWidget(w.edit_button)
    outer.insertWidget(outer.indexOf(w.splitter),w.mode_bar)
    w.action_bar=QWidget();foot=QHBoxLayout(w.action_bar);foot.setContentsMargins(0,0,0,0)
    w.edit_status=QLabel();w.edit_status.setWordWrap(True);foot.addWidget(w.edit_status,1)
    w.cancel_button=action_button(w.actions['cancel'],w.action_bar);w.save_button=action_button(w.actions['save'],w.action_bar)
    foot.addWidget(w.cancel_button);foot.addWidget(w.save_button);outer.addWidget(w.action_bar)
    # Compatibility identity for existing toolbar callers: one Save action, one button.
    w.toolbar_buttons['Save device']=w.save_button
    for key,property_name in [('Edit device','edit'),('Delete device…','delete')]:
        old=w.toolbar_buttons[key]
        w.actions[property_name].changed.connect(lambda button=old,a=w.actions[property_name]:button.setEnabled(a.isEnabled()))
    w.toolbar_buttons['Edit device'].hide()  # Edit is beside the mode status, once.


def form_controls(w):
    roots=[*w.inputs.values(),w.type_group,w.location_panel,w.lifecycle_panel,w.network_panel,
           w.software_panel,*w.connection_panels.values()]
    seen=set()
    for root in roots:
        for widget in [root,*root.findChildren(QWidget)]:
            if id(widget) not in seen:seen.add(id(widget));yield widget


def set_editing(w,editing):
    w.editing=bool(editing) and not getattr(w,'deleted',False);editing=w.editing
    if not hasattr(w,'action_bar'):return
    for widget in form_controls(w):
        if isinstance(widget,QLineEdit):widget.setReadOnly(not editing or widget is w.inputs['device_id'])
        elif isinstance(widget,(QComboBox,QCheckBox)):widget.setEnabled(editing)
        elif isinstance(widget,QDateEdit):widget.setReadOnly(not editing)
        elif isinstance(widget,QTableWidget):
            if widget.property('_edit_triggers') is None:widget.setProperty('_edit_triggers',widget.editTriggers().value)
            widget.setEditTriggers(QAbstractItemView.EditTrigger(widget.property('_edit_triggers')) if editing else QAbstractItemView.NoEditTriggers)
            for row in range(widget.rowCount()):
                for col in range(widget.columnCount()):
                    item=widget.item(row,col)
                    if item is None:continue
                    old=item.data(Qt.UserRole+98)
                    if not editing:
                        if old is None:item.setData(Qt.UserRole+98,item.flags().value)
                        item.setFlags(item.flags() & ~Qt.ItemIsEditable & ~Qt.ItemIsUserCheckable)
                    elif old is not None:item.setFlags(Qt.ItemFlag(old));item.setData(Qt.UserRole+98,None)
        elif isinstance(widget,QPushButton):
            label=widget.property('_i18n_source_text') or widget.text()
            widget.setEnabled(editing or label=='Find installed versions…')
    # Restore conditional editability without clearing unknown values.
    for date in w.findChildren(QWidget):
        if date.__class__.__name__=='OptionalDate':date.editor.setEnabled(date.known.isChecked())
    known=w.software_panel.os_status.currentData()=='recorded'
    for control in (w.software_panel.family,w.software_panel.name,w.software_panel.version):control.setEnabled(known if editing else isinstance(control,QLineEdit) and known)
    w.software_panel.firmware.setEnabled(w.software_panel.firmware_status.currentData()=='recorded')
    w.lifecycle_panel.read_only=not editing;w.location_panel.read_only=not editing
    for selector in w.source_selectors.values():selector.set_read_only(not editing)
    for button in (w.role_button,w.tag_button,w.model_button,w.merchant_fix):button.setEnabled(editing)
    for name in ('add_photo_button','detach_photo_button','add_manual_button','edit_manual_button','detach_manual_button'):
        if hasattr(w,name):getattr(w,name).setEnabled(editing and w.original is not None)
    w.refresh_name_suggestion()
    w.connections_button.setEnabled(editing)
    for key,value in [('edit',not editing and not getattr(w,'deleted',False)),('save',editing),('cancel',editing),('delete',editing and w.original is not None),('links',editing)]:w.actions[key].setEnabled(value)
    w.edit_button.setVisible(not editing);w.save_button.setVisible(editing);w.cancel_button.setVisible(editing)
    w.edit_status.setText('Editing — save or cancel your changes.' if editing else 'View mode — choose Edit device to make changes.')
    apply(w.edit_status)


def basic_widget(w,widget):
    if widget in (w.short_id,w.type_group,w.name_feedback,w.name_suggestion_panel,w.tag_button,w.location_panel,w.source_selectors['device'].parentWidget()):return True
    return any(widget is w.inputs[key] for key in BASIC_FIELDS)


def set_details(w,details):
    w.details_mode=bool(details)
    if not hasattr(w,'mode_bar'):return
    w.actions['basic'].setChecked(not details);w.actions['details'].setChecked(details)
    w.mode_hint.setText('All properties are available.' if details else 'Everyday properties. Other saved values are retained in Details.')
    if w.lifecycle_panel.feedback.text():w.mode_hint.setText(tr(w.mode_hint.text())+' '+tr('Lifecycle details need attention.'))
    apply(w.mode_hint)
    if hasattr(w,'workspace'):
        w.workspace.set_details(details)
    else:
        for row in range(w.quick_form.rowCount()):
            item=w.quick_form.itemAt(row,QFormLayout.FieldRole)
            widget=item.widget() if item else None
            visible=details or widget is w.form_title or (widget is not None and basic_widget(w,widget))
            w.quick_form.setRowVisible(row,visible)
        # A merchant suggestion must not become visible merely by toggling Details.
        w.merchant_fix.setVisible(details and bool(getattr(w,'merchant_suggestion',None)))


def reveal_validation(w,error):
    text=str(error).lower();key='identity';target=w.inputs['name']
    mapping=[(('purchase','price','currency','installation','scrapped'),'purchase',w.inputs['purchase_date']),
             (('lifecycle','release','warranty','support'),'lifecycle',w.lifecycle_section),
             (('software','firmware','operating'),'software',w.software_panel),
             (('protocol',),'protocol',w.connection_panels['protocol']),
             (('interface','connectivity'),'interface',w.connection_panels['interface']),
             (('network','hostname','mac','ip address'),'network',w.network_panel),
             (('serial','manufacturer','model'),'location',w.inputs['serial_number']),
             (('role',),'identity',w.role_button),
             (('tag',),'identity',w.tag_button),
             (('source','evidence'),'evidence',w.inputs['source'])]
    for words,section,widget in mapping:
        if any(word in text for word in words):key=section;target=widget;break
    if key not in BASIC_CARDS or target.isHidden():w.set_details(True)
    if hasattr(w,'workspace'):w.workspace.tree.setCurrentItem(w.workspace.items[key])
    else:
        for section in [w.lifecycle_section,*w.sections]:
            if target is section or target is section.body:section.header.setChecked(True)
    w.form_scroll.ensureWidgetVisible(target);target.setFocus()
