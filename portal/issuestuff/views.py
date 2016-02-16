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
# from django.core.servers.basehttp import FileWrapper
import re
import requests
import json
import base64

redirecturl = 'http://localhost:8000/redirect'
clientid = 'LEdwtHLmG59vmQAh3O8YE1MyeuEUQo0vF59BHN4y'
clientsecret = 'Ojxvb3sPNZhBa5kdvQeznMGMJf0EhRNqehMBKEkLRX68tzFkpt7X3kbXSSaaVP16aD7HUoi6Py142sCrfVnqawIhKZwDoRsTu4Hb9vnpkwW6K8SeiE7ezwARlPRU7fUJ'

def mainpage(request):
	template = loader.get_template('mainpage.html')
  	return HttpResponse(template.render())

def enter(request):
	return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic%20profile%20ldap%20sex&redirect_uri='+redirecturl+'&state=enter')  

def exit(request):
	
	return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic%20profile%20ldap%20sex&redirect_uri='+redirecturl+'&state=exit')  


####################################################################
##########enter the client secret id in the below function########################################
#################################################################################
####################################################################
##########enter the client secret id in the below function########################################
#################################################################################
def redirect(request):

	# return HttpResponseRedirect('http://www.google.com')
	authcode = request.GET.get('code', 'lol')
	state  = request.GET.get('state', 'error')
	# clientsecret = 'intentionally_hidden:-P'
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
	# storeentry(name,ldap,state)
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


def login(request):
    user = request.user
    if user is not None and user.is_active:
        return redirect("/home/")
    return render(request,'login.html')

def signin(request):
    user = request.user
    if user is not None and user.is_active:
        return redirect("/home/")
    if request.method=='POST':
        username= request.POST['username']
        password= request.POST['password']
        user = auth.authenticate(username=username,password=password)
        if user is not None and user.is_active:
            auth.login(request,user)
            return redirect("/home/")
        else:
            return render(request,'login.html',{'error':"Wrong Credentials"})
    return HttpResponse("POST request required")

def signup(request):
    user = request.user
    if user is not None and user.is_active:
        return redirect("/home/")
    if request.method=='POST':
        username = request.POST['username']
        password = request.POST['password']
        name = request.POST['name']
        email_id = request.POST['email_id']

        user = auth.authenticate(username=username,password=password)
        if user is not None and user.is_active:
            return redirect("/home",{'error':"already registered"})    
        if "" in [username,password,name,email_id]:
            return render(request,"login.html",{'error':"Invalid form response. Missing one field."})

        users = User.objects.all()
        for u in users:
            if u.username == username:
                return render(request,'login.html',{'error':"Username Already taken"})
        _user = Users(username=username,password=password,name=name,email_id=email_id)
        _user.save()
        auth_user = User.objects.create_user(username=username,password=password,email=email_id,first_name=name)
        auth_user.save()

        return redirect("/login")
    return HttpResponse("POST request required")

def signout(request):
    auth.logout(request)
    return redirect("/")

# def newSignUp(userdata):

# def signIn(userdata):



# def storeentry(name,ldap,state):
	#write the entry in database
	#state is enter or exit