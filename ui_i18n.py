"""Live UI translation; database identifiers and user-entered text stay unchanged."""
import json
import os
from pathlib import Path
import re
import tempfile
from PySide6.QtCore import QObject,QEvent,QTranslator,QLocale
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (QApplication,QWidget,QLabel,QPushButton,QCheckBox,QGroupBox,
    QComboBox,QLineEdit,QTableWidget,QMenu,QDateEdit,QToolButton)

from language_catalog import CATALOGUES
LANGUAGES={code:data['name'] for code,data in CATALOGUES.locales.items()}
APP_VERSION='0.21.0'
RELEASE_DATE='2026-10-20'

def locale_name(code):
    return CATALOGUES.locales.get(code,CATALOGUES.locales['en'])['qt_locale']

def tr(text):
    lang=getattr(QApplication.instance(),'inventory_language','en')
    # Qt mnemonic markers are display-only.
    bare=text.replace('&','')
    entry=CATALOGUES.translate(text,lang)
    if entry!=text or lang=='en':return entry
    patterns=(
      (r'^Saved (.+)\. Pre-save backup: (.+)$','Saved {0}. Pre-save backup: {1}'),
      (r'^Verified full backup saved: (.+)$','Verified full backup saved: {0}'),
      (r'^Photo list unavailable: (.+)$','Photo list unavailable: {0}'),
      (r'^Original image • (.+)$','Original image • {0}'),
      (r'^Information source is required for (interface|protocol) connectivity\.$','Information source is required for {0} connectivity.'),
      (r'^(.+): choose a valid calendar date\.$','{0}: choose a valid calendar date.'),
      (r'^(interface|protocol): recorded needs at least one (supported|in use) choice; unknown/none must have no choices\.$','{0}: recorded needs at least one {1} choice; unknown/none must have no choices.'),
      (r'^Unknown (interface|protocol) choice; refresh the lists\.$','Unknown {0} choice; refresh the lists.'),
      (r'^Could not decode this image: (.+)$','Could not decode this image: {0}'),
      (r'^(.+) is required\.$','{0} is required.'),
    )
    for pattern,key in patterns:
        match=re.match(pattern,text)
        if match and key in CATALOGUES.by_source:
            semantic={'{0} is required.','{0}: choose a valid calendar date.','Information source is required for {0} connectivity.','{0}: recorded needs at least one {1} choice; unknown/none must have no choices.','Unknown {0} choice; refresh the lists.'}
            args=[tr(v) if key in semantic else v for v in match.groups()]
            return CATALOGUES.translate(key,lang).format(*args)
    return text

class InventoryTranslator(QTranslator):
    def isEmpty(self):return False
    def translate(self,context,source,disambiguation=None,n=-1):
        value=tr(source)
        return value if value!=source else ''

def _text(obj,key,current,setter):
    previous=obj.property('_i18n_last_'+key)
    source=obj.property('_i18n_source_'+key) if current==previous else current
    if source is None:source=current
    translated=tr(source)
    obj.setProperty('_i18n_source_'+key,source)
    obj.setProperty('_i18n_last_'+key,translated)
    if translated!=current:setter(translated)

def apply(root):
    widgets=[root]+root.findChildren(QWidget)
    for w in widgets:
        if not w.property('_literal_title') and w.isWindow():_text(w,'title',w.windowTitle(),w.setWindowTitle)
        if isinstance(w,(QLabel,QPushButton,QCheckBox,QToolButton)) and not w.property('_literal_text'):
            _text(w,'text',w.text(),w.setText)
        if isinstance(w,QGroupBox):_text(w,'group_title',w.title(),w.setTitle)
        if isinstance(w,QMenu):_text(w,'menu_title',w.title(),w.setTitle)
        if isinstance(w,QLineEdit):_text(w,'placeholder',w.placeholderText(),w.setPlaceholderText)
        if w.toolTip():_text(w,'tip',w.toolTip(),w.setToolTip)
        if isinstance(w,QComboBox) and (not w.isEditable() or w.property('_searchable_choices')):
            for n in range(w.count()):
                if w.itemData(n,275):continue  # Literal user-entered location paths.
                # Only fixed UI choices; shared catalogue values remain canonical.
                source=w.itemData(n,273)
                last=w.itemData(n,274)
                text=w.itemText(n)
                if text!=last:source=text
                if source is None:source=text
                value=tr(source)
                blocked=w.blockSignals(True);w.setItemText(n,value);w.setItemData(n,source,273);w.setItemData(n,value,274);w.blockSignals(blocked)
                if w.itemData(n) is not None:w.setItemData(n,tr('Stored value: ')+str(w.itemData(n)),3)
        if isinstance(w,QTableWidget):
            for n in range(w.columnCount()):
                item=w.horizontalHeaderItem(n)
                if item:
                    source=item.data(273);last=item.data(274)
                    if item.text()!=last:source=item.text()
                    if source is None:source=item.text()
                    item.setData(273,source);item.setData(274,tr(source));item.setText(tr(source))
            if not w.property('_managed_columns'):w.resizeColumnsToContents()
        if isinstance(w,QDateEdit):
            locale=QLocale(locale_name(getattr(QApplication.instance(),'inventory_language','en')))
            w.setLocale(locale);w.calendarWidget().setLocale(locale)
    for action in root.findChildren(QAction):
        _text(action,'action',action.text(),action.setText)
        if action.toolTip():_text(action,'action_tip',action.toolTip(),action.setToolTip)

class ShowFilter(QObject):
    def eventFilter(self,obj,event):
        if event.type()==QEvent.Show and isinstance(obj,QWidget):
            from ui_help import BUTTONS
            for button in obj.findChildren(QPushButton):
                source=button.property('_i18n_source_text') or button.text()
                if not button.toolTip() and source in BUTTONS:button.setToolTip(BUTTONS[source][0])
            apply(obj)
        return False

def install(language):
    if language not in LANGUAGES:raise ValueError('Unsupported interface language')
    app=QApplication.instance();app.inventory_language=language
    from wheel_guard import install_wheel_guard
    install_wheel_guard(app)
    if not hasattr(app,'inventory_translator'):
        app.inventory_translator=InventoryTranslator(app);app.installTranslator(app.inventory_translator)
        app.inventory_show_filter=ShowFilter(app);app.installEventFilter(app.inventory_show_filter)
    QLocale.setDefault(QLocale(locale_name(language)))
    for widget in app.topLevelWidgets():apply(widget)

def read_language(folder):
    try:
        language=json.loads((Path(folder)/'ui-settings.json').read_text()).get('language','en')
        return language if language in LANGUAGES else 'en'
    except (OSError,ValueError,TypeError,AttributeError):return 'en'

def write_language(folder,language):
    if language not in LANGUAGES:raise ValueError('Unsupported interface language')
    target=Path(folder)/'ui-settings.json'
    fd,name=tempfile.mkstemp(prefix='.ui-settings-',dir=folder)
    try:
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump({'language':language},f)
        os.replace(name,target)
    finally:
        Path(name).unlink(missing_ok=True)


from functools import wraps
import inspect
def localized(method):
    positional=sum(p.kind in (p.POSITIONAL_ONLY,p.POSITIONAL_OR_KEYWORD) for p in inspect.signature(method).parameters.values())-1
    @wraps(method)
    def wrapped(self,*args,**kwargs):
        result=method(self,*args[:positional],**kwargs)
        apply(self)
        return result
    return wrapped
