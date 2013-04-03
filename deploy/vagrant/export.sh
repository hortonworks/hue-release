set -x
set -e

vagrant up
MACHINE="$(VBoxManage list vms | grep `python2 -c "import json; print json.loads(file('.vagrant').read())['active']['default']"` | sed -r 's/\"(.*)\".*/\1/g')"
VBoxManage export "$MACHINE" --output "$MACHINE".ova --vsys 0 --vendor "HortonWorks" --version "Caterpillar" --product "Sandbox"
