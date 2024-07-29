from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login

# Create your views here.
def index(request):
    return render(request,'core/index.html')
def signup(request):
    if request.method=='POST':
        username=request.POST['username']
        firstname=request.POST['firstname']
        lastname=request.POST['lastname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']
        player=User.objects.create_user(username,email,pass1)
        
        
        player.first_name=firstname
        player.last_name=lastname
        player.save()
        return redirect(request,'signin')
    
    return render(request,'core/signup.html')
def login(request):
    return render(request,'registration/login.html')
def dashboard(request):
    name=request.POST['first_name']
    
    return render(request,"core/dashboard.html",{
        "name":name
    })
