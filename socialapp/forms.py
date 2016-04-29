# coding=utf-8


from django import forms
from django.forms import Textarea, TextInput, PasswordInput, ModelForm, EmailField, DateInput, Select, ChoiceField
from django.contrib.auth.models import User
from captcha.fields import CaptchaField, CaptchaTextInput
from socialapp.models import UserFeedback, WallPost, UserPhoto, UserProfile, UniversityDepartment
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext, ugettext_lazy as _


class MyAuthenticationForm(AuthenticationForm):
    username = forms.CharField(label=_("Username"), max_length=30,
                               widget=forms.TextInput(
                                   attrs={'type': 'email', 'placeholder': "@bilgiedu.net veya @bilgi.edu.tr", 'class': 'input-block-level form-control'}))
    password = forms.CharField(label=_("Password"), widget=forms.PasswordInput(
        attrs={'placeholder': _("Password"), 'class': 'input-block-level form-control'}))


class ContactForm(forms.Form):
    subject = forms.CharField()
    email = forms.EmailField(required=False)
    message = forms.CharField()


class UserForm(ModelForm):
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'placeholder': 'Üsteki kodu girin', 'class': 'input-block-level form-control'}))

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'password')
        widgets = {
            'password': PasswordInput(attrs={'placeholder': "Parola", 'class': 'input-block-level form-control'}),
            'email': TextInput(attrs={'placeholder': "@bilgiedu.net veya @bilgi.edu.tr", 'class': 'input-block-level form-control'}),
            'first_name': TextInput(attrs={'placeholder': "Ad", 'class': 'input-block-level form-control'}),
            'last_name': TextInput(attrs={'placeholder': "Soyad", 'class': 'input-block-level form-control'}),
        }


class SearchForm(forms.Form):
    first_name = forms.CharField(label="Ad", widget=TextInput(attrs={'placeholder': "Ad", 'class': 'input-block-level form-control'}))
    last_name = forms.CharField(label="Soyad", widget=TextInput(attrs={'placeholder': "Soyad", 'class': 'input-block-level form-control'}))


class FeedbackForm(ModelForm):
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'placeholder': 'Üsteki kodu girin', 'class': 'input-block-level form-control'}))

    class Meta:
        model = UserFeedback
        fields = ('content',)
        widgets = {
            'content': Textarea(attrs={'placeholder': "Görüşleriniz...", 'class': 'input-block-level form-control'}),
        }


class PasswordResetForm(ModelForm):
    captcha = CaptchaField(widget=CaptchaTextInput(attrs={'placeholder': 'Üsteki kodu girin', 'class': 'input-block-level form-control'}))

    class Meta:
        model = User
        fields = ('email',)
        widgets = {
            'email': TextInput(attrs={'placeholder': "@bilgiedu.net veya @bilgi.edu.tr", 'class': 'input-block-level form-control'})
        }


class NewPasswordForm(forms.Form):
    new_password = forms.CharField(widget=PasswordInput(attrs={'placeholder': "Yeni Parola", 'class': 'input-block-level form-control'}), max_length=128)
    new_password_confirm = forms.CharField(widget=PasswordInput(attrs={'placeholder': "Parolayı Tekrarla", 'class': 'input-block-level form-control'}), max_length=128)


class NewPostForm(ModelForm):

    class Meta:
        model = WallPost
        fields = ('title', 'content')
        widgets = {
            'title': TextInput(attrs={'placeholder': "Başlık", 'class': 'input-block-level form-control'}),
            'content': Textarea(attrs={'placeholder': "İçerik", 'class': 'input-block-level form-control'})
        }


class NewPhotoForm(ModelForm):

    class Meta:
        model = UserPhoto
        fields = ('file_name', 'title')
        widgets = {
            'title': TextInput(attrs={'placeholder': "Açıklama (Opsiyonel)", 'class': 'input-block-level form-control'}),
        }


class EditUserProfileForm(ModelForm):

    class Meta:
        model = UserProfile

        fields = ('birth_date', 'department', 'about')
        widgets = {
            'birth_date': DateInput(attrs={'placeholder': "GG/AA/YYYY", 'class': 'input-block-level form-control'}),
            'about': Textarea(attrs={'placeholder': "Hakkımda", 'class': 'input-block-level form-control'})
        }