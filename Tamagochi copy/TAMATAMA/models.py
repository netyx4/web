from django.db import models
from django.contrib.postgres.fields import ArrayField



#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from django.conf import settings
# Create your models here.

class CustomUser(AbstractUser):
    #acc_username = models.CharField(max_length=15)
    #acc_email = models.EmailField()
    #acc_password = models.CharField(max_length=100)
    #acc_date = models.DateField()
    acc_friends = models.CharField(max_length=15)
    bg_color = models.CharField(max_length=15)


class models_tamagochi(models.Model):
    tam_owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    tam_income = models.IntegerField()
    tam_type = models.CharField(max_length=15)
    tam_skin = models.CharField(max_length=15)
    tam_bought = models.CharField(max_length=99)
    tam_water = models.IntegerField()
    tam_food = models.IntegerField()
    tam_sleep = models.IntegerField()
    tam_playtime = models.IntegerField() 
    tam_timeleft = models.DateTimeField()
    tam_money = models.IntegerField()

class models_shop(models.Model):
    item_price = models.IntegerField()
    item_pic = models.CharField(max_length=15)

class models_friend_invites(models.Model):
    player1 = models.CharField(max_length=15)
    player2 = models.CharField(max_length=15)
    is_accepted = models.BooleanField(default=False)
    class Meta:
        unique_together = ('player1', 'player2')

class models_messages(models.Model):
    player1 = models.CharField(max_length=15)
    player2 = models.CharField(max_length=15)
    message_text = models.CharField(max_length=141)
    message_date = models.DateField()

class models_global_chat(models.Model):
    player = models.CharField(max_length=15)
    message_text = models.CharField(max_length=141)
    message_date = models.DateField()



