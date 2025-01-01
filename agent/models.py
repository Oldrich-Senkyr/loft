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

    
    unique_id = models.CharField(max_length=20, unique=True, verbose_name=_("Unique ID"), help_text=_("Enter a unique identifier."))
    display_name = models.CharField(max_length=25, default="Alias", verbose_name=_("Alias"))
    first_name = models.CharField(max_length=25, default="Nomen", verbose_name=_("First Name"))
    last_name = models.CharField(max_length=25, default="Omen", verbose_name=_("Last Name"))
    role = models.IntegerField(choices=ROLE_CHOICES, default=6, verbose_name=_("Role"))
    title_before = models.CharField(max_length=10, choices=TITLE_BEFORE_CHOICES, blank=True, verbose_name=_("Title Before"))
    title_after = models.CharField(max_length=10, choices=TITLE_AFTER_CHOICES, blank=True, verbose_name=_("Title After"))
 
    
    def __str__(self):
        return f"{self.unique_id} {self.last_name} {self.first_name} ({self.get_role_display()})"


"""
Table Person {
  id integer [pk, increment, note: "ID osoby"]
  unique_id varchar(10) [unique, not null, note: "Něco jako číslování a odlišení zaměstnanců např ET10, EV10"]
  display_name varchar(25) [default: "Alias", note: "Přezdívka"]
  first_name varchar(25) [not null, default: "Nomen", note: "Křestní jméno"]
  last_name varchar(25) [not null, default: "Omen", note: "Příjmení"]
  role integer [not null, default: 1, note: "Role osoby (1 = Employee, 2 = Guest, 3 = Contractor, 4 = Supplier, 5 = Customer, 6 = Other)"]
  title_before varchar(10) [default: "", note: "Titul před jménem (např. Dr., Ing.)"]
  title_after varchar(10) [default: "", note: "Titul za jménem (např. Ph.D., MBA)"]
  hierarchy_node_id integer [ref: > HierarchyNode.id, not null, note: "Odkaz na hierarchický uzel, ke kterému osoba patří"]
}
"""





from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


from django.db import models
from django.contrib.auth.models import User



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





from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class AppUser(AbstractUser):
    """
    Rozšířený model uživatele s podporou hierarchických uzlů.
    """
    POSITION_CHOICES = [
        (1, _('Manager')),
        (2, _('Division Manager')),
        (3, _('Group Leader')),
        (4, _('Employee')),
    ]

    first_name = models.CharField(max_length=50, verbose_name=_("First Name"))
    last_name = models.CharField(max_length=50, verbose_name=_("Last Name"))
    email = models.EmailField(unique=True, verbose_name=_("Email Address"))

    position = models.IntegerField(choices=POSITION_CHOICES, default=4)
    companies = models.ManyToManyField('Company', blank=True, related_name="users")

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.username})"

    # Metody pro hierarchii přístupů
    def is_manager(self):
        return self.position == 1

    def is_division_manager(self):
        return self.position == 2

    def is_group_leader(self):
        return self.position == 3

    def is_employee(self):
        return self.position == 4





class Company(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    leader = models.ForeignKey('Person', null=True, blank=True, on_delete=models.SET_NULL, related_name='led_companies', verbose_name=_("Leader"))

    def __str__(self):
        return self.name

class Division(models.Model):
    name = models.CharField(max_length=255)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='divisions')
    leader = models.ForeignKey('Person', null=True, blank=True, on_delete=models.SET_NULL, related_name='led_divisions')

    def __str__(self):
        return self.name
    

class Team(models.Model):
    name = models.CharField(max_length=255)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams')
    leader = models.ForeignKey('Person', null=True, blank=True, on_delete=models.SET_NULL, related_name='led_teams')

    def __str__(self):
        return self.name



