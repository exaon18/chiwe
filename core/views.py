from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'core/index.html')
def signup(request):
    return render(request, 'core/signup.html')
def signin(request):
    return render(request,"core/signin.html")
