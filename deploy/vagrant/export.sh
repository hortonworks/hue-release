MACHINE="$(VBoxManage list vms | grep `python2 -c "import json; print json.loads(file('.vagrant').read())['active']['default']"` | sed -r 's/\"(.*)\".*/\1/g')"
VBoxManage export "$MACHINE" --output "$MACHINE".ova --vendor "HortonWorks" --version "Caterpillar" --product "Sandbox"
