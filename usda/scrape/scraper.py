from selenium import webdriver
import traceback
from selenium.webdriver.support.ui import WebDriverWait
import json
from scrape import models
import re
from urllib.request import urlopen
from django.core.files import File
from io import BytesIO
from datetime import datetime
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class USDAInspectionReportScraper():

    def __init__(self, id_list=None):

        # initiate phantomjs browser and set variables for it
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36")
        self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
        self.driver.implicitly_wait(10)
        self.wait = WebDriverWait(self.driver, 30)

        if id_list is None:
            print('Must provide list of IDs')
            raise ValueError
        else:
            self.id_list = id_list

    def scrape(self):
        try:
            self._prepare_scrape()
            for num in self.id_list:
                licensee = models.Licensee.objects.get_or_create(customer_id=int(num))[0]
                scrape = models.Scrape.objects.create(licensee=licensee)
                try:
                    self._scrape_num(licensee, scrape)
                except:
                    print(traceback.format_exc())
                    scrape.update_attrs(error=traceback.format_exc())
                    continue
            self._cleanup()
        except:
            print(traceback.format_exc())
            self._cleanup()

    def _prepare_scrape(self):
        self.driver.get('https://acissearch.aphis.usda.gov/LPASearch/faces/CustomerSearch.jspx')
        link = self.driver.find_element_by_id('resultview:_id293:_id303:InspInfo')
        link.click()

    def _cleanup(self):
        self.driver.quit()

    def _scrape_num(self, licensee, scrape):
        print("Trying id " + str(licensee.customer_id))
        # clear search box and enter new id number
        search_elem = self.driver.find_element_by_id('_id33')
        search_elem.clear()
        search_elem.send_keys(str(licensee.customer_id))
        # find the search button and click it
        search_button = self.driver.find_element_by_xpath('//img[@src="/LPASearch/adf/images/cache/en/bBasicSearchWEIw.gif"]')
        search_button.click()

        if len(self.driver.find_elements_by_xpath("//select[@title='Select record set']")) > 0:
            select_ele = self.driver.find_element_by_xpath("//select[@title='Select record set']/option[@value='all']")
            num_of_entries = int(select_ele.text.replace('Show All ','').strip())
            select_ele.click()
            self.wait.until(lambda d: len(d.find_elements_by_xpath("//img[@title='Click this button to show the details of this Inspection Report.']")) == num_of_entries)

        details_buttons = self.driver.find_elements_by_xpath("//img[@title='Click this button to show the details of this Inspection Report.']")

        if len(details_buttons) == 0:
            print("No elements present for id " + str(licensee.customer_id))
        else:
            self._scrape_eles(licensee, scrape, details_buttons)

    def _scrape_eles(self, licensee, scrape, details_buttons):
        for x in range(0, len(details_buttons)):
            details_buttons[x].click()

            cert_num = self.driver.find_elements_by_xpath("//span[@title='Select to only show information on this USDA Certificate']")[x]
            cert = models.LicenseeCert.objects.get(certificate=cert_num.text, licensee=licensee)

            site_name = self.driver.find_elements_by_xpath("//td[@headers='resultview:_id293:_id394:_id473']")[x]
            date = self.driver.find_elements_by_xpath("//td[@headers='resultview:_id293:_id394:_id475']")[x]
            png = self.driver.find_element_by_xpath('//img[@title="Click to view Inspection Report Explanation"]')

            inspection_number = re.search(r"request_id=\d+", png.get_attribute('src')).group(0).split("=")[1]
            inspection_report = models.InspectionReport.objects.get_or_create(inspector_number=int(inspection_number))[0]

            inspection_report.update_attrs(**{
                'inspection_site_name': site_name.text,
                'inspection_date': datetime.strptime(date.text, '%b %d, %Y'),
                'img_link': png.get_attribute('src'),
                'licensee_cert': cert
            })

            inventory_table = self.driver.find_elements_by_xpath("//table[@class='x2f']")[1]

            entries = inventory_table.find_elements_by_xpath(".//td[@class='x2n x62']")
            for i in range(0, len(entries), 3):
                models.AnimalInventory.objects.get_or_create(inspection_report=inspection_report,
                                                             animal_count=entries[i].text,
                                                             animal_name=entries[i+1].text,
                                                             animal_group_name=entries[i+2].text)
            # download png file of report
            if not inspection_report.img_file:
                response = urlopen(png.get_attribute('src'))
                io = BytesIO(response.read())
                inspection_report.img_file.save("{0}.png".format(inspection_number), File(io))

            total_compliance_span = self.driver.find_elements_by_xpath("//span[@style='font-weight:bold;']")[(x*5)+4]
            if total_compliance_span.text != '' and total_compliance_span.find_element_by_xpath('..').tag_name == 'a':
                total_compliance_span.click()
                self.wait.until(lambda d: len(d.find_elements_by_xpath("//img[@title='Click to hide Non-Compliances Table']")) != 0)

                compliance_table = self.driver.find_elements_by_xpath("//table[@class='x2f']")[2]
                compliance_entries = compliance_table.find_elements_by_xpath(".//td[@class='x2n x62']")

                for i in range(0, len(compliance_entries), 4):

                    compliance_entry = {
                        'inspection_report': inspection_report,
                        'description': compliance_entries[i+1].text,
                        'direct_non_compliance': compliance_entries[i+2].text == 'Yes',
                        'repeat_non_compliance': compliance_entries[i+3].text == 'Yes'
                    }

                    try:
                        compliance_entry['regulation_section'] = compliance_entries[i].find_element_by_xpath('.//span').text,
                    except:
                        try:
                            compliance_entry['regulation_section'] = compliance_entries[i].text
                        except:
                            compliance_entry['regulation_section'] = 'Error 101'

                    try:
                        compliance_entry['cfrs_id'] = compliance_entries[i].find_element_by_xpath('.//a').get_attribute('href').split('=')[1]
                    except:
                        compliance_entry['cfrs_id'] = None

                    models.NonCompliance.objects.get_or_create(**compliance_entry)

                self.driver.find_element_by_xpath("//img[@title='Click to hide Non-Compliances Table']").click()
                self.wait.until(lambda d: len(d.find_elements_by_xpath("//img[@title='Click to hide Non-Compliances Table']")) == 0)

            # hide details of current report
            self.driver.find_element_by_xpath('//img[@title="Click this button to hide the details of this Inspection Report."]').click()
            # wait until it's hidden
            self.wait.until(lambda d: len(d.find_elements_by_xpath('//img[@title="Click this button to hide the details of this Inspection Report."]')) == 0)
            # get detail buttons again
            details_buttons = self.driver.find_elements_by_xpath('//img[@title="Click this button to show the details of this Inspection Report."]')
