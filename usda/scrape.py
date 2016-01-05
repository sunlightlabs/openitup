from selenium import webdriver
import traceback
from selenium.webdriver.support.ui import WebDriverWait
import requests
import json
import csv
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


class USDAInspectionReportScraper():

	def __init__(self, manifest='manifest.json', img_path='inspection_reports/', start_id=2, end_id=10, id_file=None):

		# initiate phantomjs browser and set variables for it
		dcap = dict(DesiredCapabilities.PHANTOMJS)
		dcap["phantomjs.page.settings.userAgent"] = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " + "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36")
		self.driver = webdriver.PhantomJS(desired_capabilities=dcap)
		self.driver.implicitly_wait(10)
		self.wait = WebDriverWait(self.driver, 30)

		# path to store report images and start and end id numbers
		self.img_path = img_path
		if id_file is not None:
			try:
				with open(id_file, 'rU') as id_file_csv:
					reader = csv.DictReader(id_file_csv)
					self.id_list = [row['CUSTIDNUMBER'] for row in reader]
			except:
				print traceback.format_exc()
				print "Unable to parse given CSV from USDA for customer IDs"
				raise ValueError
		else:
			self.id_list = range(start_id, end_id + 1)

		# try to open the manifest json file if it exists and load it into
		# manifest_dict, otherwise initialize empty dictionary
		try:
			json_data = open(manifest,'r')
			self.manifest_dict = json.load(json_data)	
		except:
			self.manifest_dict = {}

		# open file to store the manifest_dict
		self.manifest = open(manifest, 'w')

	def scrape(self):
		try:
			self._prepare_scrape()
			for num in self.id_list:
				try:
					self._scrape_num(num)
				except KeyboardInterrupt:
					# go to outer try/except to clean up before exiting program
					raise KeyboardInterrupt
				except:
					print traceback.format_exc()
					self.manifest_dict[str(num)] = 'Error'
					continue
			self._cleanup()
		except KeyboardInterrupt:
			print "Cleaning up, hold on one second..."
			self._cleanup()
		except:
			print traceback.format_exc()
			self._cleanup()

	def _prepare_scrape(self):
		self.driver.get('https://acissearch.aphis.usda.gov/LPASearch/faces/CustomerSearch.jspx')
		link = self.driver.find_element_by_id('resultview:_id293:_id303:InspInfo')
		link.click()

	def _cleanup(self):
		# write dictionary of what we found to a JSON file
		self.manifest.write(json.dumps(self.manifest_dict, indent=4))
		# exit the phantomjs driver and clean up resources
		self.driver.quit()

	def _retry_errors(self):
		self._prepare_scrape()
		for key in self.manifest_dict:
			if self.manifest_dict[str(key)] == [] or self.manifest_dict[str(key)] == 'Error':
				try:
					self._scrape_num(key)
				except:
					print traceback.format_exc()
					self.manifest_dict[str(key)] = 'Error'
					continue
		self._cleanup()

	def _scrape_num(self, num):
		print "Trying id " + str(num)
		search_elem = self.driver.find_element_by_id('_id33')
		search_elem.clear()
		search_elem.send_keys(str(num))

		search_button = self.driver.find_element_by_xpath('//img[@src="/LPASearch/adf/images/cache/en/bBasicSearchWEIw.gif"]')
		search_button.click()
		eles = self.driver.find_elements_by_xpath("//img[@title='Click this button to show the details of this Inspection Report.']")
		self.manifest_dict[str(num)] = []

		if len(eles) == 0:
			print "No elements present for id " + str(num)
		else:
			self._scrape_eles(num, eles)

	def _scrape_eles(self, num, eles):
		for x in range(0, len(eles)):
			eles[x].click()

			cert_num = self.driver.find_elements_by_xpath("//span[@title='Select to only show information on this USDA Certificate']")[x]
			site_name = self.driver.find_elements_by_xpath("//td[@headers='resultview:_id293:_id394:_id473']")[x]
			date = self.driver.find_elements_by_xpath("//td[@headers='resultview:_id293:_id394:_id475']")[x]
			png = self.driver.find_element_by_xpath('//img[@title="Click to view Inspection Report Explanation"]')
			inventory_table = self.driver.find_elements_by_xpath("//table[@class='x2f']")[1]

			entry_list = []
			entries = inventory_table.find_elements_by_xpath(".//td[@class='x2n x62']")
			for i in range(0, len(entries), 3):
				entry_list.append({
					'Inspection Animal Count': entries[i].text,
					'Animal Common Name': entries[i+1].text,
					'Animal Group Name': entries[i+2].text
				})

			self.manifest_dict[str(num)].append({
				'Customer No.': num,
				'Certificate No.': cert_num.text,
				'Inspection Site Name': site_name.text,
				'Inspection Date': date.text,
				'PNG Report Link': png.get_attribute('src'),
				'Inventory Table': entry_list,
				'PNG File': str(num) + '-' + str(x) + '.png'
			})

			# TODO get remaining fields specified in manifest_TODO.json

			# download png file of report
			c = requests.get(png.get_attribute('src'))
			open(self.img_path + str(num) + '-' + str(x) + '.png', 'w').write(c.content)

			# hide details of current report
			self.driver.find_element_by_xpath('//img[@title="Click this button to hide the details of this Inspection Report."]').click()
			# wait until it's hidden
			self.wait.until(lambda d: len(d.find_elements_by_xpath('//img[@title="Click this button to hide the details of this Inspection Report."]')) == 0)
			# get detail buttons again
			eles = self.driver.find_elements_by_xpath('//img[@title="Click this button to show the details of this Inspection Report."]')

# start here
if __name__ == "__main__":
	usda = USDAInspectionReportScraper(start_id=2, end_id=2)#id_file='usda-certificate-status-active-2016-01-05.csv')
	usda.scrape()
