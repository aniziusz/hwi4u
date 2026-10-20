"""Source alternatives, editable language discovery, and invalidation of test evidence."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import test_desktop
from desktop import Window
from language_catalog import Catalogues, CATALOGUES, text_hash
from source_store import SourceStore
from update_runtime import source_files
from validation import run_full


class DeviceEvidence(unittest.TestCase):
    setUp = test_desktop.Desktop.setUp

    def test_live_alternatives_and_missing_evidence_focus(self):
        w = self.window
        w.inputs['name'].setText('Fictional evidence test')
        self.assertFalse(w.check_device_evidence())
        with patch.object(w, 'error') as error:
            self.assertFalse(w.save())
            self.assertIn('OR choose', str(error.call_args.args[0]))
        self.assertEqual(self.store.devices(), [])
        w.inputs['source'].setText('Fictional user report')
        self.assertTrue(w.check_device_evidence()); self.assertTrue(w.save())
        row = self.store.devices()[0]
        ident = SourceStore(self.db).save(dict(kind='observation', title='Fictional label', body='TEST ONLY', evidence_status='user_reported'))
        w.inputs['source'].clear()
        w.source_selectors['device'].load([ident], row['device_id'])
        w.source_selectors['device'].changed.emit()
        self.assertTrue(w.check_device_evidence()); self.assertTrue(w.save())
        self.assertEqual(self.store.devices()[0]['_sources']['device'], [ident])

    def test_other_sections_do_not_satisfy_device_provenance(self):
        w = self.window; w.inputs['name'].setText('Fictional missing provenance')
        ident = SourceStore(self.db).save(dict(kind='observation', title='Fictional OS settings', body='TEST ONLY', evidence_status='user_reported'))
        w.source_selectors['software'].load([ident])
        with patch.object(w, 'error'):
            self.assertFalse(w.save())
        self.assertEqual(self.store.devices(), [])
        for language in ('de', 'hu', 'en'):
            w.set_language(language)
            self.assertIn('*', w.source_selectors['device'].parentWidget().title())
            self.assertTrue(w.evidence_feedback.text())


class LanguageCatalogues(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.folder = Path(self.tmp.name) / 'locales'
        shutil.copytree(test_desktop.BASE / 'locales', self.folder)

    def edit(self, name, edit):
        path = self.folder / name; data = json.loads(path.read_text(encoding='utf-8'))
        edit(data); path.write_text(json.dumps(data, ensure_ascii=False), encoding='utf-8')

    def test_complete_migration_and_packaging(self):
        self.assertFalse(CATALOGUES.errors)
        self.assertGreater(len(CATALOGUES.messages), 700)
        files = source_files(test_desktop.BASE)
        for language in ('en', 'de', 'hu'):
            self.assertIn('locales/' + language + '.json', files)
        self.assertEqual(CATALOGUES.translate('Manufacturer', 'hu'), 'Gyártó')

    def test_new_language_discovered_with_partial_english_fallback(self):
        data = json.loads((self.folder / 'de.json').read_text(encoding='utf-8'))
        data.update(language='fr', name='Français', qt_locale='fr_FR')
        ident = CATALOGUES.by_source['Manufacturer']
        data['messages'] = {ident: dict(text='Fabricant', source_sha256=text_hash('Manufacturer'))}
        (self.folder / 'fr.json').write_text(json.dumps(data), encoding='utf-8')
        c = Catalogues(self.folder)
        self.assertIn('fr', c.locales)
        self.assertEqual(c.translate('Manufacturer', 'fr'), 'Fabricant')
        self.assertEqual(c.translate('Model', 'fr'), 'Model')
        self.assertEqual(c.translate('User-owned Unicode Árvíz', 'fr'), 'User-owned Unicode Árvíz')
        # Qt language menus/date locale work without a hardcoded French branch.
        import ui_i18n
        with patch.object(ui_i18n, 'CATALOGUES', c), patch.object(ui_i18n, 'LANGUAGES', {k:v['name'] for k,v in c.locales.items()}):
            ui_i18n.install('fr')
            self.assertEqual(ui_i18n.tr('Manufacturer'), 'Fabricant')
            self.assertEqual(ui_i18n.locale_name('fr'), 'fr_FR')
        ui_i18n.install('en')

    def test_stale_placeholder_duplicate_and_invalid_files_fail_safely(self):
        ident = CATALOGUES.by_source['{0} is required.']
        self.edit('de.json', lambda d: d['messages'][ident].update(text='Fehlt {wrong}'))
        c = Catalogues(self.folder)
        self.assertEqual(c.translate('{0} is required.', 'de'), '{0} is required.')
        self.assertTrue(c.errors)
        (self.folder / 'hu.json').write_text('{"format":1,"format":1}')
        c = Catalogues(self.folder)
        self.assertNotIn('hu', c.locales)
        self.edit('en.json', lambda d: d['messages'][CATALOGUES.by_source['Manufacturer']].update(text='Maker'))
        c = Catalogues(self.folder)
        self.assertEqual(c.translate('Manufacturer', 'en'), 'Maker')
        self.assertEqual(c.translate('Manufacturer', 'de'), 'Maker')
        self.assertIn('stale translation', '\n'.join(c.errors))


class ValidationEvidence(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'source'; self.root.mkdir()
        (self.root / 'tests').mkdir()
        self.test = self.root / 'tests/test_example.py'
        self.test.write_text('import unittest\nclass Example(unittest.TestCase):\n def test_example(self): self.assertTrue(True)\n')
        self.evidence = Path(self.tmp.name) / 'evidence'

    def test_exact_full_run_reused_and_source_environment_tamper_invalidated(self):
        # Keep this fixture fast; actual dependency collection is separately exercised below.
        def inputs(root, env):
            from validation import sha, canonical
            return dict(source={k:sha(v) for k,v in source_files(root).items()}, env=sha(canonical(env)))
        with patch('validation.fingerprint', side_effect=inputs):
            first = run_full(self.root, self.evidence)
            self.assertFalse(first['reused']); self.assertEqual(first['tests_run'], 1)
            with patch('validation.subprocess.run', side_effect=AssertionError('Must not run again')):
                self.assertTrue(run_full(self.root, self.evidence)['reused'])
            receipt = next(p for p in self.evidence.glob('*.json') if not p.name.startswith('reuse-'))
            data = json.loads(receipt.read_text()); data['record']['tests_run'] = 999
            receipt.write_text(json.dumps(data))
            self.assertFalse(run_full(self.root, self.evidence)['reused'])
            with patch('validation.subprocess.run', side_effect=subprocess.TimeoutExpired([],600)):
                with self.assertRaises(RuntimeError):run_full(self.root,self.evidence,reuse=False)
            self.assertFalse(run_full(self.root,self.evidence)['reused'])
            self.test.write_text(self.test.read_text() + '\n# changed input\n')
            self.assertFalse(run_full(self.root, self.evidence)['reused'])
            with patch.dict(os.environ, {'HWI4U_TEST_FINGERPRINT': 'different'}):
                self.assertFalse(run_full(self.root, self.evidence)['reused'])
            self.test.write_text('import unittest\nclass Broken(unittest.TestCase):\n def test_failure(self): self.fail("TEST FAILURE")\n')
            for _ in range(2):
                with self.assertRaises(RuntimeError): run_full(self.root, self.evidence)

    def test_dependency_fingerprint_present_and_private(self):
        from validation import fingerprint
        result = fingerprint(self.root, {'EXAMPLE_SECRET': 'not-to-be-stored'})
        self.assertNotIn('not-to-be-stored', json.dumps(result))
        self.assertIn('PySide6_Essentials', result['dependencies'])
        self.assertIn('executable_sha256', result)


if __name__ == '__main__': unittest.main()
