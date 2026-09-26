from django import forms
from django.contrib.auth import get_user_model
from apps.accounts.models import UserProfile, CLIMATE_ZONE_CHOICES, GARDEN_TYPE_CHOICES
from apps.blog.models import Comment

User = get_user_model()

class WebLoginForm(forms.Form):
    login = forms.CharField(
        label="Email ou Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': 'votre.email@exemple.com',
            'autocomplete': 'username',
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': '••••••••',
            'autocomplete': 'current-password',
        })
    )

class WebRegisterForm(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur ou Prénom",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': 'Moussa Maraîcher',
        })
    )
    email = forms.EmailField(
        label="Adresse Email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': 'moussa@exemple.com',
        })
    )
    password = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': '•••••••• (8 caractères minimum)',
        })
    )
    password_confirm = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': '••••••••',
        })
    )
    climate_zone = forms.ChoiceField(
        choices=CLIMATE_ZONE_CHOICES,
        label="Zone Agro-climatique",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition bg-white',
        })
    )
    garden_type = forms.ChoiceField(
        choices=GARDEN_TYPE_CHOICES,
        label="Type d'exploitation / Potager",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition bg-white',
        })
    )
    country = forms.CharField(
        label="Pays / Ville",
        required=False,
        initial="Sénégal",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': 'Ex: Dakar, Sénégal / Abidjan, Côte d\'Ivoire',
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà enregistrée.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            self.add_error('password_confirm', "Les deux mots de passe ne correspondent pas.")
        return cleaned_data

class UserProfileUpdateForm(forms.ModelForm):
    username = forms.CharField(
        label="Nom d'utilisateur",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
        })
    )
    phone_number = forms.CharField(
        label="Numéro de téléphone / WhatsApp",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
            'placeholder': '+221 77 000 00 00',
        })
    )
    country = forms.CharField(
        label="Pays / Territoire",
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
        })
    )
    climate_zone = forms.ChoiceField(
        choices=CLIMATE_ZONE_CHOICES,
        label="Zone Agro-climatique",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition bg-white',
        })
    )
    garden_type = forms.ChoiceField(
        choices=GARDEN_TYPE_CHOICES,
        label="Type de potager",
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-2.5 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition bg-white',
        })
    )

    class Meta:
        model = UserProfile
        fields = ['country', 'climate_zone', 'garden_type', 'phone_number']

class BlogCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full p-4 rounded-xl border border-gray-300 focus:ring-2 focus:ring-[#3D7A42] focus:border-transparent outline-none transition',
                'placeholder': 'Partagez votre avis, vos questions ou votre retour d\'expérience maraîchère...',
            })
        }
