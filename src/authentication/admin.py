# from django.contrib import admin
#
# # Register your models here.
# from authentication.models import Users
#
#
# @admin.register(Users)
# class UsersAdmin(admin.ModelAdmin):
#     pass

from django import forms
from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

from authentication.models import Users

# source : https://docs.djangoproject.com/fr/4.0/topics/auth/customizing/


class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = Users
        fields = ('email', 'first_name', 'last_name')

    def clean_password2(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    password = ReadOnlyPasswordHashField()

    class Meta:
        model = Users
        fields = ('email', 'password', 'first_name', 'last_name', 'is_sales',
                  'is_support', 'is_management', 'is_staff', 'is_active', 'is_admin')


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    add_form = UserCreationForm

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('email', 'first_name', 'last_name', 'is_sales',
                    'is_support', 'is_management', 'is_staff', 'is_admin')
    list_editable = ('is_sales', 'is_support', 'is_management', 'is_staff', 'is_admin')

    list_filter = ('email', 'first_name', 'last_name', 'is_sales',
                   'is_support', 'is_management', 'is_staff', 'is_admin')

    # le fieldset cr??e des sous menu :
    # https://docs.djangoproject.com/fr/4.0/intro/tutorial07/
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_sales', 'is_support', 'is_management',
                                    'is_staff', 'is_admin',)}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'password', 'password2'),
        }),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

    def has_view_permission(self, request):
        if request.user.is_admin:
            return True
        if request.user.is_management:
            return True
        return False

    # Si seulement has_view, les users restes visibles car suppos??s
    # modifiables et autres

    def has_add_permission(self, request):
        if request.user.is_admin:
            return True
        if request.user.is_management:
            return True
        return False

    def has_change_permission(self, request):
        if request.user.is_admin:
            return True
        if request.user.is_management:
            return True
        return False

    def has_delete_permission(self, request):
        if request.user.is_admin:
            return True
        if request.user.is_management:
            return True
        return False


# admin.site.register permt de remplacer un mod??le (et ses champs) par un autre
# pour le gestionnaire d'administration au lieu d'utiliser le d??corateur @admin.register(***):
# https://docs.djangoproject.com/fr/4.0/intro/tutorial07/
# Now register the new UserAdmin...
admin.site.register(Users, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# GROUP : Pour ne pas afficher group dans Admin (unregister the Group model from admin) :
admin.site.unregister(Group)

