from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login

# Create your views here.
def index(request):
    return render(request,'core/index.html')