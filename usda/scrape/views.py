from django.views.generic.list import ListView
from scrape import models


class LicenseeCertListView(ListView):

    model = models.LicenseeCert
    queryset = models.LicenseeCert.objects.all().prefetch_related('address')
    paginate_by = 20


class InspectionReportListView(ListView):

    model = models.InspectionReport
    queryset = models.InspectionReport.objects.all()
    paginate_by = 20
