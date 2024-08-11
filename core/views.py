from django.contrib import messages
from django.shortcuts import redirect, render
from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm
# Create your views here.
def index(request):
    return render(request,'core/index.html')
def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            username = form.cleaned_data.get('username')
            messages.success(request,f'Account created for {username}!')
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request,'registration/signup.html',{'form':form})
@login_required
def singout(request):
    logout(request)
    msg='you are logged out'
    signout=True
    return render(request,'registration/login.html',{
    'msg':msg,"sigout":signout
    })
@login_required
def dashboard(request):
    if request.user.is_authenticated:
        name=request.user.username

        msg='you are logged in'
        return render(request,'core/dashboard.html',{
        'msg':msg,"name":name
        })
    return render(request,'core/dashboard.html')