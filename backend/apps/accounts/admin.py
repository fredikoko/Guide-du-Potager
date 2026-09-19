from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profil Utilisateur & Abonnement'
    fields = ('subscription_active', 'subscription_end_date', 'phone_number', 'avatar', 'preferences', 'history')

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'username', 'first_name', 'last_name', 'is_staff', 'get_subscription_status', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'profile__subscription_active')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-created_at',)

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations Personnelles', {'fields': ('username', 'first_name', 'last_name')}),
        ('Permissions & Statut', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Dates Importantes', {'fields': ('last_login', 'date_joined')}),
    )

    def get_subscription_status(self, obj):
        if hasattr(obj, 'profile') and obj.profile.subscription_active:
            return "★ Membre Premium"
        return "Gratuit"
    get_subscription_status.short_description = "Statut Abonnement"

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'subscription_active', 'subscription_end_date', 'phone_number')
    list_filter = ('subscription_active',)
    search_fields = ('user__email', 'user__username', 'phone_number')
