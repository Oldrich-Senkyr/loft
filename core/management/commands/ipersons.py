import csv
from django.conf import settings
from django.core.management.base import BaseCommand
from agent.models import Person  # Upravte dle cesty k vašemu modelu

class Command(BaseCommand):
    help = 'Inicializuje výchozí hodnoty pro model Person z CSV souboru'

    def handle(self, *args, **kwargs):
        # Cesta k CSV souboru (přizpůsobte dle potřeby)
        csv_file_path = settings.BASE_DIR / 'data' / 'init' / 'persons_v03.csv'

        try:
            with open(csv_file_path, mode='r', encoding='utf-8') as file:
                reader = csv.DictReader(file)

                for row in reader:
                    unique_id = row['unique_id']
                    display_name = row['display_name']
                    first_name = row['first_name']
                    last_name = row['last_name']
                    role = int(row['role'])
                    # title_before = row['title_before']
                    # title_after = row['title_after']

                    # Zkontrolujte, zda záznam již existuje
                    if not Person.objects.filter(unique_id=unique_id).exists():
                        # Vytvoření nové osoby
                        Person.objects.create(
                            unique_id=unique_id,
                            display_name=display_name,
                            first_name=first_name,
                            last_name=last_name,
                            role=role,
                            # title_before=title_before,
                            # title_after=title_after
                        )
                        self.stdout.write(self.style.SUCCESS(f'Person {first_name} {last_name} vytvořen.'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Person s unique_id {unique_id} již existuje, záznam byl přeskočen.'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV soubor {csv_file_path} nebyl nalezen.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Chyba při zpracování souboru: {str(e)}'))
