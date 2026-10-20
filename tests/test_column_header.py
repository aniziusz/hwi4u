"""Header filter clicks retain column identity without invoking sort or losing drafts."""
import unittest
from unittest.mock import patch
import test_desktop
from PySide6.QtCore import Qt
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication,QDialog
from list_view import KEYS

class ColumnHeader(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def test_one_click_targets_logical_column_after_reorder_and_scroll(self):
        w=self.window;w.show();h=w.table.horizontalHeader();QApplication.processEvents()
        h.moveSection(h.visualIndex(1),0);w.table.horizontalScrollBar().setValue(40);QApplication.processEvents()
        calls=[];h.filterRequested.disconnect();h.filterRequested.connect(calls.append)
        before=w.list_controller.sort_key,w.list_controller.descending;QTest.mouseClick(h.buttons[1],Qt.LeftButton)
        self.assertEqual(calls,[1]);self.assertEqual((w.list_controller.sort_key,w.list_controller.descending),before)
        self.assertIn('Name',h.buttons[1].accessibleName());self.assertEqual(h.buttons[1].geometry().right(),h.sectionViewportPosition(1)+h.sectionSize(1)-3)
    def test_direct_dialog_apply_cancel_active_indicator_and_unknown(self):
        w=self.window;w.store.save(dict(name='fictional',source='FICTIONAL TEST'));w.reload();w.begin_edit();w.inputs['name'].setText('pending name');pending=w.values();c=w.list_controller
        with patch('list_view.ChoiceDialog') as make,patch('PySide6.QtWidgets.QInputDialog.getItem') as column_picker:
            make.return_value.width.return_value=430;make.return_value.height.return_value=480
            make.return_value.exec.return_value=QDialog.Accepted;make.return_value.selected.return_value=['fictional'];c.filter_column(KEYS.index('name'));column_picker.assert_not_called()
        self.assertEqual(c.view['filters']['name'],['fictional']);self.assertIn('●',w.table.horizontalHeader().buttons[1].text());self.assertEqual(w.values(),pending)
        with patch('list_view.ChoiceDialog') as make:
            make.return_value.width.return_value=430;make.return_value.height.return_value=480
            make.return_value.exec.return_value=QDialog.Rejected;c.filter_column(1)
        self.assertEqual(c.view['filters']['name'],['fictional'])
        with patch('list_view.ChoiceDialog') as make:
            make.return_value.width.return_value=430;make.return_value.height.return_value=480
            make.return_value.exec.return_value=QDialog.Accepted;make.return_value.selected.return_value=None;c.filter_column(1)
        self.assertNotIn('name',c.view['filters']);self.assertNotIn('●',w.table.horizontalHeader().buttons[1].text())
    def test_hidden_columns_and_language_keep_button_labels_and_filters(self):
        w=self.window;c=w.list_controller;c.view['filters']={'name':['Example']};c.view['hidden'].append('name');c.restore_header();h=w.table.horizontalHeader();self.assertTrue(h.buttons[1].isHidden())
        c.view['hidden'].remove('name');c.restore_header()
        for lang in ('de','hu','en'):
            w.set_language(lang);self.assertIn('Example',c.view['filters']['name']);self.assertIn('●',h.buttons[1].text())
