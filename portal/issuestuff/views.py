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
import datetime
from django.contrib import messages
# from django.core.servers.basehttp import FileWrapper
import re
import requests
import json
import base64
from django.http import Http404
from portal.env import *

def mainpage(request):
    user = request.user
    if user is not None and user.is_active:
        return redirect(reverse("home"))
    template = loader.get_template('mainpage.html')
    users_in = User.objects.filter(member__current_status="IN")
    return render(request,"mainpage.html",{'users_in':users_in})

def login(request):
    user = request.user
    if user is not None and user.is_active:
        return redirect(reverse('home'))
    return HttpResponseRedirect(ssoURL()) 

def ssoURL():
    return 'http://gymkhana.iitb.ac.in/sso/oauth/authorize/?client_id='+clientid+'&response_type=code&scope=basic%20profile%20ldap%20sex%20picture%20phone%20insti_address%20program%20secondary_emails&redirect_uri='+redirecturl+'&state=enter'

def logout(request):
    user = request.user
    if user is not None and user.is_active:
        auth.logout(request)
        return redirect(reverse("default"))
    return redirect(reverse("default"))    
    
def logout_users(request):
    username = request.POST.get('username')
    user_exists = User.objects.filter(username=username).exists()
    if user_exists:
        user = User.objects.get(username=username)
        if username is not None and user is not None:
            if(user.member.current_status=="IN"):
                now = datetime.datetime.now()
                user.member.current_status="OUT"
                user.member.current_log.outtime = now
                user.member.current_log.save()
                user.member.save()
                user.save()
    return redirect(reverse("default"))    

def enter(request):
    user = request.user
    if user is not None and user.is_active:
        if new_record(request):
            return redirect(reverse("home"))
        else:
            messages.warning(request, 'Please fill purpose.')
            return redirect(reverse("home"))    
    return redirect(reverse("default"))    


def exit(request):
    user = request.user
    if user is not None and user.is_active:
        if(user.member.current_status=="IN"):
            now = datetime.datetime.now()
            user.member.current_status="OUT"
            user.member.current_log.outtime = now
            user.member.current_log.save()
            user.member.save()
            user.save()
        return redirect(reverse("home"))
    return redirect(reverse("default"))    


def redirect_function(request):
    authcode = request.GET.get('code', 'error')
    state  = request.GET.get('state', 'error')
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
    check,data = checkEnoughInformation(userdata)
    if not check:
        messages.warning(request,"Not enough Information provided. Please allow application to access the required information.")    
        return redirect(reverse("default"))

    username = userdata.get('username')

    user = auth.authenticate(username=username,password=password)

    if user is not None and user.is_active:
        auth.login(request,user)
        return HttpResponseRedirect("/home/")
    else:
        signup(userdata)
        user = auth.authenticate(username=username,password=password)
        auth.login(request,user)
        return HttpResponseRedirect("/home/")    

def checkEnoughInformation(userdata):
    username = userdata.get('username')
    first_name = userdata.get('first_name')
    last_name = userdata.get('last_name')
    email = userdata.get('email')
    roll_number = userdata.get('roll_number')
    notGivenInfo = []
    if username is None:
        notGivenInfo.append('username')
    if first_name is None:
        notGivenInfo.append('first_name')
    if last_name is None:
        notGivenInfo.append('last_name')
    if email is None:
        notGivenInfo.append('email')
    if roll_number is None:
        notGivenInfo.append('roll_number')
    if len(notGivenInfo)>0:
        return False,notGivenInfo
    return True,notGivenInfo

def new_record(request):
    user = request.user
    if user is not None and user.is_active:
        if user.member.current_status!="IN":
            if(request.POST.get('purpose')==""):
                return False
            now = datetime.datetime.now()
            log = Log(user=user,intime=now,purpose=request.POST.get('purpose'))
            log.save()
            user.member.current_status="IN"
            user.member.current_log=log
            user.member.save()
            user.save()
        return True
    return False        

def getdata(acctoken,reftoken):
    fields = 'first_name,last_name,type,profile_picture,sex,username,email,program,contacts,insti_address,secondary_emails,mobile,roll_number'
    url = 'http://gymkhana.iitb.ac.in/sso/user/api/user/?fields='+fields
    header = {
        'GET /sso/user/api/user/ HTTP/1.1'
        'Host': 'gymkhana.iitb.ac.in',
        'Authorization': 'Bearer '+acctoken
    }
    r = requests.get(url,headers=header)
    # return r.content
    parsed_json = json.loads(r.content)
    return parsed_json

