from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser, BaseUserManager

class Person(models.Model):
    class Meta:
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")

    TITLE_BEFORE_CHOICES = [
        ('Bc.', _('Bc.')),
        ('BcA.', _('BcA.')),
        ('RNDr.', _('RNDr.')),
        ('MUDr.', _('MUDr.')),
        ('JUDr.', _('JUDr.')),
        ('PhDr.', _('PhDr.')),
        ('Ing.', _('Ing.')),
        ('Mgr.', _('Mgr.')),
    ]

    TITLE_AFTER_CHOICES = [
        ('DiS.', _('DiS.')),
        ('MBA', _('MBA')),
        ('LL.M.', _('LL.M.')),
        ('CSc.', _('CSc.')),
        ('DrSc.', _('DrSc.')),
        ('Ph.D.', _('Ph.D.')),
    ]

    ROLE_CHOICES = [
        (1, _('Employee')),
        (2, _('Guest')),
        (3, _('Contractor')),
        (4, _('Supplier')),
        (5, _('Customer')),
        (6, _('Other')),
    ]

    unique_id = models.CharField(max_length=20, unique=True, editable=False)
    display_name = models.CharField(max_length=25, default="Alias", verbose_name=_("Alias"))
    first_name = models.CharField(max_length=25, default="Nomen", verbose_name=_("First Name"))
    last_name = models.CharField(max_length=25, default="Omen", verbose_name=_("Last Name"))
    company = models.ForeignKey(
        'Company', 
        on_delete=models.CASCADE, 
        related_name="persons", 
        verbose_name=_("Company")
    )
    role = models.IntegerField(choices=ROLE_CHOICES, default=6, verbose_name=_("Role"))
    title_before = models.CharField(max_length=10, choices=TITLE_BEFORE_CHOICES, blank=True, verbose_name=_("Title Before"))
    title_after = models.CharField(max_length=10, choices=TITLE_AFTER_CHOICES, blank=True, verbose_name=_("Title After"))
    managed_by = models.ForeignKey('AppUser', on_delete=models.CASCADE, related_name="persons", verbose_name=_("Managed by"))

    def generate_unique_id(self):
        return f"{self.role}{self.pk}"

    def save(self, *args, **kwargs):
        if not self.unique_id:
            super().save(*args, **kwargs)  # Save to generate PK
            self.unique_id = self.generate_unique_id()
            super().save(update_fields=['unique_id'])
        else:
            super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_role_display()})"

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _

class Company(models.Model):
    """
    Model reprezentující podnik.
    """
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Division(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class AppUserManager(BaseUserManager):
    """
    Správce uživatelů pro model AppUser.
    """
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError(_('User must have a username'))
        email = self.normalize_email(email)
        extra_fields.setdefault('is_active', True)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('position', 1)  # Superuser má pozici "Manager"

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True'))

        return self.create_user(username, email, password, **extra_fields)


class AppUser(AbstractUser):
    """
    Rozšířený model uživatele s podporou více podniků.
    """
    POSITION_CHOICES = [
        (1, _('Manager')),
        (2, _('Division Manager')),
        (3, _('Group Leader')),
        (4, _('Employee')),
    ]

    position = models.IntegerField(choices=POSITION_CHOICES, default=4)
    companies = models.ManyToManyField(Company, blank=True, related_name="users")
    divisions = models.ManyToManyField('Division', blank=True)

    objects = AppUserManager()  # Použijeme vlastního správce

    def __str__(self):
        return self.username

    # Metody pro hierarchii přístupů
    def is_manager(self):
        return self.position == 1

    def is_division_manager(self):
        return self.position == 2

    def is_group_leader(self):
        return self.position == 3

    def is_employee(self):
        return self.position == 4

    # Metoda pro kontrolu přístupu k podniku
    def has_access_to_company(self, company):
        """
        Zkontroluje, zda má uživatel přístup k danému podniku.
        """
        return self.companies.filter(id=company.id).exists()

    def has_access_to_division(self, division):
        """
        Zkontroluje, zda má uživatel přístup k dané divizi.
        """
        return self.divisions.filter(id=division.id).exists()
