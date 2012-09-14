# encoding: utf-8
from djangomako.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponseRedirect, HttpResponse
from auth.models import UserProfile

def authorization(func):
	def check_auth(request, *args):
		if request.method == 'POST':
			if request.POST.has_key("login"):
				username = request.POST['username']
				password = request.POST['password']
				user = auth.authenticate(username=username, password=password)
				if user is not None and user.is_active:
					auth.login(request, user)

			elif request.POST.has_key("logout"):
				auth.logout(request)

		return func(request, *args)

	return check_auth

@authorization
def login(request):
	return render_to_response("auth.html", {"auth" : request.user.is_authenticated()})

def registration(request):
	users = UserProfile.objects.all()
	return render_to_response("registration.html", {"users" : users})

def redirect_after_activation(request):
	return HttpResponseRedirect("account/activate/complete/")
	
def start_page(request):
	return render_to_response("base.html", {})