def signup(userdata):
    username = userdata.get('username')
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
    current_status = None
    address = userdata.get('insti_address')
    hostel = None
    room = None
    if(address!=None):
        hostel = address.get('hostel_name')
        room = address.get('room')
    current_log = None
    secondary_emails = userdata.get("secondary_emails")
    secondary_email=None
    if secondary_emails!=None:
        if(len(secondary_emails)>0):
            secondary_email = secondary_emails[0].get('email')

    auth_user = User.objects.create_user(username=username,password=password,email=email,first_name=first_name,last_name=last_name)
    auth_user.save()

    _user = Member(user=auth_user,roll=roll_number,sex=sex,contact=contact,hostel=hostel,room=room,discipline=discipline,join_year=join_year,graduation_year=graduation_year,degree=degree,current_status=current_status,current_log = current_log,secondary_email=secondary_email)
    _user.save()
    return 

def home(request):
    user = request.user
    if user is not None and user.is_active and user.is_staff:
        return redirect(reverse("admin_interface",args=["home"]))
    if user is not None and user.is_active:
        visit_number = Log.objects.filter(user=user).count()
        if visit_number==1:
            sym = "st"
        elif visit_number==2:
            sym = "nd"
        else:
            sym = "th"        
        return render(request,'home.html',{'user':user,"active":"home","visit_number":visit_number,"sym":sym})
    return redirect(reverse("default"))    

def validateEmail(email ):
    from django.core.validators import validate_email
    from django.core.exceptions import ValidationError
    try:
        validate_email( email )
        return True
    except ValidationError:
        return False

def enter_secondary_email(request):
    user = request.user
    if user is not None and user.is_active:
        if request.POST.get('email')!=None:
            email = request.POST.get('email')
            if validateEmail(email):
                user.member.secondary_email=email
                user.member.save()
            else:
                messages.warning(request,"Please enter correct email address.")    
    return redirect(reverse("home"))

def tl_records(request):
    user = request.user
    if user is not None and user.is_active:
        logs = Log.objects.filter(user = user).order_by('-intime')
        return render(request,"records.html",{'logs':logs,"active":"records"})
    return redirect(reverse("default"))

def issuestuff(request):
    user = request.user
    if user is not None and user.is_active:
        issuelog = IssuingLog.objects.filter(user=user)
        return render(request,"issue_records.html",{'logs':issuelog,"active":"issuestuff","type":"return","is_Staff":False})
    return redirect(reverse("default"))
    
def admin_interface(request,page):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))

    if(page == ""):
        return HttpResponseRedirect("/admin_site/home/")
    elif(page == "home"):
        return render(request,"admin_home.html")
    elif(page == "records"):
        return HttpResponseRedirect("/admin_site/records/all")
    elif(page == "issues"):
        return HttpResponseRedirect("/admin_site/issues/all")
        

    return HttpResponse("Page Not Found 2")

def admin_records(request,page):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))

    if(page==""):
        return HttpResponseRedirect("/admin_site/records/all")
    elif(page=="all"):
        logs = Log.objects.order_by('-intime')
        return render(request,"admin_records.html",{'logs':logs,"active":"records"})
    elif(page=="current"):
        logs = Log.objects.filter(outtime__isnull=True).order_by('-intime')
        return render(request,"admin_records.html",{'logs':logs,"active":"records"})
    elif(page=="search"):
        return HttpResponse("Error Wrong function call")

    return HttpResponse("Page Not Found 3")

def admin_records_search(request,username):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))

    user_exists = User.objects.filter(username__startswith=username).exists()
    if user_exists:
        logs = Log.objects.filter(user__username__startswith=username).order_by('-intime')
        return render(request,"admin_records.html",{'logs':logs,"active":"records"})
    else:
        return HttpResponse("User Not Found")

