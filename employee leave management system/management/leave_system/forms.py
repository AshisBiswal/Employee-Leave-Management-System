from django import forms 
from .models import Profile,Leave,Comment
from django.contrib.auth.models import User


class register_form(forms.Form):
    first_name = forms.CharField(max_length=200)
    last_name = forms.CharField(max_length=200)
    username = forms.CharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(label="email")
    ROLES_CHOICES = (
        ('employee', 'Employee'),
        ('manager', 'Manager'),
    )
    role = forms.ChoiceField(choices=ROLES_CHOICES, label="Role")
   


class login_form(forms.Form):
    username = forms.CharField(max_length=200)
    password = forms.CharField(widget=forms.PasswordInput())


class LeaveForm(forms.ModelForm):
    class Meta:
        model = Leave
        fields = ['start_date', 'end_date', 'reason', 'type', 'manager']


    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
       
        self.fields['manager'].queryset = Profile.objects.filter(role='manager')

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {'text': 'Comment'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
     
        self.fields['text'].widget.attrs.update({'class': 'form-control', 'rows': '3'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['role', 'email']

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name']