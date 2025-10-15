from django import forms
from django.contrib.postgres.fields import ArrayField

class form_account(forms.Form):
    acc_username = forms.CharField(max_length=15)
    acc_email = forms.EmailField()
    acc_p = forms.CharField(max_length=32)
    acc_password2 = forms.CharField(max_length=32)

class form_messages(forms.Form): 
    message_text = forms.CharField(max_length=141)

class form_login(forms.Form):
     acc_username = forms.CharField(max_length=15)   
     acc_password = forms.CharField(max_length=32)

