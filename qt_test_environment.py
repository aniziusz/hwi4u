"""Child-test settings only; normal desktop launches keep the native Qt backend."""
import os,sys
from pathlib import Path


def test_environment(base=None):
    env=dict(os.environ if base is None else base)
    env.update(QT_QPA_PLATFORM='offscreen',PYTHONDONTWRITEBYTECODE='1')
    # The offscreen plugin needs a font directory; the Windows native plugin does not.
    # Reuse installed OS fonts, never copy or redistribute them. Respect explicit settings.
    if sys.platform=='win32' and not env.get('QT_QPA_FONTDIR'):
        fonts=Path(env.get('WINDIR','C:/Windows'))/'Fonts'
        if fonts.is_dir():env['QT_QPA_FONTDIR']=str(fonts)
    return env
