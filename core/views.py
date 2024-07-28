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
        player=User.objects.create_user(username=username,email=email,password=pass1)
        player.save()
        return redirect(request,'signin')
    else:
        return render(request,'core/signup.html')
def signin(request):
      
      if request.method=="POST":

        username=request.POST['username']
        password=request.POST['pass2']
        user=authenticate(username=username,password=password)
        if User is not None:
            login(request, User)
            fname=user.first_name
            messages.success(request,"you are logged in successfully ")
            return render(request,"core/dashboard.html",{
                "name":fname
            })
        else:
            messages.error(request,'Bad credentials')
            return render(request,"core/signin.html")
      else:
        return render(request,"core/signin.html")
def dashboard(request):
    name=User.first_name
    return render(request,"core/dashboard.html",{
        "name":name
    })
