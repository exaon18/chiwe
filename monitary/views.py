from decimal import Decimal
import decimal
import string
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import Http404, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.urls import reverse
from autapp.models import MyUser, Ballance
from .models import WithdrawalRequest,DepositRequest,TelebirrReq,Ebirreq
from autapp.models import chiweProfit,Maintainance
from django.db.models import Sum
import random
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json
import time
import re
from django.http import JsonResponse
import threading
from autapp.views import generate_unique_number
import re

def extract_ebirr_info(message: str):
    pattern = r"Ref:(\d+)\s+Confirmed\.\s+(ETB\d+)"
    match = re.search(pattern, message, re.DOTALL)
    if match:
        trx_id = match.group(1)
        amount = match.group(2)
        return trx_id, amount
    return None, None

def extract_sms_info(message):
    pattern = (
    r"received ETB (?P<amount>[\d.]+) from (?P<name>.+?)\((?P<phone>[\d\*]+)\)\s+on (?P<date>\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2})\."
    r" Your transaction number is (?P<tx_id>\w+)"
)

    match = re.search(pattern, message)
    if match:
        print(match.groupdict())
        return match.groupdict()
    else:
        print("Pattern didn't match 😢")

# In your view
@csrf_exempt
@require_POST
def receive_sms(request,key,way):
    if key=="Plgp2y8yu":
        if way=="tb":
            print("in tb")
            print(request.POST)
            body = request.POST["Plgp2y8yu"]
            print(body)
            
            data = extract_sms_info(message=body)
            tx_id=data["tx_id"]
            amount=float(data["amount"])
            date=data["date"]
            if TelebirrReq.objects.filter(tx_id=tx_id).exists()==False and len(tx_id)==10:
                TelebirrReq.objects.create(tx_id=tx_id,amount=amount,completed=False)
            elif TelebirrReq.objects.filter(tx_id=tx_id).exists():
                if TelebirrReq.objects.get(tx_id=tx_id).completed==False:
                    print("trx already exisit waiting to be reedemd")
                else:
                    print("trx already reedemd")
            else:
                print("smtn went wrong")
        elif way=="eb":
            print(request.POST)
            print("in eb")
            body = json.loads(request.body)
            print(f"body {body}")
            sms = body.get('content', '')
            print(sms)
            data = extract_ebirr_info(sms)
            print(f"extracted {data}")
            tx_id=data[0]
            amount=data[1]
            amount=amount[3:]
            print(f"extracted {data}")
            print(f"tx_id {tx_id}")
            print(f"amount {amount}")
            
            if Ebirreq.objects.filter(tx_id=tx_id).exists()==False and len(tx_id)==10:
                Ebirreq.objects.create(tx_id=tx_id,amount=amount,completed=False)
            elif Ebirreq.objects.filter(tx_id=tx_id).exists():
                if Ebirreq.objects.get(tx_id=tx_id).completed==False:
                    print("trx already exisit waiting to be reedemd")
                else:
                    print("trx already reedemd")
            else:
                print("smtn went wrong")

            print(data)

        return JsonResponse({'status': 'received', 'parsed': data})

invalidOtp = False
# ✅ Generate a proper 6-digit OTP
def generate_unique_number():
    return str(random.randint(100000, 999999))  # Always generates a 6-digit OTP

# ✅ Send email properly
def send_welcome_email(user, email, token, subjectE):
    subject = subjectE
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = email
    print(f"📧 Sending email to: {to_email}")
    html_content = render_to_string('withdrawOTP.html', {'user': user, 'token': token})
    
    email_message = EmailMessage(subject, html_content, from_email, [to_email])
    email_message.content_subtype = 'html'
    
    try:
        email_message.send()
        print(f"✅ Email sent successfully to {email}")
    except Exception as e:
        print(f"❌ Email sending failed: {e}")

