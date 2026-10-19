"""Names, per-interface MAC/IP identities, history, conflicts and migration safety."""
import contextlib
import copy
import json
from pathlib import Path
import sqlite3
import unittest
from unittest.mock import patch
import test_desktop
from PySide6.QtWidgets import QTableWidgetItem,QMessageBox
from PySide6.QtTest import QTest
from device_store import DeviceStore
from network_identity import empty_network,hostname,mac_address,ip_address,validate_network,load_network
import inventory

BASE=test_desktop.BASE
class NetworkIdentity(unittest.TestCase):
    setUp=test_desktop.Desktop.setUp
    def known(self):
        data=empty_network();data.update(hostname='Firewall.Example.',source='TEST ONLY',observed_on='2026-10-18')
        data['interfaces']=[dict(interface_id='a'*32,label='WAN',mac_address='02-00-00-00-00-01',addresses=['192.0.2.10/24','2001:db8::10/64']),dict(interface_id='b'*32,label='LAN',mac_address='0200.0000.0002',addresses=['198.51.100.1/24'])]
        return data
    def test_live_name_uniqueness_unicode_and_length(self):
        first={'name':'Árvíz  szerver','source':'TEST ONLY'};self.store.save(first)
        w=self.window;w.inputs['name'].setText(' ÁRVÍZ szerver ')
        # Await the debounced UI result rather than assuming a fixed CI scheduling delay.
        for _ in range(100):
            if 'already exists' in w.name_feedback.text():break
            QTest.qWait(50)
        self.assertIn('already exists',w.name_feedback.text())
        w.inputs['name'].setText('ü'*100);w.check_name();self.assertIn('No duplicate',w.name_feedback.text())
        self.assertIn('100',w.inputs['name'].toolTip());self.assertIn('Unicode',w.inputs['name'].toolTip())
        w.inputs['name'].setText('ü'*101);w.check_name();self.assertIn('100',w.name_feedback.text())
        for value in ('x'*101,'line\nbreak','tab\there','bad\x00name'):
            with self.assertRaises(ValueError):self.store.save(dict(name=value,source='TEST ONLY'))
        self.store.save(dict(name='ü'*100,source='TEST ONLY'))
        # Current record may retain its own name; a concurrent new duplicate is still blocked on Save.
        original=next(r for r in self.store.devices() if r['device_id']==first['device_id'])
        self.assertIsNone(self.store.name_issue('ÁRVÍZ szerver',first['device_id']))
        self.store.save({**first,'name':'renamed'},original)
    def test_multiple_interfaces_ipv4_ipv6_history_and_conflict(self):
        data=dict(name='test',source='TEST ONLY',network=self.known());self.store.save(data)
        original=self.store.devices()[0];network=original['_network']
        self.assertEqual(network['hostname'],'firewall.example');self.assertEqual(len(network['interfaces']),2)
        self.assertEqual(next(r for r in network['interfaces'] if r['label']=='WAN')['mac_address'],'02:00:00:00:00:01')
        updated=copy.deepcopy(network);updated['hostname']='changed.example'
        self.store.save({**data,'network':updated},original)
        with contextlib.closing(self.store.connect()) as c:
            history=[json.loads(r[0]) for r in c.execute('SELECT profile_json FROM network_observations ORDER BY observation_id')]
            self.assertEqual([r['hostname'] for r in history],['firewall.example','changed.example'])
            with self.assertRaises(sqlite3.IntegrityError):c.execute('DELETE FROM network_observations')
        with self.assertRaisesRegex(ValueError,'Network details changed'):
            self.store.save({**data,'network':network},original)
    def test_invalid_addresses_atomic_and_unknown_allowed(self):
        for mutate in (lambda n:n.update(hostname='bad_name'),lambda n:n['interfaces'][0].update(mac_address='not mac'),lambda n:n['interfaces'][0].update(addresses=['300.1.1.1']),lambda n:n.update(evidence_status='verified',source=None)):
            n=self.known();mutate(n)
            with self.assertRaises(ValueError):self.store.save(dict(name='test',source='TEST ONLY',network=n))
            self.assertEqual(self.store.devices(),[])
        n=empty_network();n['interfaces']=[dict(label='port one',mac_address=None,addresses=[])]
        self.store.save(dict(name='test',source='TEST ONLY',network=n))
        self.assertIsNone(self.store.devices()[0]['_network']['interfaces'][0]['mac_address'])
    def test_gui_save_language_and_search(self):
        w=self.window;w.inputs['name'].setText('test');w.inputs['source'].setText('TEST ONLY')
        w.network_panel.load(validate_network(self.known()));before=w.values()
        for lang in ('de','hu','en'):
            w.set_language(lang);self.assertEqual(w.values(),before)
        self.assertTrue(w.save());self.assertEqual(w.network_panel.hostname.text(),'firewall.example')
        w.search.setText('2001:db8::10');self.assertFalse(w.table.isRowHidden(0))
        self.assertEqual(w.network_panel.table.rowCount(),2)
        w.network_panel.table.setCurrentCell(0,0);w.network_panel.remove_row();self.assertEqual(w.network_panel.table.rowCount(),1)
        w.cancel() if w.values()==w.baseline else None
    def test_schema16_upgrade_preserves_devices_and_adds_no_invented_values(self):
        db=self.root/'old.sqlite3'
        with contextlib.closing(sqlite3.connect(db)) as c:
            c.executescript((BASE/'tests/fixtures/schema-016.sql').read_text())
            c.execute("INSERT INTO devices(device_id,name,source) VALUES('OLD','existing','TEST ONLY')");c.commit()
            devices=c.execute('SELECT * FROM devices').fetchall();labels=c.execute('SELECT * FROM device_short_labels').fetchall()
            c.executescript((BASE/'migrations/017-network-identities.sql').read_text())
            self.assertEqual(devices,c.execute('SELECT * FROM devices').fetchall());self.assertEqual(labels,c.execute('SELECT * FROM device_short_labels').fetchall())
            self.assertEqual(c.execute('SELECT count(*) FROM device_network').fetchone()[0],0)
            inventory.check(c)
            c.executescript((BASE/'migrations/018-hwi4u.sql').read_text())
            c.executescript((BASE/'migrations/019-source-library.sql').read_text())
            c.executescript((BASE/'migrations/020-network-links.sql').read_text())
            c.executescript((BASE/'migrations/021-location.sql').read_text());c.executescript((BASE/'migrations/022-guided-locations.sql').read_text());c.executescript((BASE/'migrations/023-device-roles.sql').read_text());c.executescript((BASE/'migrations/024-device-identification.sql').read_text());c.executescript((test_desktop.BASE/'migrations/025-model-lifecycle.sql').read_text())
        self.assertEqual(DeviceStore(db).devices()[0]['_network'],empty_network())
    def test_normalization_and_distinct_network_scope(self):
        self.assertEqual(hostname('München.example'),'xn--mnchen-3ya.example')
        self.assertEqual(mac_address('020000000001'),'02:00:00:00:00:01')
        self.assertEqual(ip_address('2001:0DB8::1'),'2001:db8::1')
        n=self.known();n['interfaces'][1]['addresses']=['192.0.2.10/24'];validate_network(n)
        n['interfaces'][0]['addresses']=['192.0.2.10','192.0.2.10/24']
        with self.assertRaises(ValueError):validate_network(n)

    def test_name_save_race_and_direct_sql_audit(self):
        w=self.window;w.inputs['name'].setText('available');w.inputs['source'].setText('TEST ONLY');w.check_name()
        self.assertIn('No duplicate',w.name_feedback.text())
        DeviceStore(self.db).save(dict(name='AVAILABLE',source='OTHER EDITOR TEST'))
        with patch.object(QMessageBox,'warning'):
            self.assertFalse(w.save())
        self.assertEqual(len(self.store.devices()),1)
        with contextlib.closing(self.store.connect()) as c:
            c.execute("INSERT INTO devices(device_id,name,source) VALUES('SECOND','available','TEST ONLY')");c.commit()
            with self.assertRaisesRegex(ValueError,'Duplicate normalized'):inventory.check(c)
    def test_network_observation_removal_retains_prior_values(self):
        data=dict(name='test',source='TEST ONLY',network=self.known());self.store.save(data)
        original=self.store.devices()[0]
        self.store.save({**data,'network':empty_network()},original)
        saved=self.store.devices()[0];self.assertEqual(saved['_network'],empty_network())
        with contextlib.closing(self.store.connect()) as c:
            self.assertEqual(c.execute('SELECT count(*) FROM network_observations').fetchone()[0],2)
            self.assertEqual(c.execute('SELECT count(*) FROM network_interfaces').fetchone()[0],0)

    def test_busy_name_check_warns_without_writing(self):
        w=self.window;w.inputs['name'].setText('pending')
        with contextlib.closing(sqlite3.connect(self.db)) as other:
            other.execute('BEGIN EXCLUSIVE')
            w.check_name();self.assertIn('unavailable',w.name_feedback.text())
            other.rollback()
        w.check_name();self.assertIn('No duplicate',w.name_feedback.text())
        self.assertEqual(self.store.devices(),[])
