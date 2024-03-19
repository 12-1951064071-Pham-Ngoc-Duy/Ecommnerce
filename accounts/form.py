from django import forms
from .models import Account, UserProfile


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Enter Password',
        'class' : 'form-control'
    }))
    re_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder': 'Re Password',
        'class' : 'form-control'
    }))
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={
        'class': 'form-control-file'
    }))

    class Meta:
        model = Account
        fields = ['first_name','last_name','phone_number','email','password']

    def clean(self):
        clean_data = super(RegistrationForm, self).clean()
        password = clean_data.get('password')
        re_password = clean_data.get('re_password')

        if password != re_password:
            raise forms.ValidationError(
                'Password does not math!'
            )

    def __init__(self, *args, **kwargs):
        super(RegistrationForm, self).__init__(*args, **kwargs)
        self.fields['first_name'].widget.attrs['placeholder'] = 'First Name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Last Name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Phone Number'
        self.fields['email'].widget.attrs['placeholder'] = 'Email'
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
        
        # Add fields from UserProfile to the form
        self.fields['address_line_1'] = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
            'placeholder': 'Address Line 1',
            'class': 'form-control'
        }))
        self.fields['address_line_2'] = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={
            'placeholder': 'Address Line 2',
            'class': 'form-control'
        }))
        self.fields['city'] = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
            'placeholder': 'City',
            'class': 'form-control'
        }))
        self.fields['state'] = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
            'placeholder': 'State',
            'class': 'form-control'
        }))
        self.fields['country'] = forms.CharField(max_length=20, required=False, widget=forms.TextInput(attrs={
            'placeholder': 'Country',
            'class': 'form-control'
        }))

class UserForm(forms.ModelForm):
    class Meta:
        model = Account
        fields = ('first_name','last_name','phone_number')

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'

class UserProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, error_messages= {'invalid':("Image files only")}, widget=forms.FileInput)
    class Meta:
        model = UserProfile 
        fields = ('address_line_1','address_line_2','city','state','country','profile_picture')

    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs['class'] = 'form-control'
    
    # def clean(self):
    #     clean_data = super(UserProfileForm, self).clean()
    #     address_line_1 = clean_data.get('address_line_1')
    #     address_line_2 = clean_data.get('address_line_2')
    #     state = clean_data.get('address_line_2')
    #     city = clean_data.get('address_line_2')
    #     country = clean_data.get('address_line_2')
    #     profile_picture = clean_data.get('address_line_2')