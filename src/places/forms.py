# coding: utf-8

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True,label="אי-מייל")
    first_name = forms.CharField(required=True, label="שם פרטי")
    last_name = forms.CharField(required=True, label="שם משפחה")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2", "first_name", "last_name")

    def save(self, commit=True):
        user = super(UserCreateForm, self).save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user

class UploadFileForm(forms.Form):
    title = forms.CharField(max_length=50)
    file = forms.FileField()
    file_type = forms.ChoiceField(choices=(('csv', 'csv'), ('json', 'json')), required=True, widget=forms.RadioSelect)
    
    def is_valid(self):
        # run the parent validation first
        
        valid = super(UploadFileForm, self).is_valid()
        
        if not valid:
            return False
        
        if not self.cleaned_data['file'].name.endswith(self.cleaned_data['file_type']):
            self._errors['bad_file'] = "File does not match the chosen format"
            #messages.error(request, "סיומת הקובץ לא תואמת לסוג הקובץ שנבחר")
            return False
        
        return True
    