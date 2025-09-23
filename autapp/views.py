import os
from django.contrib import messages
from django.shortcuts import render,redirect
import hashlib
import time
from .models import MyUser,Ballance,GameHistory,Maintainance,PiPayment
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import login, authenticate,logout
from django.http import FileResponse, Http404, JsonResponse
from django.contrib.auth import login
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
import json, requests
from django.middleware.csrf import get_token
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

# Pi API configuration - prefer settings, fallback to environment variables
# Default to the official production API host. For sandbox/testing you can
# override `PI_API_BASE` in Django settings or set the env var `PI_API_BASE`.
PI_API_BASE = getattr(settings, 'PI_API_BASE', os.environ.get('PI_API_BASE', 'https://api.minepi.com/v2'))
# Hardcoded Server API Key (temporary for demo/hackathon)
SERVER_API_KEY = '7vqrbckrr4fvplcmt5ox3uqyhfxlaiwwqde3jjvt3gn1oo9ni4yyn0utxlb6e9yk'

def get_csrf_token(request):
    """
    View to provide a fresh CSRF token via AJAX.
    This is useful for SPA applications or when cookies might be blocked.
    """
    csrf_token = get_token(request)
    return JsonResponse({'csrf_token': csrf_token})
def username_to_id(username):
    h = hashlib.sha256(username.encode()).hexdigest()
    return int(h[:16], 16) % 10**8

def send_welcome_email(user, email,token,why):
    subject = 'Welcome to Chiwe'
    from_email = settings.DEFAULT_FROM_EMAIL
    to_email = email
    # Render the HTML template with context
    if why=="signup":
        html_content = render_to_string('otp.html', {'user': user,'token':token})
    else:
        html_content = render_to_string('forgot.html', {'user': user,'token':token})
    # Create the email message
    email = EmailMessage(subject, html_content, from_email, [to_email])
    email.content_subtype = 'html'  # Set the content type to HTML
    # Send the email
    email.send()

def generate_unique_number(username):
    # Get the current timestamp
    timestamp = str(time.time())

    # Combine the username and timestamp
    seed = username + timestamp

    # Create a hash of the seed
    hash_object = hashlib.sha256(seed.encode())

    # Convert the hash to an integer and get the last 6 digits
    unique_number = int(hash_object.hexdigest(), 16) % 1000000

    # Ensure the number is 6 digits by padding with zeros if necessary
    return str(unique_number).zfill(6)

def index(request):
    
    return render(request,'index.html')
def signup(request,ref):
    if request.method == 'POST':
        username = request.POST['username'].upper()
        firstname = request.POST['first_name']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']
        referal=request.POST.get('referal', None)
        rewarded=''
        try:
            validate_email(email)
            print("Valid email")
        except ValidationError:
            return JsonResponse({"success": False, "message":"Invalid email address."})
        if not username or not firstname or not email or not password or not password2:
            return JsonResponse({"success": False, "message":"All fields are required."})
        if len(username) < 4:
            return JsonResponse({"success": False, "message":"Username must be at least 4 characters."})

         
        if password != password2:
            return JsonResponse({"success": False, "message":"Passwords do not match."})
            
        if len(password) < 6:
            return JsonResponse({"success": False, "message":"Password must be at least 6 characters."})
       
        
                # Check for active user conflicts
        invalid_chars = set(' @#$/&*><-_.!%^()+=[]{}|~`,;:\'"')
        if any(char in username for char in invalid_chars) or not username:
            return JsonResponse({"success": False, "message":"Username must not contain spaces or special characters."})

        if MyUser.objects.filter(username=username, is_active=True).exists():
            return JsonResponse({"success": False, "message":"Username already exists, try another one."})
        if MyUser.objects.filter(email=email, is_active=True).exists():
            return JsonResponse({"success": False, "message":"Email already exists, try another one."})
        
        # If inactive user exists, remove it
        inactive_user = MyUser.objects.filter(username=username, is_active=False).first()
        if inactive_user:
            inactive_user.delete()
        inactive_email = MyUser.objects.filter(email=email, is_active=False).first()
        if inactive_email:
            inactive_email.delete()
        if referal!= None and referal!="":
            try:
           

                    
                rewarded=MyUser.objects.get(referalCode=referal)
                rewarded.referedCount+=1
                rewarded.save()
            except MyUser.DoesNotExist:
                print(referal=="")
                print("DNE")
                return JsonResponse({"success": False, "message":"Invalid referal code."})
       
        token = generate_unique_number(username)
        user = MyUser.objects.create_user(
            username=username,
            first_name=firstname,
            email=email,
            password=password,
            token=token,
            referedBy=referal,
            referalCode=username_to_id(username)
            
        )
        
        Ballance.objects.create(user=user, ballance=0.00)
        user.is_active = False  # User needs to verify via email
        user.save()
        print("finished")
        try:
            send_welcome_email(user, email, token,why="signup")
            return JsonResponse({"success": True, "message":"OTP has been sent to your email, please check your inbox.",
                                 "username":username})
        except Exception as e:
            print(e)
            
            user.delete()
            return JsonResponse({"success": False, "message":"system is busy , please sign up again."})
    if ref=="1":
        return render(request, 'signup.html')
    else:
        return render(request, 'signup.html',{'referal':ref})


