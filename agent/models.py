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
    role = models.IntegerField(choices=ROLE_CHOICES, default=6, verbose_name=_("Role"))
    title_before = models.CharField(max_length=10, choices=TITLE_BEFORE_CHOICES, blank=True, verbose_name=_("Title Before"))
    title_after = models.CharField(max_length=10, choices=TITLE_AFTER_CHOICES, blank=True, verbose_name=_("Title After"))
    managed_by = models.ForeignKey(
        'UserHierarchyNode',
        on_delete=models.SET_NULL,  # Nastaví na NULL, pokud je smazán UserHierarchyNode
        related_name="persons",
        verbose_name=_("Managed by"),
        null=True,                  # Povolit NULL hodnoty v databázi
        blank=True                  # Povolit prázdné hodnoty ve formulářích
)

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

    position = models.IntegerField(choices=POSITION_CHOICES, default=4)
    companies = models.ManyToManyField('Company', blank=True, related_name="users")
    hierarchy_nodes = models.ManyToManyField(
        'HierarchyNode', blank=True, through='UserHierarchyNode', related_name="users"
    )

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

    def has_access_to_hierarchy_node(self, node):
        """
        Zkontroluje, zda má uživatel přístup k danému hierarchickému uzlu.
        """
        return self.hierarchy_nodes.filter(id=node.id).exists()
    


class UserHierarchyNode(models.Model):
    """
    Prostřední tabulka pro přiřazení uživatelů k hierarchickým uzlům s definovanou rolí.
    """
    ROLE_CHOICES = [
        (1, _('Manager')),
        (2, _('Division Manager')),
        (3, _('Group Leader')),
        (4, _('Employee')),
    ]

    user = models.ForeignKey(AppUser, on_delete=models.CASCADE)
    hierarchy_node = models.ForeignKey('HierarchyNode', on_delete=models.CASCADE)
    role = models.IntegerField(choices=ROLE_CHOICES, default=4)

    class Meta:
        unique_together = ('user', 'hierarchy_node')

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()} of {self.hierarchy_node.name}"

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

class HierarchyNode(models.Model):
    """
    Univerzální model reprezentující uzel v hierarchii.
    """
    PARENT_CHOICES = [
        (1, _('Company')),
        (2, _('Division')),
        (3, _('Group')),
    ]
    parent = models.ForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name="children"
    )
    parent_type = models.IntegerField(choices=PARENT_CHOICES, null=True, blank=True)
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if self.parent_type == 1 and self.parent is not None:
            raise ValidationError(_('Company cannot have a parent.'))

        if self.parent_type in [2, 3] and self.parent is None:
            raise ValidationError(_('Division or Group must have a parent.'))

        if self.parent:
            if self.parent_type == 2 and self.parent.parent_type != 1:
                raise ValidationError(_('Division must have a Company as its parent.'))
            if self.parent_type == 3 and self.parent.parent_type != 2:
                raise ValidationError(_('Group must have a Division as its parent.'))

    def __str__(self):
        hierarchy_path = []
        current = self
        while current:
            hierarchy_path.append(current.name)
            current = current.parent
        return " > ".join(reversed(hierarchy_path))

class Company(models.Model):
    """
    Model reprezentující podnik.
    """
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return self.name


class Division(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='divisions')

    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    division = models.ForeignKey(Division, on_delete=models.CASCADE, related_name='teams')

    def __str__(self):
        return self.name

class Employee(models.Model):
    class Meta: permissions = [ ("view_employee data", "Can view employee data"), 
                                ("edit_employee", "Can edit employee data"), 
                                ("view_team_data", "Can view team data"), 
                                ("edit_team_data", "Can edit team data"), 
                                ("view_division_data", "Can view division data"), 
                                ("edit_division_data", "Can edit division data"), 
                            ]
    
    user = models.OneToOneField(AppUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='members', null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

