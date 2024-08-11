from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.index,name='index'),
    path('home',views.index,name='home'),
    path('singup',views.signup,name='singup'),
    path('signout',views.singout,name='signout'),
    path('dashboard',views.dashboard,name='dashboard'),
   
   
    
  
]