@csrf_exempt
def pi_auth(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "POST required"}, status=400)

    try:
        # Robustly parse incoming data (JSON body or form-encoded)
        data = {}
        if request.content_type and 'application/json' in request.content_type:
            try:
                body = request.body.decode('utf-8') if request.body else ''
                data = json.loads(body) if body else {}
            except Exception:
                data = {}
        else:
            # fallback to form-encoded data
            data = request.POST.dict() if hasattr(request, 'POST') else {}

        # Normalize possible payload shapes
        access_token = (data.get('accessToken') or data.get('access_token') or data.get('token'))
        username = None
        if isinstance(data.get('user'), dict):
            username = data['user'].get('username') or data['user'].get('uid')
        username = username or data.get('username') or data.get('uid') or data.get('user')

        if not username:
            return JsonResponse({"success": False, "error": "Missing username in payload"}, status=400)

        # Step 1: Verify with Pi API using the client's access token
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.get(f"{PI_API_BASE}/me", headers=headers)


        pi_data = None
        # If we have an access token, verify it with Pi API
        if access_token:
            try:
                if response.status_code != 200:
                    print("pi error status", response.status_code, response.text)
                    return JsonResponse({"success": False, "error": "Pi verification failed"}, status=401)
                pi_data = response.json()
            except Exception as e:
                print('pi verification parse error', e)
                return JsonResponse({"success": False, "error": "Pi verification parse error"}, status=500)

            pi_username = pi_data.get("username")
            if pi_username != username:
                return JsonResponse({"success": False, "error": "Username mismatch"}, status=403)
        else:
            # No access token provided. In production we should reject this.
            # For local development (DEBUG=True) allow it for convenience.
            if getattr(settings, 'DEBUG', False):
                print('pi_auth: no access token provided, proceeding in DEBUG mode')
                # treat incoming data as pi_data if it looks like one
                pi_data = data
            else:
                return JsonResponse({"success": False, "error": "Missing access token"}, status=400)

        # Step 2: Create or get Django user
        # Create or get a user safely. Put creation-only fields in defaults.
        user_defaults = {
            'first_name': pi_data.get('username') if pi_data else username,
            'referalCode': username_to_id(username),
        }
        user, created = MyUser.objects.get_or_create(username=username, defaults=user_defaults)
        if created:
            # Don't set a usable password here; mark account active and set unusable password
            user.set_unusable_password()
            user.is_active = True
            user.save()
        else:
            user.is_active = True
            user.save()

        Ballance.objects.get_or_create(user=user, ballance=0.00)
        GameHistory.objects.get_or_create(user=user, defaults={
            'TotalPlayed': 0, 'TotalWin': 0, 'Totaloss': 0, 'TotalEarning': 0.00
        })

        # Log the user in. Since we may not have credentials, set backend and call login()
        try:
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
        except Exception as e:
            print('pi_auth: login error', e)
            return JsonResponse({"success": False, "error": "Login failed"}, status=500)
        # Debug: print incoming cookies to see if browser sent any
        try:
            print("PI AUTH - incoming request.COOKIES:", request.COOKIES)
        except Exception:
            pass

        # Ensure the session is saved so Django will issue a Set-Cookie header
        try:
            request.session.save()
        except Exception:
            pass

        # Build JSON response and explicitly set the session cookie to be safe
        response = JsonResponse({
            "status": "success",
            "username": user.username,
            "uid": str(user.id),
            "accessToken": access_token,
            "pi_data": pi_data
        })

        # Explicitly set the session cookie value on the response to ensure
        # the browser receives it (helps when using fetch + credentials).
        try:
            # Ensure session is saved and set cookie
            request.session.save()
            session_key = request.session.session_key
            print("PI AUTH - created session_key:", session_key)
            if session_key:
                response.set_cookie(
                    settings.SESSION_COOKIE_NAME,
                    session_key,
                    secure=getattr(settings, 'SESSION_COOKIE_SECURE', False),
                    httponly=True,
                    samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
                )
        except Exception as e:
            print("PI AUTH - set_cookie error:", e)

        # For debugging locally, include the session_key in the JSON response when DEBUG
        try:
            if getattr(settings, 'DEBUG', False):
                # include session key for local debugging
                resp = json.loads(response.content)
                resp['session_key'] = request.session.session_key
                response = JsonResponse(resp)
                if request.session.session_key:
                    response.set_cookie(
                        settings.SESSION_COOKIE_NAME,
                        request.session.session_key,
                        secure=getattr(settings, 'SESSION_COOKIE_SECURE', False),
                        httponly=True,
                        samesite=getattr(settings, 'SESSION_COOKIE_SAMESITE', 'Lax')
                    )
        except Exception as e:
            print("PI AUTH - debug include session_key error:", e)

        print('pi_data:', pi_data)
        return response
    except Exception as e:
        print('pi_auth exception:', e)
        return JsonResponse({"success": False, "error": str(e)}, status=500)
