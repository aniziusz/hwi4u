#!/bin/sh
cd -- "$(dirname -- "$0")" || exit 1
python3 install_desktop.py
result=$?
if [ "$result" -ne 0 ]; then
  printf '\nInstallation stopped. See the message above. Press Enter to close.\n'
  read -r answer
fi
exit "$result"
