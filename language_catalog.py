"""Validated, discoverable UTF-8 catalogues. No Qt dependency or user data writes."""
import hashlib
import json
from pathlib import Path
import re
from string import Formatter


def text_hash(text):
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


def placeholders(text):
    return sorted(field for _, field, _, _ in Formatter().parse(text) if field is not None)


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError('Duplicate catalogue key: ' + key)
        value[key] = item
    return value


class Catalogues:
    def __init__(self, folder):
        self.folder = Path(folder)
        self.errors = []
        self.locales = {'en': {'name': 'English', 'qt_locale': 'en_GB'}}
        self.messages = {}
        self.by_source = {}
        self.translations = {}
        self.help = {'fields': {}, 'tips': {}, 'buttons': {}}
        try:
            source = self.read(self.folder / 'en.json')
            if source['language'] != 'en':
                raise ValueError('English source language must be en')
            for ident, entry in source['messages'].items():
                if not re.fullmatch(r'[a-z][a-z0-9_.-]+', ident):
                    raise ValueError('Invalid message ID: ' + ident)
                if not isinstance(entry, dict) or not isinstance(entry.get('text'), str) or not isinstance(entry.get('context'), str):
                    raise ValueError('Source text/context required: ' + ident)
                placeholders(entry['text'])
                if entry['text'] in self.by_source:
                    raise ValueError('Duplicate English source text: ' + ident)
                self.messages[ident] = entry
                self.by_source[entry.get('source',entry['text'])] = ident
                self.by_source[entry['text']] = ident
            help_values = source.get('help', {})
            for group in self.help:
                mapping = help_values.get(group, {})
                if not isinstance(mapping, dict) or any(ident not in self.messages for ident in mapping.values()):
                    raise ValueError('Invalid help message reference: ' + group)
                self.help[group] = mapping
            self.locales['en'] = source
        except (OSError, ValueError, TypeError, KeyError) as exc:
            self.errors.append('en: ' + str(exc))
            self.messages.clear(); self.by_source.clear()
            return  # Literal English UI remains usable if even the base file is broken.
        for path in sorted(self.folder.glob('*.json')):
            if path.name == 'en.json':
                continue
            try:
                data = self.read(path)
                code = data['language']
                if path.stem != code or code in self.locales:
                    raise ValueError('Duplicate language or filename/language mismatch')
                translated = {}
                for ident, entry in data['messages'].items():
                    if ident not in self.messages:
                        self.errors.append(code + ': unknown message ' + ident); continue
                    source_text = self.messages[ident]['text']
                    if not isinstance(entry, dict) or not isinstance(entry.get('text'), str):
                        self.errors.append(code + ': invalid text ' + ident); continue
                    text = entry['text']
                    if entry.get('source_sha256') != text_hash(source_text):
                        self.errors.append(code + ': stale translation ' + ident); continue
                    if not text or placeholders(text) != placeholders(source_text):
                        self.errors.append(code + ': missing text or placeholder mismatch ' + ident); continue
                    translated[ident] = text
                missing = self.messages.keys() - translated.keys()
                if missing:
                    self.errors.append(code + ': ' + str(len(missing)) + ' messages use English fallback')
                self.translations[code] = translated
                self.locales[code] = data
            except (OSError, ValueError, TypeError, KeyError) as exc:
                self.errors.append(path.name + ': ' + str(exc))

    @staticmethod
    def read(path):
        data = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object)
        if not isinstance(data, dict) or data.get('format') != 1:
            raise ValueError('Unsupported catalogue format')
        if not isinstance(data.get('language'), str) or not re.fullmatch(r'[a-z]{2,3}(?:_[A-Z]{2})?', data['language']):
            raise ValueError('Invalid language code')
        if not isinstance(data.get('name'), str) or not data['name'].strip():
            raise ValueError('Language display name required')
        if not isinstance(data.get('qt_locale'), str) or not re.fullmatch(r'[a-z]{2,3}_[A-Z]{2}', data['qt_locale']):
            raise ValueError('Invalid Qt locale')
        if not isinstance(data.get('messages'), dict):
            raise ValueError('Messages must be an object')
        return data

    def translate(self, text, language='en'):
        ident = self.by_source.get(text) or self.by_source.get(text.replace('&', ''))
        if not ident:
            return text
        return self.translations.get(language, {}).get(ident, self.messages[ident]['text'])

    def help_text(self, group):
        return {key: self.messages[ident]['text'] for key, ident in self.help[group].items()}


CATALOGUES = Catalogues(Path(__file__).resolve().parent / 'locales')