@login_required
def withdraw(request, invalidOtp=invalidOtp):
    maintenance = Maintainance.objects.first()
    if maintenance and maintenance.enabled:
        return render(request, 'maintenance.html')
    
    user = request.user
    user_balance = Ballance.objects.get(user=user)


    if request.method == 'POST':
        
        try:
            amount = float(request.POST["amount"])
            way=request.POST["way"]
        except ValueError:
            messages.error(request, "Please enter a valid number for the amount.")
            print("Redirecting to 'withdraw' after invalid amount input.")
            return JsonResponse(request,{"success":False,"message":"Please enter a valid number for the amount."})
        
        
        phone_number = request.POST["phone_number"].strip()

        if user.pendingWithdrwal:
            print("⏳ User already has a pending withdrawal. Rendering 'withdraw.html'.")
            
            return JsonResponse(request,{"success":False,"message":"You already have a pending withdrawal. Please wait for it to be processed."})
        
        # Compare after converting token from the form to int
        if  user_balance.ballance >= amount:
            if amount < 25:
                print("❌ Withdrawal amount too low. Rendering 'withdraw.html'.")
                return JsonResponse(request,{"success":False,"message":"Withdrawal amount must be at least 25 birr."})
            if way=="tb":
                user_balance.ballance -= Decimal(amount)
                user_balance.save()
                WithdrawalRequest.objects.create(
                    user=user,
                    amount=amount,
                    phone_number=phone_number,
                    status="Pending",
                    way="tb"

                )
                user.pendingWithdrwal = True
                # Reset OTP after use
                user.save()
                return JsonResponse({"success":True,"message":f"Your withdrawal request for {amount}  ETB using Telebirr has been submitted successfully."})
                    
                
            elif way=="eb":
                user_balance.ballance -= Decimal(amount)
                user_balance.save()
                WithdrawalRequest.objects.create(
                    user=user,
                    amount=amount,
                    phone_number=phone_number,
                    status="Pending",
                    way="eb"

                )
                user.pendingWithdrwal = True
                # Reset OTP after use
                user.save()
                return JsonResponse({"success":True,"message":f"Your withdrawal request for {amount}  ETB using E-birr has been submitted successfully."})
            else:
                return JsonResponse({"success":False,"message":"Please select a wallet to withdraw."})
        else:
            
            print("❌insufficient balance. Redirecting to 'withdraw'.")
            
            return JsonResponse({"success":False, "message":" Insufficinet balance"})
    else: 
        
        return render(request, "withdraw.html")

def ChiweA(request, username):
    try:
        admin_user = MyUser.objects.get(username=username)
    except MyUser.DoesNotExist:
        print("❌ Admin not found. Raising 404.")
        raise Http404("Admin not found")
    
    if admin_user.is_staff:
        if request.method == "POST":
            password = request.POST["password"]
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Build URL using the URL pattern parameter 'admin'
                url = reverse("Monitering", kwargs={"admin": username})
                print(f"🔄 Redirecting to: {url}")
                return redirect(url)
            else:
                print("❌ Authentication failed! Redirecting to 'signup'.")
                return redirect("signup")
        else:
            print("Rendering 'loginA.html' for admin login.")
            return render(request, "loginA.html", {"admin": username})
    else:
        print("❌ User is not staff. Raising 404.")
        raise Http404

def Monitering(request, admin):
    try:
        admin_user = MyUser.objects.get(username=admin)
    except MyUser.DoesNotExist:
        print("❌ Admin not found in Monitering. Raising 404.")
        raise Http404("page not found")

    if admin_user.is_staff:
        
        if request.method == "POST":
            print(request.POST)
            transactiontype=request.POST["transaction_type"]
            print(transactiontype)
            if transactiontype == "withdrawal":
                print("Withdrawal in")
                amount = request.POST["amount"]
                user = request.POST["username"]
                phoneNumber= request.POST["phone_number"]
                AdminRES = request.POST["adminres"]
                print(transactiontype)
                try:
                    Player = MyUser.objects.get(username=user)
                    PlayerB = Ballance.objects.get(user=Player)
                    WR = WithdrawalRequest.objects.filter(user=Player, status="Pending")

                    if  WR.exists() and AdminRES == "Approved":
                        
                        Player.pendingWithdrwal = False
                        
                        Player.save()
                        WR.update(status="Approved")
                        messages.success(request, f"✅ approved {amount} ETB to {user}.")
                        print(f"✅ Approved transaction: {user} - {amount} ETB. Rendering 'admin.html'.")
                        return JsonResponse({"success":True,"message":"withdrawal request has been approved"})
                    elif AdminRES == "Rejected":
                        WR.update(status="Rejected")
                        Player.pendingWithdrwal = False
                        Player.withdrawalToken = None
                        PlayerB.ballance += Decimal(amount)
                        PlayerB.save()
                        Player.save()
                        messages.error(request, f"❌ rejected {amount} ETB to {user}.")
                        print(f"❌ Rejected transaction: {user} - {amount} ETB. Rendering 'admin.html'.")
                        return JsonResponse({"success":True, "message":"withdrawal request has been rejected"})
                    
                    else:
                        return JsonResponse({"success":False, "message":"the request is already on pending "})
                    
             
                except MyUser.DoesNotExist:
                    print("❌ User does not exist!")
                except Ballance.DoesNotExist:
                    print("❌ User has no balance record!")
            elif transactiontype == "profit":
                profit=chiweProfit.objects.all().aggregate(total=Sum("profit"))
                print(profit)
                amount=request.POST["amount"]
                if Decimal(amount)>profit["total"]:
                    return JsonResponse({"success":False,"message":"insufficient balance"})
                count = chiweProfit.objects.count()
                if count == 0:
                    JsonResponse({"success":False,"message":"the amount is not enough"})
                else:
                    chiweProfit.objects.all().delete()
                    return JsonResponse({"success":True,"message":"updated profit "})
            elif transactiontype == "men":
                maintenance = Maintainance.objects.get(pk=1)
                print(maintenance.enabled)
                enabled=request.POST["enabled"]
                if enabled == "false":
                    enabled=False
                    msg="Server is now live to all players"
                else:
                    enabled=True
                    msg="Server is now in maintenance mode"
                if maintenance.enabled == enabled:
                    return JsonResponse({"success":True,"message":"the server is already in this mode"})
                maintenance.enabled=enabled
                maintenance.save()
                return JsonResponse({"success":True,"message":msg})
            else:
                return JsonResponse({"success":False,"message":"invalid message"})
        Pdata = WithdrawalRequest.objects.filter(status="Pending")
        Adata = WithdrawalRequest.objects.filter(status="Approved")
        Rdata = WithdrawalRequest.objects.filter(status="Rejected")
        profit=chiweProfit.objects.all().aggregate(total=Sum("profit"))
        
        
            
        print(f"📊 Admin: {admin} - Pending: {Pdata.count()}, Approved: {Adata.count()}, Rejected: {Rdata.count()}")
        print("Rendering 'admin.html' with current data.")
        print(profit["total"])
        totalp=profit["total"] or Decimal(0.00)
        maintenance = Maintainance.objects.get(pk=1)
        return render(request, "admin.html", {"Adata": Adata, "Pdata": Pdata, "Rdata": Rdata, "admin": admin,"profit":totalp ,"maintenance":maintenance})
    else:
        print("❌ User is not staff in Monitering. Raising 404.")
        raise Http404
