from django.db import models
from address.models import AddressField
import subprocess
from django.conf import settings
import os
import jellyfish


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
        img_file_path = os.path.join(settings.MEDIA_ROOT, self.img_file.url)
        img_file_output_path = img_file_path.replace('.png', '-c.png')

        # Pre-process image for OCR
        cmd = 'convert {0} -crop 530x390+20+230 -scale 300% -colorspace gray -morphology erode Octagon:1' \
              ' -black-threshold 60% -white-threshold 75%' \
              ' {1}'.format(img_file_path, img_file_output_path)

        process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()

        # OCR with tesseract
        cmd = 'tesseract ' + img_file_output_path + ' stdout ' + os.path.join(settings.BASE_DIR, 'config/tesseract/azdigitspunc')
        process = subprocess.Popen([cmd], shell=True, stdout=subprocess.PIPE)
        out, err = process.communicate()
        text = out.decode('utf-8').split('\n')
        new_text = []

        print(text)
        # Post process with Levenshtein
        eng_words = [word.strip() for word in open(os.path.join(settings.MEDIA_ROOT, 'english_dict_20k.txt'), 'r')]
        vocab = [word.strip() for word in open(os.path.join(settings.MEDIA_ROOT, 'vocabulary.txt'), 'r')]

        for line in text:
            new_line = []
            for item in line.split():
                tup = (item, None)
                if item in vocab:
                    tup = (item, 0)
                else:
                    for word in vocab:
                        dist = jellyfish.levenshtein_distance(item, word)
                        if tup[1] is None or dist <= tup[1]:
                            tup = (word, dist)

                    if item.lower() not in eng_words and not item.isdigit() and not item.isupper():
                        for word in eng_words:
                            dist = jellyfish.levenshtein_distance(item, word)
                            if tup[1] is None or dist <= tup[1]:
                                tup = (word, dist)
                    else:
                        tup = (item, 0)

                new_line.append(tup[0])

            new_text.append(new_line)

        self.text = '\n'.join([' '.join(line) for line in new_text])
        self.save()


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