def verify(request, username):
   
    user = get_object_or_404(MyUser, username=username)
    if user.is_active: 
        raise Http404
    if request.method == 'POST':
        print(request.POST)
        if request.POST.get('type')=="fp":
           
            if str(username)==str(request.POST.get('username')):
               
               return resend_otp_signup(request, user)
            else:
                return JsonResponse({"success":False,"message":"Something went wrong , please refresh the page"})
        if not request.POST.get('otp_code'):
            return JsonResponse({"success": False, "message":"OTP is required."})
        
            
        token = request.POST['otp_code']
        print(user.token)
        if user.token == token:
            user.is_active = True
            GameHistory.objects.get_or_create(user=user,TotalPlayed=0,TotalWin=0,Totaloss=0,TotalEarning=0.00,)
            user.save()
            login(request, user)
            
            return JsonResponse({"success": True, "message":"Account Verified successfully, redirecting you to the login page "})  # Redirect to the home page or any other page
        else:
            
            return JsonResponse({"success": False, "message":"Invalid token"})
    
    return render(request, 'activate.html', {'user': user})

from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip().upper()
        password = request.POST.get('password', '')

        if not username or not password:
           
            return JsonResponse({"success": False, "message":"Username and password are required."})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True, "message":"Login successful."})
        else:
            
            return JsonResponse({"success": False, "message": "Invalid username or password"})
            
    else:
        return render(request, 'login.html')

def dashboard(request):
    print("im trigered")
    # Ensure only authenticated users can access the dashboard
    from django.contrib.auth.decorators import login_required

    # If a user is not authenticated, redirect to login (login_required handles this when used as decorator)
    if not request.user.is_authenticated:
        print("not authenticated")
        return redirect('login')

    # Use the authenticated user instance directly rather than querying by username
    user = request.user
    try:
        ballance = Ballance.objects.get(user=user).ballance
    except Ballance.DoesNotExist:
        ballance = 0.00

    return render(request, 'dashboard.html', {'user': user, 'ballance': ballance})