from django.db import transaction
from django.db.models import F
from django.http import JsonResponse

def check_transaction(username: str, tx_id: str,way):
    tx_id = tx_id.upper()
    if way=="tb":

    # Wrap the whole thing in an atomic block
        with transaction.atomic():
            try:
                # Lock the TelebirrReq row so concurrent threads queue up here
                req = (TelebirrReq.objects
                    .select_for_update()
                    .get(tx_id=tx_id))
            except TelebirrReq.DoesNotExist:
                return JsonResponse({
                    "status": False,
                    "message": "Your transaction id is not valid, please try again in a few minutes or use a new one"
                })

            if req.completed:
                return JsonResponse({
                    "status": False,
                    "message": "Your deposit has already been approved, please use a new one"
                })

            # Lock the user balance row too
            user = MyUser.objects.get(username=username)
            bal = (Ballance.objects
                .select_for_update()
                .get(user=user))

            # Credit using an F-expression so it’s done in the database
            bal.ballance = F("ballance") + req.amount
            bal.save()

            # Mark request completed
            req.completed = True
            req.save()

            # Clear the pending-deposit flag
            user.pendingDeposit = False
            user.save()

            return JsonResponse({
                "status": True,
                "message": f"Your deposit for {req.amount} ETB has been approved"
            })
    else:
        with transaction.atomic():
            try:
                # Lock the TelebirrReq row so concurrent threads queue up here
                req = (Ebirreq.objects
                    .select_for_update()
                    .get(tx_id=tx_id))
            except Ebirreq.DoesNotExist:
                return JsonResponse({
                    "status": False,
                    "message": "Your transaction id is not valid, please try again in a few minutes or use a new one"
                })

            if req.completed:
                return JsonResponse({
                    "status": False,
                    "message": "Your deposit has already been approved, please use a new one"
                })

            # Lock the user balance row too
            user = MyUser.objects.get(username=username)
            bal = (Ballance.objects
                .select_for_update()
                .get(user=user))

            # Credit using an F-expression so it’s done in the database
            bal.ballance = F("ballance") + req.amount
            bal.save()

            # Mark request completed
            req.completed = True
            req.save()

            # Clear the pending-deposit flag
            user.pendingDeposit = False
            user.save()

            return JsonResponse({
                "status": True,
                "message": f"Your deposit for {req.amount} ETB has been approved"
            })
@login_required
def deposit(request):
    maintenance = Maintainance.objects.first()
    if maintenance and maintenance.enabled:
        return render(request, 'maintenance.html')
    if request.method == "POST":
        user = MyUser.objects.get(username=request.user.username)
        if user.pendingDeposit:
            return JsonResponse({
                "status": False,
                "message": "You already have a pending deposit request. Please wait for it to be completed."
            })
        tx_id = request.POST["tx_id"]
        way=request.POST["way"]
        if way=="tb":
            print("tb")
            return check_transaction(user.username, tx_id,way="tb")
        elif way=="eb":
            print("eb")
            return check_transaction(user.username,tx_id=tx_id,way="eb")
        else:
            return JsonResponse(request,{
                "sucess":False,"message":"please select the way you deposited the money"
            })

    return render(request, "deposit.html")

