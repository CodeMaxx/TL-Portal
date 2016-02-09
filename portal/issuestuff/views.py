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
import json
import base64

redirecturl = 'http://127.0.0.1:8000/redirect'
clientid = 'nnzCDk9LFowzvz51f9LXeHV4eWgKX8dOzVDsqFGL'

def mainpage(request):
	template = loader.get_template('mainpage.html')
  	return HttpResponse(template.render())

def enter(request):
	return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic%20profile%20ldap%20sex&redirect_uri='+redirecturl+'&state=enter')  

def exit(request):
	
	return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic%20profile%20ldap%20sex&redirect_uri='+redirecturl+'&state=exit')  


def redirect(request):

	# return HttpResponseRedirect('http://www.google.com')
	authcode = request.GET.get('code', 'lol')
	state  = request.GET.get('state', 'error')
	clientsecret = 'intentionally_hidden:-P'
	authtoken = clientid+':'+clientsecret
	authtoken = base64.b64encode(authtoken)
	#state shows whether the user is entering and exiting
	url = 'http://gymkhana.iitb.ac.in/sso/oauth/token/'
	header = {
		'Host': 'gymkhana.iitb.ac.in',
		'Authorization': 'Basic '+authtoken,
		'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'	
	}

	payload = {
		'code':authcode,
		'redirect_uri':redirecturl,
		'grant_type' : "authorization_code"
		}
	r = requests.post(url,data=payload,headers=header)
	parsed_json = json.loads(r.content)
	acctoken = parsed_json['access_token']
	reftoken = parsed_json['refresh_token']
	userdata = getdata(acctoken,reftoken)
	name = userdata['first_name']+" "+userdata['last_name']
	ldap = userdata['email']
	print name
	print ldap
	storeentry(name,ldap,state)
	template = loader.get_template('test.html')
	return HttpResponse(template.render())

def getdata(acctoken,reftoken):
	url = 'http://gymkhana.iitb.ac.in/sso/user/api/user/?fields=first_name,last_name,roll_number,email'
	header = {
		'GET /sso/user/api/user/ HTTP/1.1'
		'Host': 'gymkhana.iitb.ac.in',
		'Authorization': 'Bearer '+acctoken
	}
	r = requests.get(url,headers=header)
	parsed_json = json.loads(r.content)
	return parsed_json

def storeentry(name,ldap,state):
	#write the entry in database
	#state is enter or exit