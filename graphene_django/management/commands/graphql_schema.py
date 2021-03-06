import importlib
import json
from distutils.version import StrictVersion
from optparse import make_option

from django import get_version as get_django_version
from django.core.management.base import BaseCommand, CommandError

from graphene_django.settings import graphene_settings

LT_DJANGO_1_8 = StrictVersion(get_django_version()) < StrictVersion('1.8')

if LT_DJANGO_1_8:
    class CommandArguments(BaseCommand):
        option_list = BaseCommand.option_list + (
            make_option(
                '--schema',
                type=str,
                dest='schema',
                default='',
                help='Django app containing schema to dump, e.g. myproject.core.schema.schema',
            ),
            make_option(
                '--out',
                type=str,
                dest='out',
                default='',
                help='Output file (default: schema.json)'
            ),
        )
else:
    class CommandArguments(BaseCommand):

        def add_arguments(self, parser):
            parser.add_argument(
                '--schema',
                type=str,
                dest='schema',
                default=graphene_settings.SCHEMA,
                help='Django app containing schema to dump, e.g. myproject.core.schema.schema')

            parser.add_argument(
                '--out',
                type=str,
                dest='out',
                default=graphene_settings.SCHEMA_OUTPUT,
                help='Output file (default: schema.json)')


class Command(CommandArguments):
    help = 'Dump Graphene schema JSON to file'
    can_import_settings = True

    def save_file(self, out, schema_dict):
        with open(out, 'w') as outfile:
            json.dump(schema_dict, outfile)

    def handle(self, *args, **options):
        options_schema = options.get('schema')
        if options_schema:
            schema = importlib.import_module(options_schema)
        else:
            schema = graphene_settings.SCHEMA

        out = options.get('out') or graphene_settings.SCHEMA_OUTPUT

        if not schema:
            raise CommandError('Specify schema on GRAPHENE.SCHEMA setting or by using --schema')

        schema_dict = {'data': schema.introspect()}
        self.save_file(out, schema_dict)

        style = getattr(self, 'style', None)
        success = getattr(style, 'SUCCESS', lambda x: x)

        self.stdout.write(success('Successfully dumped GraphQL schema to %s' % out))
