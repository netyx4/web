from django.shortcuts import render, redirect

# Create your views here.
from django.http import HttpResponse, JsonResponse
from datetime import datetime
from django.contrib.auth.hashers import make_password, check_password
from django import forms
from TAMATAMA.models import models_tamagochi, models_shop, models_messages, models_friend_invites, CustomUser
from django.contrib.auth import get_user_model
from TAMATAMA.forms import form_account, form_messages, form_login

#from django.contrib.auth.models import User
User = get_user_model()

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view
from rest_framework.response import Response

from coinbase_commerce.client import Client
from TAMACOPY import settings

import paypalrestsdk

@api_view(["POST"])
def get_auth_token(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "User not authenticated"}, status=401)

    token, _ = Token.objects.get_or_create(user=user)
    return Response({"token": token.key})
    

def reg(request):
    if request.method == "POST":
        form = form_account(request.POST)
        if form.is_valid():
            username = form.cleaned_data["acc_username"]
            email = form.cleaned_data["acc_email"]
            password = form.cleaned_data["acc_p"]
            password2 = form.cleaned_data["acc_password2"]
            if len(password) >= 8 and password == password2:
                #password = make_password(password)
                user1 = User.objects.create_user(username = username, password = password, email = email, bg_color = "#C1CFA1")
                user1.save()
                return redirect("/")
            else:
                if len(password) < 8:
                    form.add_error("acc_p", "Password must be at least 8 characters long.")
                if password != password2:
                    form.add_error("acc_password2", "Passwords do not match.")

    else:
        form = form_account()

    return render(request, "template_register.html", {"form" : form})




def login_site(request):
    if request.method == "POST":
        form = form_login(request.POST)
        if form.is_valid():
            username = form.cleaned_data["acc_username"]
            password = form.cleaned_data["acc_password"]    
            #password = make_password(password)
            if User.objects.filter(username = username).exists():
                user = authenticate(username = username, password = password)
            else:
                form.add_error("acc_username", "Username does not exist.")
                return render(request, "template_login.html", {"form" : form})

            if user:
                login(request, user)
                return redirect("/tamagochi")
            else:
                form.add_error("acc_password", "Wrong password.")
                messages.error(request, "loch")
    else:
        form = form_login()


    return render(request, "template_login.html", {"form" : form})
def home(request):

    if request.user.is_authenticated:
        logged = True
        c = User.objects.filter(username = request.user).first()
        color = c.bg_color
        color = "#7a54c4"

    else:
        logged = False
        color = "#C1CFA1"

    return render(request, "template_home.html", {"logged" : logged, "username" : request.user, "color" : color})
def user(request, username):
    user1 = User.objects.filter(username = username).first()    
    friend_invites = models_friend_invites.objects.filter(player1 = username)
    friend_invites2 = models_friend_invites.objects.filter(player2 = username)
    if request.method == "POST":
        action = request.POST.get("action")
        if action == "add":
            if not friend_invites and not friend_invites2:
                models_friend_invites.objects.get_or_create(player1=request.user.username, player2=user1.username, defaults={"is_accepted": False})

        elif action == "delete":
            models_friend_invites.objects.filter(player1=user1.username, player2=request.user.username).delete()

        elif action.startswith("accept"):
            invite = models_friend_invites.objects.filter(player1=action[6:], player2=request.user.username).first()
            if invite:
                invite.is_accepted = True
                invite.save()

        elif action.startswith("reject"):
            models_friend_invites.objects.filter(player1=action[6:], player2=request.user.username).delete()

    parameters = models_tamagochi.objects.filter(tam_owner = user1).first()

    existing_tamagochi = False
    friend = False


    if user1.username == request.user.username:
        our_page = True
    else:
        our_page = False


    friends = []
    invites = []

    for i in friend_invites:
        if i.is_accepted:
            friends.append(str(i.player2))
    
    for i in friend_invites2:
        if i.is_accepted:
            friends.append(str(i.player1))   
        else:
            invites.append(str(i.player1))
    #print(friend_invites.values())
    #print(friend_invites2.values())
    #print(friends)


    if friend_invites or friend_invites2:
        friend = True


    if parameters:
        existing_tamagochi = True



    #"friends_list" : friend_list.acc_friends
    to_render = {"form" : form_login, "acc_username" : user1, "our_page" : our_page, "username" : request.user, "existing_tamagochi" : existing_tamagochi, "friend" : friend, 
     }
    if existing_tamagochi == True:
        to_render["last_joined"] = parameters.tam_timeleft
        to_render["needs"] = parameters.tam_water+parameters.tam_food+parameters.tam_sleep+parameters.tam_playtime
        to_render["money"] = parameters.tam_money
    if our_page == True:
        to_render["invites"] = invites
    if len(friends) >= 1:
        to_render["spisok_friends"] = friends
    return render(request, "template_user.html", to_render)






def settings(request):
    if request.user.is_authenticated:
        player_model = models_tamagochi.objects.filter(tam_owner = request.user).first()
        tam_bought = player_model.tam_bought
        tam_bought = tam_bought.split(" ")
        skins = [{"name":"pikachu","image":"pikachu.png"}]
        for i in tam_bought[:-1]:
            skins.append({"name":i[:len(i)-4],"image" : i})

        if request.method == "POST":
            skin = request.POST["skin_button"]
            models_tamagochi.objects.filter(tam_owner=request.user).update(tam_skin = skin)

        current_skin = player_model.tam_skin

    else:
        return redirect("/login")
    return render(request, "template_settings.html",{"username" : request.user, "skins" : skins, "current_skin" : current_skin})
