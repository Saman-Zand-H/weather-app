from allauth.account.forms import SignupForm
from captcha.fields import CaptchaField

from django import forms


class CustomSignUpForm(SignupForm):
    captcha = CaptchaField()
    picture = forms.ImageField()

    def save(self, request):
        user = super(CustomSignUpForm, self).save(request)
        user.image = self.cleaned_data.get("picture")
        user.save()
        return user