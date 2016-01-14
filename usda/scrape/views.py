from django.views.generic.list import ListView
from scrape import models


class LicenseeCertListView(ListView):

    model = models.LicenseeCert
    queryset = models.LicenseeCert.objects.all().prefetch_related('address')