def shop(request):
    if request.user.is_authenticated:
        request.session.save()  # Ensure session exists
        client = Client(api_key = settings.COINBASE_COMMERCE_API_KEY)
        url = "http://127.0.0.1:8000"
        product = {"name":"500 coins", "description":"you get 500 coins",
        "local_price": {"amount": "1", "currency" : "EUR"}, "pricing_type" : "fixed_price",
        "redirect_url": url+"/good", "cancel_url":url+"/bad"}
        check = client.charge.create(**product)

       

        return render(request, "template_shop.html", {"check": check, "check_paypal":make_payment(request)})
    else:
        return redirect("login/")
def gameshop(request):
    if request.user.is_authenticated:
        player_model = models_tamagochi.objects.filter(tam_owner = request.user).first()
        shop_objects = list(models_shop.objects.values_list("item_pic", flat = True))
        shop_price = list(models_shop.objects.values_list("item_price", flat = True))
        if request.method == "POST":
            item = request.POST["gameshop_item"]
            tam_bought = player_model.tam_bought
            tam_money = player_model.tam_money
            if item not in tam_bought and tam_money >= shop_price[shop_objects.index(item)]:
                tam_bought += item + " "
                tam_money -= shop_price[shop_objects.index(item)]
                models_tamagochi.objects.filter(tam_owner=request.user).update(tam_bought = tam_bought, tam_money = tam_money)

        skins = []
        for i in range(len(shop_objects)):
            #shop_objects[i] = shop_objects[i][:-4]
            skins.append({"image" : shop_objects[i], "price" : shop_price[i]})
#           for i in range (len(shop_objects)):
#               if shop_objects[i] == request.POST:
#                    player_model = models_tamagochi.objects.filter(tam_owner = request.user).first()
#                   if shop_objects[i] not in player_model.tam_bought and player_model.tam_money > shop_price[i]:
#                        player_model.tam_bought += shop_objects[i] + " "
#                        player_model.tam_money -= shop_price[i]
#                        tam_bought = player_model.tam_bought
#                        tam_bought += shop_objects[i] + " "
#                        tam_money = player_model.tam_money
#                        tam_money -= shop_price[i]
#                        models_tamagochi.objects.filter(tam_owner=request.user).update(tam_bought = tam_bought, tam_money = tam_money)
    else:
        return redirect("/login")
    return render(request, "template_gameshop.html", {"username" : request.user, "skins" : skins})

def chat(request):
    return HttpResponse("чат")
def global_chat(request):
    return render(request, "template_global_chat.html", {"username" : request.user,"sessionid": request.session.session_key,})
def tamagochi(request):
    if request.user.is_authenticated:
        request.session.save()  # Ensure session exists
        create = models_tamagochi.objects.filter(tam_owner = request.user).exists()
        if request.method == "POST":
            if not create:
                tamagochi_create = models_tamagochi.objects.create(tam_owner = request.user, tam_income = 50, tam_money= 0, tam_type = "starter", tam_skin = "1", 
                    tam_water = 100, tam_food = 100, tam_sleep = 100, tam_playtime = 100, tam_timeleft = datetime.now())
                tamagochi_create.save()
                return redirect("/")
        else:
            pass
        

        tama_skin = models_tamagochi.objects.filter(tam_owner = request.user).first().tam_skin
        print(tama_skin)

        return render(request, "template.html", {"create" : create,"sessionid": request.session.session_key,"username" : request.user, "skin":tama_skin})
    else:
        return redirect("/login")



paypalrestsdk.configure({
    "mode": "sandbox", # Use "live" for real payments
    "client_id": "YOUR_CLIENT_ID",
    "client_secret": "YOUR_CLIENT_SECRET"
})

def make_payment(request):
    url = "http://127.0.0.1:8000"
    payment = paypalrestsdk.Payment({"intent":"sale", "payer":{"payment_method":"paypal"}, 
        "redirect_urls":{"return_url": url+"/good_paypal", "cancel_url":url+"/bad_paypal"},
        "transactions":[{"amount":{"total":"1.00", "currency":"EUR"}, "description":"you get 500 coins"}]})
    if payment.create():
        for i in payment.links:
            if i.rel == "approval_url":
                return JsonResponse({"approval_url":i.href})
    else:
        return JsonResponse({"error":"payment error"}, status = 400)
def payment_paypal_success(request):
    payment_id = request.GET.get("paymentId")
    payer_id = request.GET.get("PayerID")

    payment = paypalrestsdk.Payment.find(payment_id)

    if payment.execute({"payer_id": payer_id}):
        return JsonResponse({"message": "Payment successful!"})
    else:
        return JsonResponse({"error": payment.error}, status=400)
def payment_crypto_success(request):
    return JsonResponse({"message": "Payment successful!"})
def payment_failure(request):
    return JsonResponse({"message": "Payment failure!"})




def page_logout(request):
    logout(request)
    return redirect("/login")
