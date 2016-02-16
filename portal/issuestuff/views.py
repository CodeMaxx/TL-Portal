from django.shortcuts import render, redirect
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect
from django.http import HttpResponse
import csv
from django.contrib.auth import authenticate, login, logout
from django.template.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.contrib import auth
from django.contrib.auth.models import User
from models import *
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
    return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic%20profile%20ldap%20sex%20picture%20phone%20insti_address%20program%20secondary_emails&redirect_uri='+redirecturl+'&state=enter')  

def exit(request):
    auth.logout(request)
    return HttpResponseRedirect("/")
    return HttpResponseRedirect('http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic%20profile%20ldap%20sex%20picture%20phone%20insti_address%20program%20secondary_emails&redirect_uri='+redirecturl+'&state=exit')


####################################################################
##########enter the client secret id in the below function########################################
#################################################################################
####################################################################
##########enter the client secret id in the below function########################################
#################################################################################
def redirect_function(request):

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
    username = userdata['username']
    password = username
    user = auth.authenticate(username=username,password=password)

    if user is not None and user.is_active:
        auth.login(request,user)
        return HttpResponse('old user')
        return HttpResponseRedirect("/home/")
    else:
        signup(userdata)
        user = auth.authenticate(username=username,password=password)
        auth.login(request,user)
        return HttpResponse('new user')
        return HttpResponseRedirect("/home/")    

    name = userdata['first_name']+" "+userdata['last_name']
    ldap = userdata['email']
    print name
    print ldap
    # storeentry(name,ldap,state)
    template = loader.get_template('test.html')
    return HttpResponse(template.render())

def getdata(acctoken,reftoken):

    fields = 'first_name,last_name,type,profile_picture,sex,username,email,program,contacts,insti_address,secondary_emails,mobile,roll_number'
    url = 'http://gymkhana.iitb.ac.in/sso/user/api/user/?fields='+fields
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

def signup(userdata):
    username = userdata.get('username')
    password = username
    first_name = userdata.get('first_name')
    last_name = userdata.get('last_name')
    email = userdata.get('email')
    roll_number = userdata.get('roll_number')
    profile_picture = userdata.get('profile_picture')
    sex = userdata.get('sex')
    contact = userdata.get('mobile')
    program = userdata.get('program')
    discipline = None
    join_year = None
    graduation_year = None
    degree = None
    if(program!=None):
        discipline = program.get('department_name')
        join_year = program.get('join_year')
        graduation_year = program.get('graduation_year')
        degree = program.get('degree_name')
    current_status = "IN"
    address = userdata.get('insti_address')
    hostel = None
    room = None
    if(address!=None):
        hostel = address.get('hostel_name')
        room = address.get('room')
    current_log = None

    auth_user = User.objects.create_user(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
    auth_user.save()

    _user = Member(user=auth_user,roll=roll_number,sex=sex,contact=contact,hostel=hostel,room=room,discipline=discipline,join_year=join_year,graduation_year=graduation_year,degree=degree,current_status=current_status,current_log = current_log)
    _user.save()
    return 

def home(request):
    return HttpResponse("home")

def signout(request):
    auth.logout(request)
    return redirect("/")

# def newSignUp(userdata):

# def signIn(userdata):



# def storeentry(name,ldap,state):
    #write the entry in database
    #state is enter or exit