@login_required
def profile(request):
    if request.method == 'POST':
        user = request.user
        first_name=request.POST['first_name']
        last_name=request.POST['last_name']
        
        username=request.POST['username'].upper()
        if " " in username:
            return JsonResponse({"success": False, "message":"Username must not contain spaces."})
        
        if MyUser.objects.filter(username=username).exists():
            if request.user.username != username:
                return JsonResponse({"success": False, "message":"Username already exists, try another one."})
            else:
                if len(first_name)>200 :
                    return JsonResponse({"success": False, "message":"First name and last name must be less than 200 characters"})
                else:
                    user_obj=MyUser.objects.get(username=user.username)
                    user_obj.first_name=first_name
                    user_obj.last_name=last_name
                    user_obj.username=username  
                    
            try:
                user_obj.save()
                return JsonResponse({"success": True, "message":"Profile updated successfully."})
            except Exception as e:
                return render(request,'profile.html')
        else:
            if len(first_name)>200  :
                return JsonResponse({"success":False,"messaege":"First name and last name must be less than 200 characters"})
            else:
                user_obj=MyUser.objects.get(username=user.username)
                user_obj.first_name=first_name
                user_obj.username=username  
                try:
                    user_obj.save()
                    return JsonResponse({"success": True, "message":"Profile updated successfully."})
                except Exception as e:
                    return JsonResponse({"success": False, "message":"Erorr updating profile try again"})
    user_file=MyUser.objects.get(username=request.user.username)
    Game_Stat, created = GameHistory.objects.get_or_create(
    user=user_file, 
    defaults={"TotalEarning": 0.00, "TotalPlayed": 0, "TotalWin": 0, "Totaloss": 0}
)

    ballance=Ballance.objects.get(user=user_file)
    print(f"total earning {Game_Stat.TotalEarning}") 
    print(f"total played {Game_Stat.TotalPlayed}")
    print(f"total won {Game_Stat.TotalWin}")
    print(f"total loss {Game_Stat.Totaloss}")

    return render(request, 'profile.html', {'user': request.user, 'stat': Game_Stat,'ballance':ballance})

@login_required
def logout_view(request):
    user=MyUser.objects.get(username=request.user.username)
    user.is_logged_in=False
    logout(request) 
    
    return redirect('login')
def forgot_password(request):
    if request.method == "POST":
        print(request.POST)
        email = request.POST["email"]
        try:
            user = MyUser.objects.get(email=email)
            if not user.is_active:
                return JsonResponse({"Success": False, "message":"User is not active."})
            otp = generate_unique_number(user.username)
            user.forgetPasswordToken = otp
            user.save()
            send_welcome_email(user=user, email=email, token=otp, why="forgot")
            return JsonResponse({"Success": True, "message":"OTP has been sent to your email, please check your inbox."})  # Redirect to the home page or any other page
        except MyUser.DoesNotExist:
            return JsonResponse({"Success": False, "message":"User not found."}) # Redirect to the home page or any other page
    else:
        return render(request, "forgot_password.html")
@require_POST 
def validate_recovery(request):
    if request.method == "POST":
        print(request.POST)
        email = request.POST["email"]
        token = request.POST["otp"]
        pass1=request.POST["new_password"]
        pass2=request.POST["confirm_password"]
        try:
            user = MyUser.objects.get(email=email)
            if not user.is_active:
                return JsonResponse({"Success": False, "message":"User is not active."})
            print(type(str(user.forgetPasswordToken)))
            print(type(token))
            if str(user.forgetPasswordToken) == token:
                if pass1==pass2:
                    if len(pass1)>6:
                        user.set_password(pass1)
                        user.save()
                        return JsonResponse({"Success": True, "message":"Password changed successfully."})  # Redirect to the home page or any other page
                    else:
                        return JsonResponse({"Success": False, "message":"Password must be at least 6 characters."})  # Redirect to the home page or any other page
                else:
                    return JsonResponse({"Success": False,"message":"Passwords do not match."})  # Redirect to the home page or any other page

            else:
                return JsonResponse({"Success": False, "message":"OTP is invalid."})  # Redirect to the home page or any other page
        except MyUser.DoesNotExist:
            return JsonResponse({"Success": False, "message":"User not found."}) # Redirect to the home page or any other page
from django.utils import timezone
from datetime import timedelta

@require_POST
def resend_otp_signup(request, userobj):
    print("i got in ")
    try:
        user = userobj
    
        if user.is_active:
            return JsonResponse({"success": False, "message": "User is already active."})
        cooldown_period = timedelta(seconds=60)
        now = timezone.now()
        last_otp=user.last_otp_sent
        if last_otp and now - last_otp < cooldown_period:
            remaining = cooldown_period - (now - last_otp)
            return JsonResponse({
                "success": False,
                "message": f"Please wait {int(remaining.total_seconds())} seconds before resending OTP."
                })
        otp = generate_unique_number(user.username)
        user.token = otp
        user.last_otp_sent = now
        user.save()
        send_welcome_email(user=user, email=user.email, token=otp, why="signup")
        return JsonResponse({"success": True, "message": "OTP has been sent to your email. Please check your inbox or SPAM folder."})
    except MyUser.DoesNotExist:
        return JsonResponse({"success": False, "message": "User not found."})
