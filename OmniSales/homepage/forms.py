from django import forms
from django.contrib.auth.models import User

class UpdatePasswordForm(forms.Form):
    username = forms.CharField(max_length=150)
    new_password = forms.CharField(widget=forms.PasswordInput)
    confirm_new_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password != confirm_new_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        username = self.cleaned_data['username']
        new_password = self.cleaned_data['new_password']

        try:
            user = User.objects.get(username=username)
            user.set_password(new_password)
            if commit:
                user.save()
        except User.DoesNotExist:
            raise forms.ValidationError("Invalid username.")

        return user