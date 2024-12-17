from django.db import models
from django.utils.translation import gettext_lazy as _ 

# Create your models here.

from django.db import models
from django.utils.translation import gettext_lazy as _


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
        ('Mgr..', _('Mgr.')),
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
    organization = models.CharField(max_length=100, verbose_name=_("Organization"))
    role = models.IntegerField(choices=ROLE_CHOICES, default=6, verbose_name=_("Role"))
    title_before = models.CharField(max_length=10, choices=TITLE_BEFORE_CHOICES, blank=True, verbose_name=_("Title Before"))
    title_after = models.CharField(max_length=10, choices=TITLE_AFTER_CHOICES, blank=True, verbose_name=_("Title After"))

    def generate_unique_id(self):
        # Použijeme číslo role pro generaci unikátního ID
        return f"{self.role}{self.pk}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save to generate PK
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
            super().save(update_fields=['unique_id'])

    def __str__(self):
        return f"{self.last_name} {self.first_name} ({self.get_role_display()})"
    
    
from django.contrib.auth.models import AbstractUser
from django.db import models


class Division(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('manager', _('Manager')),  # Lazy preklad názvu role
        ('division_manager', _('Division Manager')),  # Lazy preklad názvu role
        ('employee', _('Employee')),  # Lazy preklad názvu role
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='employee')
    divisions = models.ManyToManyField(Division, blank=True)  # Division Manager muže mít více divizí

    def is_manager(self):
        return self.role == 'manager'

    def is_division_manager(self):
        return self.role == 'division_manager'    
    
    from django.contrib.auth.models import BaseUserManager

    class CustomUserManager(BaseUserManager):
        def create_user(self, username, email=None, password=None, **extra_fields):
            if not username:
                raise ValueError(_('Uživatel musí mít uživatelské jméno'))
            email = self.normalize_email(email)
            extra_fields.setdefault('is_active', True)
            user = self.model(username=username, email=email, **extra_fields)
            user.set_password(password)
            user.save(using=self._db)
            return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'manager')  # Superuživatel je vždy manažer

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuživatel musí mít is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuživatel musí mít is_superuser=True.'))

        return self.create_user(username, email, password, **extra_fields)
