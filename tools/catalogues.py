#!/usr/bin/env python3
"""Check UTF-8 language files, or create a new English-fallback locale template."""
import argparse
import json
from pathlib import Path
import re
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from language_catalog import Catalogues, text_hash


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--folder', type=Path, default=Path(__file__).resolve().parents[1]/'locales')
    parser.add_argument('--new-language')
    parser.add_argument('--name')
    parser.add_argument('--qt-locale')
    args=parser.parse_args(); catalogues=Catalogues(args.folder)
    if args.new_language:
        if (not re.fullmatch(r'[a-z]{2,3}(?:_[A-Z]{2})?', args.new_language)
                or not args.name or not re.fullmatch(r'[a-z]{2,3}_[A-Z]{2}', args.qt_locale or '')):
            parser.error('Supply a valid language code, --name and --qt-locale')
        if 'en' not in catalogues.locales or not catalogues.messages:
            parser.error('A valid English base catalogue is required')
        value=dict(format=1,language=args.new_language,name=args.name,qt_locale=args.qt_locale,
                   messages={ident:dict(text=entry['text'],source_sha256=text_hash(entry['text']))
                             for ident,entry in catalogues.messages.items()})
        # Empty translations deliberately fall back until a translator supplies text.
        for entry in value['messages'].values(): entry['text']=''
        with (args.folder/(args.new_language+'.json')).open('x',encoding='utf-8') as file:
            file.write(json.dumps(value,ensure_ascii=False,indent=2)+'\n')
        print('Created template; translate entries and restart the client. English is used for unfinished entries.')
        return 0
    print(json.dumps(dict(languages=list(catalogues.locales),messages=len(catalogues.messages),
                         problems=catalogues.errors),ensure_ascii=False,indent=2))
    return 1 if catalogues.errors else 0


if __name__=='__main__': sys.exit(main())
