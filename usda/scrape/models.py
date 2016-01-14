from django.db import models
from address.models import AddressField


class Entity(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def update_attrs(self, **attrs):
        try:
            for key in attrs:
                setattr(self, key, attrs[key])
            self.save()
        except AttributeError:
            pass
        except:
            pass


class Licensee(Entity):

    customer_id = models.BigIntegerField()

    @property
    def first_cert(self):
        return self.cert.first()


class LicenseeCert(Entity):

    licensee = models.ForeignKey(Licensee, related_name='certs', null=True)
    cert_id = models.BigIntegerField()
    certificate = models.CharField(max_length=9)
    certificate_status = models.NullBooleanField()
    status_date = models.DateTimeField(null=True)
    legal_name = models.CharField(max_length=1024)
    dba = models.CharField(max_length=1024)
    address = AddressField(null=True)


class Scrape(Entity):

    licensee = models.ForeignKey(Licensee, null=True)
    error = models.TextField()


class InspectionReport(Entity):

    licensee_cert = models.ForeignKey(LicenseeCert, null=True)
    inspection_site_name = models.CharField(max_length=1024)
    inspection_date = models.DateField(null=True)
    inspection_type = models.CharField(max_length=256)
    prepared_by = models.CharField(max_length=2048)
    prepared_by_title = models.CharField(max_length=512)
    inspector_number = models.BigIntegerField(null=True)
    text = models.TextField()
    img_link = models.URLField(max_length=1024)
    img_file = models.ImageField(upload_to='inspection_reports/')

    def ocr_pdf_to_text(self):
        raise NotImplementedError


class AnimalInventory(Entity):

    inspection_report = models.ForeignKey(InspectionReport, null=True)

    animal_count = models.IntegerField(null=True)
    animal_name = models.CharField(max_length=1024)
    animal_group_name = models.CharField(max_length=2048)


class NonCompliance(Entity):

    inspection_report = models.ForeignKey(InspectionReport, null=True)

    cfrs_id = models.BigIntegerField(null=True)
    regulation_section = models.CharField(max_length=128)
    description = models.CharField(max_length=2048)
    direct_non_compliance = models.NullBooleanField()
    repeat_non_compliance = models.NullBooleanField()