"""Port topology and deliberate wheel edits; all data disposable."""
import contextlib,json,sqlite3,unittest,uuid
from unittest.mock import patch
from PySide6.QtCore import Qt,QPoint,QPointF,QDate
from PySide6.QtGui import QWheelEvent
from PySide6.QtWidgets import QApplication,QComboBox,QScrollArea,QWidget,QVBoxLayout,QSpinBox,QDateEdit,QMessageBox
import test_desktop
from topology_store import TopologyStore
from topology_ui import LinkEditor,LinkManager
from desktop import OptionalDate
from network_identity import empty_network
from source_store import SourceStore
from ui_i18n import install

class Topology(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def setup_ports(self):
        self.ids=[]
        for n in range(3):
            net=empty_network();port=uuid.uuid4().hex;self.ids.append(port);net['interfaces']=[dict(interface_id=port,label='LAN',mac_address=None,addresses=[])]
            self.store.save(dict(name='test-device-'+str(n),source='TEST ONLY',network=net))
        self.links=TopologyStore(self.db)
    def data(self,a=0,b=1):return dict(endpoint_a=self.ids[a],endpoint_b=self.ids[b],medium='ethernet',state='planned',speed_mbps=None,source='TEST ONLY',observed_on=None,evidence_status='user_reported',source_ids=[],notes=None)
    def test_save_reversed_duplicate_multi_links_history_backup_and_stale(self):
        self.setup_ports();ident=self.links.save(self.data());row=self.links.list()[0]
        with self.assertRaisesRegex(ValueError,'already'):self.links.save(self.data(1,0))
        self.links.save(self.data(0,2));self.links.save(dict(row,state='observed',speed_mbps=1000),row)
        with self.assertRaisesRegex(ValueError,'changed'):self.links.remove(row)
        current=next(r for r in self.links.list() if r['link_id']==ident);self.links.remove(current)
        self.assertEqual(len(self.links.list()),1);self.assertTrue(list((self.root/'backups').glob('before-connection-*.sqlite3')))
        with contextlib.closing(self.store.connect()) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM network_link_history').fetchone()[0],4)
            last=json.loads(c.execute("SELECT snapshot_json FROM network_link_history WHERE action='remove'").fetchone()[0]);self.assertEqual(len(last['endpoints']),2)
            with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM network_link_history')
    def test_invalid_evidence_speed_endpoints_and_rollback(self):
        self.setup_ports()
        for change in [dict(endpoint_b=self.ids[0]),dict(endpoint_b='missing'),dict(speed_mbps='nan'),dict(speed_mbps=-1),dict(observed_on='2026-02-30'),dict(evidence_status='verified')]:
            with self.assertRaises(ValueError):self.links.save(dict(self.data(),**change))
        with patch('inventory.exclusive',side_effect=OSError('backup failed')):
            with self.assertRaises(OSError):self.links.save(self.data())
        self.assertEqual(self.links.list(),[])
    def test_evidence_reuse_and_verified_date(self):
        self.setup_ports();source=SourceStore(self.db).save(dict(kind='observation',title='test cable tracing',body='TEST ONLY',evidence_status='user_reported'))
        self.links.save(dict(self.data(),source=None,source_ids=[source],evidence_status='verified',observed_on='2026-10-18'))
        row=self.links.list()[0];self.assertIn(source,row['source']);self.assertEqual(row['source_ids'],[source])
    def test_link_survives_port_edits_and_blocks_port_device_deletion(self):
        self.setup_ports();self.links.save(self.data());row=self.store.devices()[0];net=__import__('copy').deepcopy(row['_network']);net['interfaces'][0]['label']='renamed'
        self.store.save(dict(row,network=net),row);row=self.store.devices()[0]
        with self.assertRaisesRegex(ValueError,'connection records'):self.store.delete(row)
        with self.assertRaisesRegex(ValueError,'connection records'):self.store.save(dict(row,network=empty_network()),row)
        self.assertEqual(len(self.links.list()),1)
        self.links.remove(self.links.list()[0]);self.store.delete(self.store.devices()[0])
        with contextlib.closing(self.store.connect()) as c:self.assertEqual(c.execute('SELECT count(*) FROM network_link_history').fetchone()[0],2)
    def test_editor_explicit_save_cancel_translations(self):
        self.setup_ports()
        for lang in ('en','de','hu'):
            install(lang);dialog=LinkEditor(self.links,OptionalDate);self.addCleanup(dialog.deleteLater)
            dialog.a.setCurrentIndex(dialog.a.findData(self.ids[0]));dialog.b.setCurrentIndex(dialog.b.findData(self.ids[1]));dialog.medium.setCurrentIndex(dialog.medium.findData('ethernet'));dialog.source.setText('TEST ONLY')
            self.assertTrue(dialog.save_button.text());self.assertEqual(dialog.value()['medium'],'ethernet');dialog.reject();self.assertEqual(self.links.list(),[])
        dialog=LinkEditor(self.links,OptionalDate);dialog.a.setCurrentIndex(1);dialog.b.setCurrentIndex(2);dialog.medium.setCurrentIndex(1);dialog.source.setText('TEST ONLY');dialog.save();self.assertEqual(len(self.links.list()),1);dialog.deleteLater()
        manager=LinkManager(self.db,OptionalDate);self.assertEqual(manager.table.rowCount(),1);manager.deleteLater();install('en')

class Wheel(unittest.TestCase):
    def send(self,widget):
        event=QWheelEvent(QPointF(5,5),QPointF(widget.mapToGlobal(QPoint(5,5))),QPoint(),QPoint(0,-120),Qt.NoButton,Qt.NoModifier,Qt.ScrollUpdate,False);QApplication.sendEvent(widget,event)
    def test_closed_fields_do_not_change_and_form_scrolls(self):
        install('en');area=QScrollArea();content=QWidget();layout=QVBoxLayout(content);combo=QComboBox();combo.addItems(['one','two','three']);combo.setCurrentIndex(1);layout.addWidget(combo);date=QDateEdit(QDate(2026,10,18));date.setCalendarPopup(True);layout.addWidget(date);number=QSpinBox();number.setValue(5);layout.addWidget(number);content.setMinimumHeight(1000);area.setWidget(content);area.resize(300,200);area.show();test_desktop.APP.processEvents()
        for widget in (combo,date,number):
            widget.setFocus();self.send(widget)
        self.assertEqual(combo.currentIndex(),1);self.assertEqual(date.date(),QDate(2026,10,18));self.assertEqual(number.value(),5);self.assertGreater(area.verticalScrollBar().value(),0)
        combo.setEditable(True);self.send(combo.lineEdit());self.assertEqual(combo.currentIndex(),1)
        combo.setFocus();QApplication.sendEvent(combo,__import__('PySide6.QtGui',fromlist=['QKeyEvent']).QKeyEvent(__import__('PySide6.QtCore',fromlist=['QEvent']).QEvent.KeyPress,Qt.Key_Down,Qt.NoModifier));self.assertEqual(combo.currentIndex(),2)
        combo.showPopup();test_desktop.APP.processEvents();self.assertTrue(combo.view().isVisible())
        wheel=QWheelEvent(QPointF(5,5),QPointF(5,5),QPoint(),QPoint(0,-120),Qt.NoButton,Qt.NoModifier,Qt.ScrollUpdate,False)
        self.assertFalse(test_desktop.APP.inventory_wheel_guard.eventFilter(combo,wheel));combo.hidePopup()
        calendar=date.calendarWidget();self.assertFalse(test_desktop.APP.inventory_wheel_guard.eventFilter(calendar,wheel))
        area.close();area.deleteLater()

class Upgrade(unittest.TestCase):
    def test_schema19_upgrade_preserves_ports_sources_and_adds_no_guessed_links(self):
        import tempfile
        from pathlib import Path
        with tempfile.TemporaryDirectory() as tmp:
            db=Path(tmp)/'hardware.sqlite3'
            with contextlib.closing(sqlite3.connect(db)) as c:
                c.executescript((test_desktop.BASE/'tests/fixtures/schema-019.sql').read_text())
                c.execute("INSERT INTO devices(device_id,name,source) VALUES('test','test','TEST ONLY')")
                c.execute("INSERT INTO device_network(device_id,evidence_status) VALUES('test','uncertain')")
                c.execute("INSERT INTO network_interfaces(interface_id,device_id,label) VALUES(?, 'test','LAN')",('a'*32,));c.commit()
                tables=[r[0] for r in c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")];before={t:c.execute('SELECT * FROM '+t).fetchall() for t in tables};old_columns={t:[r[1] for r in c.execute('PRAGMA table_info('+t+')')] for t in tables}
                c.executescript((test_desktop.BASE/'migrations/020-network-links.sql').read_text())
                c.executescript((test_desktop.BASE/'migrations/021-location.sql').read_text());c.executescript((test_desktop.BASE/'migrations/022-guided-locations.sql').read_text());c.executescript((test_desktop.BASE/'migrations/023-device-roles.sql').read_text());c.executescript((test_desktop.BASE/'migrations/024-device-identification.sql').read_text())
                for t,rows in before.items():self.assertEqual(c.execute('SELECT '+','.join(old_columns[t])+' FROM '+t).fetchall(),rows,t)
                self.assertEqual(c.execute('SELECT count(*) FROM network_links').fetchone()[0],0)
                __import__('inventory').check(c)

class Recovery(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    setup_ports=Topology.setup_ports
    data=Topology.data
    def test_full_backup_restores_connection_evidence_and_history(self):
        import zipfile
        from photo_files import backup_bundle
        from pathlib import Path
        self.setup_ports();self.links.save(self.data());out=self.root/'topology.zip';backup_bundle(self.db,out)
        folder=self.root/'restored'
        with zipfile.ZipFile(out) as z:z.extractall(folder)
        recovered=TopologyStore(folder/'hardware.sqlite3');self.assertEqual(recovered.list(),self.links.list())
        with contextlib.closing(recovered.connect()) as c:self.assertEqual(c.execute('SELECT count(*) FROM network_link_history').fetchone()[0],1)
