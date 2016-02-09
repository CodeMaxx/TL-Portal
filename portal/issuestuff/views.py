from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import csv
from django.contrib.auth import authenticate, login, logout
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.core.servers.basehttp import FileWrapper
import re
import requests

redirecturl = 'http://127.0.0.1:8000/redirect'

def mainpage(request):
	template = loader.get_template('mainpage.html')
  	return HttpResponse(template.render())

def enter(request):
	clientid = '07NulE31ebnzsBhGfC8rW0DuGibN5ws2yqyJR2c9'
	return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic&redirect_uri='+redirecturl+'&state=enter')  

def exit(request):
	clientid = '07NulE31ebnzsBhGfC8rW0DuGibN5ws2yqyJR2c9'
	return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic&redirect_uri='+redirecturl+'&state=exit')  


def redirect(request):

	# return HttpResponseRedirect('http://www.google.com')
	authcode = request.GET.get('code', 'lol')
	state  = request.GET.get('state', 'error')
	print authcode
	print state
	
	template = loader.get_template('test.html')
	return HttpResponse(template.render())

