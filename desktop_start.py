"""Graphical startup for installed launchers; workspace data stays outside source."""
import sys
import subprocess
from pathlib import Path

def main(argv=None):
    from PySide6.QtWidgets import QApplication,QMessageBox
    import manage
    args=list(sys.argv[1:] if argv is None else argv)
    if args not in ([],['test']):raise ValueError('Only production or test startup is supported.')
    app=QApplication.instance() or QApplication([])
    target=manage.default_workspace()
    from ui_i18n import install,read_language,tr
    install(read_language(target))
    if not (target/'INSTALLATION.json').is_file():
        QMessageBox.information(None,'HWI4U',tr('No private workspace is installed. Run Install HWI4U first.'));return 1
    try:
        result=subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'manage.py'),'test' if args else 'run'],capture_output=True,text=True)
        if result.returncode:QMessageBox.critical(None,tr('Cannot start HWI4U'),(result.stderr or result.stdout)[-4000:])
        return result.returncode
    except Exception as exc:
        QMessageBox.critical(None,tr('Cannot start HWI4U'),str(exc));return 1

if __name__=='__main__':sys.exit(main())