def admin_issue(request, page):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))

    if(page == ""):
        return HttpResponseRedirect("/admin_site/issues/all")
    elif(page == "all"):
        issuelogs = IssuingLog.objects.order_by('-taketime')
        return render(request,"issue_records.html",{'logs':issuelogs,"active":"issuestuff","is_Staff":True})
    elif(page == "current"):
        issuelogs = IssuingLog.objects.filter(returntime__isnull=True).order_by('-taketime')
        return render(request,"issue_records.html",{'logs':issuelogs,"active":"issuestuff","is_Staff":True})
    elif(page == "stuff"):
        stuffs = Stuff.objects.order_by('-id')
        return render(request,"issue_stuff.html",{'stuffs':stuffs,"active":"issuestuff","is_Staff":True})
    else:
        return HttpResponse("Page Not Found 1")

def return_confirm(request):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))

    option = request.POST.get('log_id')
    issuelogs_exists = IssuingLog.objects.filter(id=option).exists()
    if not issuelogs_exists:
        return HttpResponse("Issue Log Not Found")

    issuelog = IssuingLog.objects.get(id=option)
    return render(request,"return_confirm.html",{'log':issuelog,"active":"issuestuff","type":"return","is_Staff":True})


def return_confirmed(request):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))

    option = request.POST.get('log_id')
    issuelogs_exists = IssuingLog.objects.filter(id=option).exists()
    if not issuelogs_exists:
        return HttpResponse("Issue Log Not Found")

    issuelog = IssuingLog.objects.get(id=option)
    now=datetime.datetime.now()
    issuelog.returntime = now
    issuelog.save()
    return HttpResponseRedirect("/admin_site/")

def new_issue_confirm(request):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))

    stuff_id = request.POST.get('stuff_id')
    stuff_exists = Stuff.objects.filter(id=stuff_id).exists()
    # return HttpResponse(str(stuff_exists)+ " -- " + str(stuff_id) + " -- " + str(Stuff.objects.all()[0].id))
    if not stuff_exists:
        return HttpResponse("Stuff Not Found 2")

    users = User.objects.exclude(username__startswith="tl_")
    stuff = Stuff.objects.get(id=stuff_id)
    return render(request,"issue_confirm.html",{'stuff':stuff,"active":"issuestuff","type":"issue","is_Staff":True,"users":users})

def new_issue_confirmed(request):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))
    stuff_id = request.POST.get('stuff_id')
    stuff_name = request.POST.get('stuff_name')
    username = request.POST.get('username').split(" ")[0]
    quantity = request.POST.get('quantity')

    stuff_exists = Stuff.objects.filter(id=stuff_id).exists()
    user_exists = User.objects.filter(username=username).exists()
    # return HttpResponse(str(stuff_exists)+ " -- " + str(stuff_id)+" -- " + str(stuff_name)  +" -- " + str(username) +" -- " + str(quantity) + " -- " + str(Stuff.objects.all()[0].id))
    if not stuff_exists:
        return HttpResponse("Stuff Not Found 1")
    if not user_exists:
        return HttpResponse("User Not Found")
    try:
        quantity = int(quantity)
    except ValueError:
        return HttpResponse("Enter Integral Quantity")
    
    if quantity <= 0:
        return HttpResponse("Enter Positive Integral Quantity")

    stuff = Stuff.objects.get(id=stuff_id)
    issue_user = User.objects.get(username=username)
    now = datetime.datetime.now()
    issuelog = IssuingLog(user=issue_user,stuff=stuff,quantity=quantity,taketime=now)
    issuelog.save()
    return HttpResponseRedirect("/admin_site/")
    

def new_stuff_add(request):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))
    stuff = Stuff.objects.all()    
    return render(request,'new_stuff_add.html',{'stuffs':stuff})

def new_stuff_confirm(request):
    user = request.user
    if not (user is not None and user.is_active and user.is_staff):
        return redirect(reverse("home"))
    stuff_name = request.POST.get('stuff_name')
    if stuff_name=="" or len(stuff_name)>=50:
        messages.warning(request,"Enter Valid Name of stuff")    
        return redirect(reverse("new_stuff_add"))
    stuff = Stuff(name=stuff_name)
    stuff.save()
    return redirect(reverse("new_stuff_add"))

def new_stuff(request,param):
    if param=="add":
        return redirect(reverse("new_stuff_add"))
    if param=="confirm":
        return redirect(reverse("new_stuff_confirm"))
    return HttpResponse("page not found")

def my_404_view(request):
    return render(render,"404page.html")    

def search_by_username(request):
    q=request.GET.get("q")
    users = User.objects.filter(username__startswith=q)
    return render(request,'search_by_username.html',{'users':users})    