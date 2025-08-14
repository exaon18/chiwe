from django.shortcuts import render
from autapp.models import MyUser,Ballance,Maintainance
from django.contrib.auth.decorators import login_required
from django.http import Http404, JsonResponse
from django.contrib import messages
# Create your views here.
@login_required
def ctc(request):
    maintenance = Maintainance.objects.first()
    if maintenance and maintenance.enabled:
        return render(request, 'maintenance.html')
    user=MyUser.objects.get(username=request.user.username)
    print(f"users id {user}")
    print(MyUser.objects.get(id=user.id).username)
    print(Ballance.objects.get(user=user).ballance)
    ballance=Ballance.objects.get(user=user).ballance

    if request.method =='POST':
        if user.Active_Game:
            print("user is already in a game")
            messages.error(request,"You are already in a game")
            return JsonResponse({"proceed":False,"message":"You are already in a game"})
        amount=int(request.POST["amount"])
        print("in the view ")
        if amount == 2 or amount == 10 or amount ==25 or amount==0:
            print('sucess')
            if Ballance.objects.get(user=user).ballance >=amount:
                print(Ballance.objects.get(user=user).ballance)
                messages.success(request,"balance verified, proceeding to the game")
                return JsonResponse({"proceed":True,"message":"balance verified, proceeding to the game","amount":amount, "type": "searching"})
            else:
                print("hey")
                return JsonResponse({"proceed":False,"message":"insufficient balance"})
           
        else:
            messages.error(request,"invalid amount")
            print('Error')
            print(type(amount))
            return JsonResponse({"procced":False})
            
    else:
        return render(request,'CTC/ctc.html',{"user":user,"ballance":ballance})
@login_required
def bingo(request):
      maintenance = Maintainance.objects.first()
      if maintenance and maintenance.enabled:
          return render(request, 'maintenance.html')
      
      if not request.user.is_authenticated:
          raise Http404("User not authenticated")
      
      
     
      if request.method =='POST':
          user=MyUser.objects.get(username=request.user.username)
          print(f"users id {user}")
          ballance=Ballance.objects.get(user=user).ballance
          if user.Active_Game:
            print("user is already in a game")
            messages.error(request,"You are already in a game")
            return JsonResponse({"proceed":False,"message":"You are already in a game"})
          amount=int(request.POST["amount"])
          print("in the view bingo ")
          if amount == 2 or amount == 10 or amount ==25 or amount==0:
              print('sucess')
              if ballance >=amount:
                  print(Ballance.objects.get(user=user).ballance)
                  messages.success(request,"balance verified, proceeding to the game")
                  return JsonResponse({"proceed":True,"message":"balance verified, proceeding to the bingo board assembly","amount":amount, "type": "Assembly"})
              else:
                  print("hey")
                  return JsonResponse({"proceed":False,"message":"insufficient balance"})
           
          else:
              messages.error(request,"invalid amount")
              print('Error')
              print(amount)
              return JsonResponse({"procced":False,"message":"invalid amount"})
            
      else:
          return render(request,'bingo.html')
      