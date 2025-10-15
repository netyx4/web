from django.urls import path
from TAMATAMA import views
from django.contrib.staticfiles.urls import staticfiles_urlpatterns


urlpatterns = [path("reg/", views.reg, name = "reg"),
                path("login/", views.login_site, name = "login"),
                path("", views.home, name = "menu"),
                path("user/<str:username>/", views.user, name = "user"),
                path("settings/", views.settings, name = "settings"),
                path("shop/", views.shop, name = "shop"),
                path("gameshop/", views.gameshop, name = "gameshop"),
                path("chat/", views.chat, name = "chat"),
                path("global_chat/", views.global_chat, name = "global_chat"),
                path("tamagochi/", views.tamagochi, name = "tamagochi"),
                path("make_payment/", views.make_payment, name = "make_payment"),
                path("payment_paypal_success/", views.payment_paypal_success, name = "payment_paypal_success"),
                path("payment_crypto_success/", views.payment_crypto_success, name = "payment_crypto_success"),
                path("payment_failure/", views.payment_failure, name = "payment_failure"),
                path("logout/", views.page_logout, name = "logout")
]
urlpatterns += staticfiles_urlpatterns()