from django.core.management.base import BaseCommand, CommandError
from scrape.models import Scrape
import csv
import traceback
from datetime import datetime


class Command(BaseCommand):
    help = 'Launches data import scripts'

    def handle(self, **options):
        id_list = Scrape.objects.exclude(error='')
        """
            values_list('licensee',flat=True).distinct()





        if options.get('ids'):
            id_list = options['ids'][0]
        elif options.get('file'):
            try:
                with open(options['file'], 'rU') as id_file_csv:
                    reader = csv.DictReader(id_file_csv)
                    id_list = []
                    for row in reader:

                        dt_format = '%Y-%m-%d' if len(row['CERTSTATUSDATE']) == 10 else '%Y-%m-%d %H:%M:%S.0'
                        address = {
                            'raw': row['STREETADDRESS'].replace('<br>', '').strip(),
                            'locality': row['CITYADDRESS'],
                            'state_code': row['STATEADDRESS'],
                            'postal_code': row['ZIPCODEADDRESS'],
                            'country': 'United States',
                            'country_code': 'US'
                        }
                        address['raw'] = "{0}, {1}, {2} {3}".format(address['raw'],
                                                                    address['locality'],
                                                                    address['state_code'],
                                                                    address['postal_code'])

                        licensee = Licensee.objects.get_or_create(customer_id=int(row['CUSTIDNUMBER']))[0]

                        cert = LicenseeCert.objects.get_or_create(cert_id=int(row['CERT_ID_NUMBER']))[0]
                        cert.update_attrs(**{
                            'licensee': licensee,
                            'certificate': row['CERT'],
                            'certificate_status': row['CERTSTATUS']=='ACTIVE',
                            'status_date': datetime.strptime(row['CERTSTATUSDATE'], dt_format),
                            'legal_name': row['LEGALNAME'],
                            'dba': row['DBA'],
                            'address': address
                        })

                        id_list.append(int(row['CUSTIDNUMBER']))
            except:
                print(traceback.format_exc())
                print("Unable to parse given CSV from USDA")
                raise ValueError
        else:
            print("Must specify a list of ids or a file to obtain IDs from")
            raise ValueError

        USDAInspectionReportScraper(id_list).scrape()
        """

