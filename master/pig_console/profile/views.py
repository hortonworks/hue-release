# -*- coding: utf-8 -*-
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login as auth_login
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from pig.views import index


def login(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            auth_login(request, form.get_user())
            return redirect(index)
    else:
        form = AuthenticationForm()
    return render_to_response("login.html",
                              RequestContext(request, {'form': form}))
