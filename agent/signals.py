from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import PersonTeam, Team
from django.db import transaction




# Signál pro aktualizaci počtu členů při přidání člena
@receiver(post_save, sender=PersonTeam)
def update_team_member_count(sender, instance, created, **kwargs):
    team = instance.team
    with transaction.atomic():  # Lock the team row to prevent concurrent updates
        print("post_save signál aktivován")  # Debugging print statement
        team = Team.objects.select_for_update().get(pk=team.pk)
        print(f"Updated member count for team {team.id}")  # Debugging print statement
        team.count = PersonTeam.objects.filter(team=team, person__isnull=False).count()  # Počítáme jen záznamy, kde person není null
        team.save()

# Signál pro aktualizaci počtu členů při odstranění člena
@receiver(post_delete, sender=PersonTeam)
def update_team_member_count_on_delete(sender, instance, **kwargs):
    print("post_delete signál aktivován")  # Debugging print statement
    team = instance.team
    print(f"Updated member count for team {team.id}")  # Debugging print statement
    team.count = PersonTeam.objects.filter(team=team, person__isnull=False).count()  # Počítáme jen záznamy, kde person není null
    team.save()

#@receiver(post_delete, sender=PersonTeam)
#def delete_null_person_entries(sender, instance, **kwargs):
    # Pokud je person_id null, záznam bude smazán
#    if instance.person is None:
#        instance.delete()