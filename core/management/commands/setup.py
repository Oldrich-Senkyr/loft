from django.core.management.base import BaseCommand
from agent.models import AppUser  # Ujistěte se, že používáte správnou cestu k vašemu modelu

class Command(BaseCommand):
    help = 'Inicializuje aplikaci, vytvoří superuživatele a další počáteční data'

    def handle(self, *args, **kwargs):
        # Vytvoření superuživatele
        if not AppUser.objects.filter(username='admin').exists():
            AppUser.objects.create_superuser(
                username='super',
                email='senkyr@dknl.cz',
                password='10super.'
            )
            self.stdout.write(self.style.SUCCESS('Superuživatel "super" byl úspěšně vytvořen.'))

        # Další počáteční nastavení (např. vytvoření skupin nebo výchozích dat)
        # Příklad:
        # from myapp.models import ExampleModel
        # ExampleModel.objects.get_or_create(name='Výchozí data')
        self.stdout.write(self.style.SUCCESS('Inicializace aplikace dokončena.'))
