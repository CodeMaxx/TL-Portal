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

def mainpage(request):
	template = loader.get_template('mainpage.html')
  	return HttpResponse(template.render())

def enter(request):
  return HttpResponseRedirect('http://www.google.com')  

def exit(request):
  return HttpResponseRedirect('http://www.cse.iitb.ac.in') 
