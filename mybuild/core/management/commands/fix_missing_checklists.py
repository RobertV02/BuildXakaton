from django.core.management.base import BaseCommand
from objects.models import ConstructionObject, OpeningChecklist, ObjectStatus


class Command(BaseCommand):
    help = 'Create missing opening checklists for ACTIVE objects'

    def handle(self, *args, **options):
        # Find all ACTIVE objects that don't have an opening checklist
        active_objects_without_checklist = ConstructionObject.objects.filter(
            status=ObjectStatus.ACTIVE
        ).exclude(
            opening_checklist__isnull=False
        )

        created_count = 0
        for obj in active_objects_without_checklist:
            OpeningChecklist.objects.create(
                object=obj,
                data={"fields": []},  # Empty checklist data to be filled later
                filled_by=None  # Will be set when checklist is filled
            )
            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Created checklist for object: {obj.name} (ID: {obj.id})')
            )

        if created_count == 0:
            self.stdout.write(
                self.style.WARNING('No missing checklists found for ACTIVE objects')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created {created_count} missing checklists')
            )