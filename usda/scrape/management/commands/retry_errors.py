from django.core.management.base import BaseCommand
from scrape.models import Scrape
from scrape.scraper import USDAInspectionReportScraper


class Command(BaseCommand):
    help = 'Retries unsuccessful scrapes.'

    def handle(self, **options):
        id_list = Scrape.objects.exclude(error='').values_list('licensee__customer_id', flat=True)
        USDAInspectionReportScraper(id_list).scrape()