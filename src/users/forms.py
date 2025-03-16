from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserRegistrationForm(UserCreationForm):
    """
    Form for register page.
    Accepts password, username, email.
    Return User object
    """
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"class": "form-control"})
        self.fields["password1"].widget.attrs.update({"class": "form-control"})
        self.fields["password2"].widget.attrs.update({"class": "form-control"})

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже зарегистрирован.")
        return email


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={"class": "form-control", "placeholder":
            "Имя пользователя."})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control",
                                          "placeholder": "Пароль"})
    )
