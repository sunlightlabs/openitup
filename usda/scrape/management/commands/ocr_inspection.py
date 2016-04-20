from django.core.management.base import BaseCommand, CommandError
from scrape.models import InspectionReport


class Command(BaseCommand):
    help = 'OCR an inspection report by number or all at once.'

    def add_arguments(self, parser):
        parser.add_argument('--number', type=str, dest='number', default=False)

    def handle(self, **options):
        if options.get('number'):
            InspectionReport.objects.filter(inspector_number=int(options.get('number'))).first().ocr_pdf_to_text()
        else:
            for report in InspectionReport.objects.all():
                report.ocr_pdf_to_text()