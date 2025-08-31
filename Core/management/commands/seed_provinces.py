from django.core.management.base import BaseCommand
from Core.models import Province

AFGHANISTAN_PROVINCES = [
    "Badakhshan", "Badghis", "Baghlan", "Balkh", "Bamyan", "Daykundi",
    "Farah", "Faryab", "Ghazni", "Ghor", "Helmand", "Herat", "Jowzjan",
    "Kabul", "Kandahar", "Kapisa", "Khost", "Kunar", "Kunduz", "Laghman",
    "Logar", "Nangarhar", "Nimruz", "Nuristan", "Paktia", "Paktika",
    "Panjshir", "Parwan", "Samangan", "Sar-e Pol", "Takhar", "Uruzgan",
    "Wardak", "Zabul"
]

class Command(BaseCommand):
    help = "Seed Afghanistan provinces into the Province model"

    def handle(self, *args, **options):
        created = 0
        for name in AFGHANISTAN_PROVINCES:
            obj, was_created = Province.objects.get_or_create(name=name)
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(f"Provinces seeding complete. Created: {created}, Existing: {len(AFGHANISTAN_PROVINCES) - created}"))
