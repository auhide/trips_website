from django import forms
from .models import User, Trip

from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


class UserCreateForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
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