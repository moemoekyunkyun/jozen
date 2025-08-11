from django import forms
from django.contrib.auth.forms import PasswordChangeForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class UserProfileForm(forms.ModelForm):
    """Form for updating user profile information"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full',
                'placeholder': 'Enter your first name (optional)'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full', 
                'placeholder': 'Enter your last name (optional)'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full',
                'placeholder': 'Enter your email address'
            }),
        }
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            # Check if email is already taken by another user
            existing_user = User.objects.filter(email=email).exclude(pk=self.instance.pk).first()
            if existing_user:
                raise ValidationError("This email address is already in use by another account.")
        return email


class CustomPasswordChangeForm(PasswordChangeForm):
    """Enhanced password change form with better styling"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add CSS classes and placeholders
        self.fields['old_password'].widget.attrs.update({
            'class': 'w-full',
            'placeholder': 'Enter your current password'
        })
        self.fields['new_password1'].widget.attrs.update({
            'class': 'w-full',
            'placeholder': 'Enter your new password'
        })
        self.fields['new_password2'].widget.attrs.update({
            'class': 'w-full',
            'placeholder': 'Confirm your new password'
        })
        
        # Update labels
        self.fields['old_password'].label = 'Current Password'
        self.fields['new_password1'].label = 'New Password'
        self.fields['new_password2'].label = 'Confirm New Password'


class AccountDeleteForm(forms.Form):
    """Form for account deletion confirmation"""
    
    confirm_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full',
            'placeholder': 'Type your username to confirm'
        }),
        help_text='Type your username to confirm account deletion'
    )
    
    confirm_deletion = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'mr-2'
        }),
        label='I understand that this action cannot be undone'
    )
    
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
    def clean_confirm_username(self):
        username = self.cleaned_data.get('confirm_username')
        if username != self.user.username:
            raise ValidationError("Username does not match. Please type your exact username.")
        return username


class AccountSettingsForm(forms.Form):
    """Form for account privacy and notification settings"""
    
    # For now, we'll add some basic settings
    # In the future, these could be extended with a UserProfile model
    
    receive_notifications = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
        label='Receive email notifications about your uploads',
        help_text='Get notified when your images are approved or need attention'
    )
    
    public_profile = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'mr-2'}),
        label='Make my profile publicly visible',
        help_text='Allow others to see your username and upload statistics'
    )
    
    # Note: These settings would need to be stored in a UserProfile model
    # or as JSON in User.profile field for full implementation
