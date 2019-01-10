from django import forms
from .models import User, Trip

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

from django.core.validators import RegexValidator

# A validation for the username, because the default validation accepts all unicode characters.
alphanumeric = RegexValidator(r'^[0-9a-zA-Z_]*$', 'Only English alphabetic characters, underscores and/or numbers are allowed.')

class UserCreateForm(UserCreationForm):

    # Adding the validation to our username field.
    username = forms.CharField(min_length=5, validators=[alphanumeric])

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        '''
        Removing help_text(s) that are being displayed by default
        in the UserCreationForm (for a better look).
        '''

        super().__init__(*args, **kwargs)
        
        self.fields['username'].help_text = None

        self.fields['password1'].help_text = None

        self.fields['password2'].help_text = None


# class TripCreateForm(forms.ModelForm):

#     class Meta:
#         model = Trip
#         fields = ('country', 'town_1', 'town_2', 'fuel_cost', 'fuel_consumption')

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
        
#         self.fields['town_1'].label = "From"
#         self.fields['town_2'].label = "To"