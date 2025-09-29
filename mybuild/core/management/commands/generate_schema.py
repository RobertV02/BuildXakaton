from django.core.management.base import BaseCommand
from drf_spectacular.generators import SchemaGenerator
from drf_spectacular.renderers import OpenApiYamlRenderer
from drf_spectacular.openapi import AutoSchema as SpectacularAutoSchema

from core import api as core_api

class Command(BaseCommand):
    help = 'Generate OpenAPI schema to schema.yaml'

    def add_arguments(self, parser):
        parser.add_argument('--file', default='schema.yaml')

    def handle(self, *args, **options):
        # Force assign spectacular AutoSchema to avoid mismatch with DRF default
        for prefix, viewset, basename in core_api.router.registry:
            try:
                viewset.schema = SpectacularAutoSchema()
            except Exception:
                pass
        generator = SchemaGenerator()
        schema = generator.get_schema(request=None, public=True)
        content = OpenApiYamlRenderer().render(schema).decode('utf-8')
        target = options['file']
        with open(target, 'w', encoding='utf-8') as f:
            f.write(content)
        self.stdout.write(self.style.SUCCESS(f'Schema written to {target}'))