@csrf_exempt
@require_POST
def resend_otp_token_fp(request):
    try:
        email=request.POST["email"]
        user = MyUser.objects.get(email=email)
        
        if not user.is_active:
            return JsonResponse({"Success": False, "message": "User is not actived, please signup again."})
        cooldown_period = timedelta(seconds=60)
        now = timezone.now()
        last_otp=user.last_otp_fp
        if last_otp and now - last_otp < cooldown_period:
            remaining = cooldown_period - (now - last_otp)
            return JsonResponse({
                "Success": False,
                "message": f"Please wait {int(remaining.total_seconds())} seconds before resending OTP."
                })
        otp = generate_unique_number(user.username)
        user.forgetPasswordToken = otp
        user.last_otp_fp = now
        user.save()
        send_welcome_email(user=user, email=user.email, token=otp, why="forgot")
        return JsonResponse({"Success": True, "message": "OTP has been sent to your email. Please check your inbox or SPAM folder."})
    except MyUser.DoesNotExist:
        return JsonResponse({"Success": False, "message": "User not found."})

def validate_key(request):
    filepath = os.path.join(settings.BASE_DIR, "autapp/validation-key.txt")
    return FileResponse(open(filepath, "rb"), content_type="text/plain")
@csrf_exempt
def pi_debug(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            print("PI DEBUG:", data)  # This shows up in Django logs
        except Exception as e:
            print("PI DEBUG ERROR:", e)
        return JsonResponse({"ok": True})
    return JsonResponse({"error": "GET not allowed"})


def session_debug(request):
    """Return current cookies and session key for debugging browser/server cookie exchange."""
    try:
        data = {
            'cookies': request.COOKIES,
            'session_key': request.session.session_key,
            'user_authenticated': request.user.is_authenticated,
            'username': getattr(request.user, 'username', None)
        }
    except Exception as e:
        data = {'error': str(e)}
    print("SESSION DEBUG:", data)
    return JsonResponse(data)


@csrf_exempt
def approve_debug(request):
    """
    Debug endpoint to show detailed request context for /api/pi-payments/approve troubleshooting.
    Returns headers, cookies, session key, CSRF token, user auth status and (optionally)
    Pi /me verification when an accessToken is provided in the JSON body.
    Only intended for DEBUG usage.
    """
    info = {}
    info['method'] = request.method
    info['headers'] = {k: v for k, v in request.headers.items()}
    info['cookies'] = request.COOKIES
    info['session_key'] = request.session.session_key
    info['user_is_authenticated'] = getattr(request.user, 'is_authenticated', False)
    info['user'] = getattr(request.user, 'username', None)
    # CSRF token available via middleware
    try:
        info['csrf_token'] = get_token(request)
    except Exception:
        info['csrf_token'] = None

    body = None
    try:
        body = json.loads(request.body.decode() or '{}')
    except Exception:
        body = {}
    info['body'] = body

    # If an access token is provided, attempt to verify it with Pi
    access_token = body.get('accessToken') or body.get('access_token')
    if access_token:
        try:
            me_resp = requests.get(f"{PI_API_BASE}/me", headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
            info['pi_me_status'] = me_resp.status_code
            try:
                info['pi_me_body'] = me_resp.json()
            except Exception:
                info['pi_me_body'] = me_resp.text[:1000]
        except Exception as e:
            info['pi_me_error'] = str(e)

    # Only return detailed info when DEBUG is True
    if not getattr(settings, 'DEBUG', False):
        return JsonResponse({'error': 'Not available'}, status=404)

    print('approve_debug:', info)
    return JsonResponse(info)
def server_headers():
    if not SERVER_API_KEY:
        print('WARNING: PI server API key is not configured (PI_SERVER_API_KEY not found in settings or env)')
        return {"Content-Type": "application/json"}
    # Pi approve endpoint expects the Server API Key in the form: "Authorization: Key <API_KEY>"
    auth_value = f"Key {SERVER_API_KEY}"
    headers = {
        "Authorization": auth_value,
        "Content-Type": "application/json",
        "Authorisation": auth_value,
        "authorization": auth_value,
    }
    return headers

@require_POST
def approve_payment(request):
    # Parse JSON body safely
    try:
        print('approve_payment: incoming request path=', request.path, 'method=', request.method, 'remote_addr=', request.META.get('REMOTE_ADDR'))
        # preview first few headers
        try:
            hdr_items = list(request.headers.items())[:10]
            print('approve_payment: headers preview=', hdr_items)
        except Exception:
            pass
    except Exception:
        pass
    try:
        data = json.loads(request.body.decode() or '{}')
    except Exception as e:
        print('approve_payment: invalid JSON body', e)
        return JsonResponse({'error': 'invalid JSON body'}, status=400)

    print('approve_payment: incoming data', data)
    # If requester is not authenticated, allow a fallback where the client
    # provides a Pi accessToken. We will verify it with Pi (/v2/me) and map
    # or create a user for this approval. This avoids depending on session
    # cookies in environments where cookies are not sent by the Pi browser.
    user_obj = None
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        access_token = data.get('accessToken') or data.get('access_token')
        if not access_token:
            print('approve_payment: unauthenticated request and no accessToken provided')
            return JsonResponse({'status': 'error', 'detail': 'Authentication required'}, status=401)
        # Verify access token with Pi
        try:
            me_resp = requests.get(f"{PI_API_BASE}/me", headers={"Authorization": f"Key {SERVER_API_KEY}"}, timeout=10)
            if me_resp.status_code != 200:
                print('approve_payment: PI /me verification failed', me_resp.status_code, me_resp.text[:200])
                return JsonResponse({'status': 'error', 'detail': 'Invalid access token'}, status=401)
            pi_user = me_resp.json()
            pi_username = pi_user.get('username') or pi_user.get('uid')
            if not pi_username:
                return JsonResponse({'status': 'error', 'detail': 'Could not determine Pi username from token'}, status=401)
            # Get or create a MyUser for this pi_username
            user_defaults = {'first_name': pi_username, 'referalCode': username_to_id(pi_username)}
            user_obj, created = MyUser.objects.get_or_create(username=pi_username, defaults=user_defaults)
            if created:
                user_obj.set_unusable_password()
                user_obj.is_active = True
                user_obj.save()
        except Exception as e:
            print('approve_payment: exception verifying access token', e)
            return JsonResponse({'status': 'error', 'detail': 'Error verifying access token'}, status=500)
    else:
        user_obj = request.user
    payment_id = data.get("paymentId")
    amount = data.get("amount")
    if not payment_id:
        return JsonResponse({"error": "missing paymentId"}, status=400)

    p, _ = PiPayment.objects.get_or_create(
        payment_id=payment_id,
        defaults={"user": user_obj, "status": "pending", 'amount': amount}
    )

    # Ensure server API key is configured (log presence only)
    print('approve_payment: SERVER_API_KEY present?', 'yes' if SERVER_API_KEY else 'no')
    if not SERVER_API_KEY:
        p.status = 'failed'
        p.save()
        return JsonResponse({
            'status': 'error',
            'detail': 'Server API key not configured on backend (PI_SERVER_API_KEY).'
        }, status=500)

    # Call Pi approve endpoint (server-to-server)
    url = f"{PI_API_BASE}/payments/{payment_id}/approve"
    print('approve_payment: calling Pi approve URL', url)
    try:
        r = requests.post(url, headers=server_headers(), timeout=15)
    except Exception as e:
        print('approve_payment: exception calling Pi approve', e)
        p.status = 'failed'
        p.save()
        return JsonResponse({'status': 'error', 'detail': str(e)}, status=500)

    # Log response for debugging
    print('approve_payment: Pi response status', r.status_code)
    try:
        print('approve_payment: Pi response body', r.text)
    except Exception:
        pass

    # If Pi indicates invalid authorization, return a clear message (likely wrong/missing server key)
    if r.status_code == 401:
        detail = None
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        print('approve_payment: Pi returned 401 invalid_authorization')
        p.status = 'failed'
        p.save()
        return JsonResponse({'status': 'error', 'detail': 'Pi API returned 401 invalid_authorization - Server API Key may be missing or invalid', 'pi': detail}, status=401)

    if r.status_code in (200, 201):
        try:
            p.status = "approved"
            p.save()
        except Exception:
            pass
        try:
            return JsonResponse({"status": "ok", "detail": r.json()})
        except Exception:
            return JsonResponse({"status": "ok", "detail": r.text})

    # non-2xx => failure
    p.status = "failed"
    p.save()
    # Return Pi response details to help debugging
    detail = None
    try:
        detail = r.json()
    except Exception:
        detail = r.text
    return JsonResponse({"status": "error", "detail": detail}, status=max(400, r.status_code))

@require_POST
def complete_payment(request):
    try:
        data = json.loads(request.body.decode())
    except Exception as e:
        print('approve_payment: invalid JSON body', e, getattr(request, 'body', None))
        return JsonResponse({'error': 'invalid JSON body'}, status=400)
    payment_id = data.get("paymentId")
    txid = data.get("txid")
    if not payment_id or not txid:
        return JsonResponse({"error": "missing paymentId or txid"}, status=400)

    # If unauthenticated, accept client accessToken and verify with Pi
    user_obj = None
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        access_token = data.get('accessToken') or data.get('access_token')
        if not access_token:
            print('complete_payment: unauthenticated request and no accessToken provided')
            return JsonResponse({'status': 'error', 'detail': 'Authentication required'}, status=401)
        try:
            me_resp = requests.get(f"{PI_API_BASE}/me", headers={"Authorization": f"Bearer {access_token}"}, timeout=10)
            if me_resp.status_code != 200:
                print('complete_payment: PI /me verification failed', me_resp.status_code, me_resp.text[:200])
                return JsonResponse({'status': 'error', 'detail': 'Invalid access token'}, status=401)
            pi_user = me_resp.json()
            pi_username = pi_user.get('username') or pi_user.get('uid')
            if not pi_username:
                return JsonResponse({'status': 'error', 'detail': 'Could not determine Pi username from token'}, status=401)
            user_defaults = {'first_name': pi_username, 'referalCode': username_to_id(pi_username)}
            user_obj, created = MyUser.objects.get_or_create(username=pi_username, defaults=user_defaults)
            if created:
                user_obj.set_unusable_password()
                user_obj.is_active = True
                user_obj.save()
        except Exception as e:
            print('complete_payment: exception verifying access token', e)
            return JsonResponse({'status': 'error', 'detail': 'Error verifying access token'}, status=500)
    else:
        user_obj = request.user

    p, _ = PiPayment.objects.get_or_create(
        payment_id=payment_id,
        defaults={"user": user_obj, "status": "pending"}
    )
    p.txid = txid
    p.save()
    # Call Pi approve endpoint (server-to-server)
    url = f"{PI_API_BASE}/payments/{payment_id}/approve"
    print('approve_payment: calling Pi approve URL', url)
    try:
        r = requests.post(url, headers=server_headers(), timeout=15)
    except Exception as e:
        print('approve_payment: exception calling Pi approve', e)
        p.status = 'failed'
        p.save()
        return JsonResponse({'status': 'error', 'detail': str(e)}, status=500)

    # Log response for debugging
    print('approve_payment: Pi response status', r.status_code)
    try:
        print('approve_payment: Pi response body', r.text)
    except Exception:
        pass

    if r.status_code == 401:
        detail = None
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        print('approve_payment (complete): Pi returned 401 invalid_authorization')
        p.status = 'failed'
        p.save()
        return JsonResponse({'status': 'error', 'detail': 'Pi API returned 401 invalid_authorization - Server API Key may be missing or invalid', 'pi': detail}, status=401)

    if r.status_code in (200, 201):
        try:
            p.status = "approved"
            p.save()
        except Exception:
            pass
        try:
            return JsonResponse({"status":"ok", "detail": r.json()})
        except Exception:
            return JsonResponse({"status":"ok", "detail": r.text})

    # non-2xx => failure
    p.status = "failed"
    p.save()
    # Return Pi response details to help debugging (but avoid leaking secrets)
    detail = None
    try:
        detail = r.json()
    except Exception:
        detail = r.text
    return JsonResponse({"status":"error", "detail": detail}, status=max(400, r.status_code))
    if p:
        p.status = "failed"
        p.save()
    return JsonResponse({"status":"error", "detail": r.text}, status=400)