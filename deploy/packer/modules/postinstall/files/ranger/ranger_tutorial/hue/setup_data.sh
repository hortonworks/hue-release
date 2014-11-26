#!/bin/bash
cd /usr/lib/hue

function createGroup {
    group=$1
}

function createUser {
    user=$1
    password=$user
    group=$2

    #echo "createUser $user $group"
    cat > /tmp/hue_user.py <<EOF
from desktop.auth.forms import UserCreationForm
from useradmin.models import get_default_user_group
form = UserCreationForm({ "username" : "$user", "password" : "$user", "ensure_home_directory": False, "is_active" : True})
user = form.save()
user.groups = set([get_default_user_group()])
user.save()
exit()
EOF

./build/env/bin/hue shell < /tmp/hue_user.py
}

for i in 1 2 3 
do
    createUser it${i} "IT"
    createUser legal${i} "Legal"
    createUser mktg${i} "Marketing"
    createUser network${i} "Network"   
done


