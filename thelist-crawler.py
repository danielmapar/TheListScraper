#!/usr/bin/python3
import time
import datetime
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from tkinter import *
from tkinter import messagebox
import tkinter
from PIL import Image, ImageTk

import threading
import subprocess

class File:

	name = None
	header = None

	def __init__(self):
		self.header    = "Company,Headquarters,Media Spend,Main Telephone,Main Fax,Primary Address,Employee First Name,Employee Last Name,Employee Title,Direct Dial,Email,Associated Brands\n"
		self.log_name  = "log.csv"
		self.log_directory = "~/Desktop/Rollback_log/"
		self.data_directory = "~/Desktop/Scraps/"

	def delete_log_file(self):
		try:
			os.remove(os.path.expanduser(self.log_directory) + self.log_name)
		except:
			pass

	def check_log_file(self, industry, sub_industry, company_filter, companies):

		try:

			if not os.path.exists(os.path.expanduser(self.log_directory)):
				os.makedirs(os.path.expanduser(self.log_directory))

			log_file = open(os.path.expanduser(self.log_directory) + self.log_name, 'r')
			log_entry = log_file.read().split(';')

			if company_filter and\
			log_entry[0] == 'Company' and\
			log_entry[1] in companies:

				return companies[companies.index(log_entry[1]):]

			elif not company_filter    and\
			log_entry[0] == 'Industry' and\
			log_entry[1] == industry   and\
			log_entry[2] == sub_industry:

				return companies[companies.index(log_entry[3]):]

			else:
				return companies

		except:
			return companies

	def generate_log_file(self, industry, sub_industry, company_name):

		if not os.path.exists(os.path.expanduser(self.log_directory)):
			os.makedirs(os.path.expanduser(self.log_directory))

		log_file = open(os.path.expanduser(self.log_directory) + self.log_name, 'w')
		if industry and sub_industry and company_name:
			log_file.write("Industry;" + industry + ";" + sub_industry + ";" + company_name)
		else:
			log_file.write("Company;" + company_name)

	def generate_report_file(self, output_data_referral, output_data_special, output_data_normal, log_text, file_name=None):
		if file_name is not None:
			FORMAT = '%Y%m%d%H%M%S'
			self.name_referral = file_name + '-' + datetime.datetime.now().strftime(FORMAT) + '-Referral.csv'
			self.name_special = file_name + '-' + datetime.datetime.now().strftime(FORMAT) + '-Special.csv'
			self.name_normal = file_name + '-' + datetime.datetime.now().strftime(FORMAT) + '-Normal.csv'

		if not os.path.exists(os.path.expanduser(self.data_directory)):
			os.makedirs(os.path.expanduser(self.data_directory))

		output_file_referral = open(os.path.expanduser(self.data_directory) + self.name_referral, 'w')
		output_file_special = open(os.path.expanduser(self.data_directory) + self.name_special, 'w')
		output_file_normal = open(os.path.expanduser(self.data_directory) + self.name_normal, 'w')

		output_file_referral.write(self.header)
		output_file_special.write(self.header)
		output_file_normal.write(self.header)

		for line in output_data_referral:
			output_file_referral.write(line)

		for line in output_data_special:
			output_file_special.write(line)

		for line in output_data_normal:
			output_file_normal.write(line)

		output_file_referral.close()
		output_file_special.close()
		output_file_normal.close()

		if len(output_data_referral) > 0:
			log_text.insert(END, "File -> " + self.name_referral + " created successfully!\n")
			log_text.yview(END)

		if len(output_data_special) > 0:
			log_text.insert(END, "File -> " + self.name_special + " created successfully!\n")
			log_text.yview(END)

		if len(output_data_normal) > 0:
			log_text.insert(END, "File -> " + self.name_normal + " created successfully!\n")
			log_text.yview(END)

class TheListExtractor:

	driver = None
	username = ""
	password = ""

	def __init__(self):

		self.driver = webdriver.Firefox()

		self.driver.implicitly_wait(15)
		self.driver.get('https://launch.thelistonline.com/login')

		# Fill up login information
		emailCred=self.driver.find_element_by_id('username')
		emailCred.send_keys(self.username)
		pwd=self.driver.find_element_by_id('password')
		pwd.send_keys(self.password)

		# Click on the login button
		self.driver.find_element_by_id('login-submit').click()

		# Check for product selection
		try:
			the_list_link = self.driver.find_element_by_id('the-list-link-container').find_element_by_tag_name('a').click()
		except:
			pass

		try:
			# Check if login was successful
			self.driver.find_element_by_id('nav-dashboard')
		except:
			self.driver.close()
			self.driver = None
			self.__init__()

	def store_industry_params(self, industry, sub_industry):
		self.industry     = industry
		self.sub_industry = sub_industry

	def get_industry_list(self):

		industries = []

		# Go back to Dashboard
		self.driver.find_element_by_id('nav-dashboard').click()

		# Click on Advanced Search
		self.driver.find_element_by_id('db_advance_search').click()

		# Wait 5 seconds for Advanced Search
		time.sleep(5)

		# Check the Companies radio button
		self.driver.find_element_by_id('focus_corporate').click()

		# Get industry list
		industries_tree = self.driver.find_element_by_id('industry-tree').find_elements_by_class_name('expandable')

		for industry in industries_tree:
			industry_name = industry.find_element_by_tag_name('a').find_element_by_class_name('hit').text

			industry.find_element_by_class_name('hitarea').click()
			time.sleep(1)

			sub_industries_tree = industry.find_element_by_tag_name('ul').find_elements_by_tag_name('li')
			sub_industries = []
			for sub_industry in sub_industries_tree:
				sub_industries.append(sub_industry.find_element_by_tag_name('a').find_element_by_class_name('hit').text)

			industries.append({'name': industry_name, 'list': sub_industries})

		return industries

	def get_companies_inside_industry(self, selected_industry, selected_sub_industry, log):

		companies = []

		# Go back to Dashboard
		self.driver.find_element_by_id('nav-dashboard').click()

		# Click on Advanced Search
		self.driver.find_element_by_id('db_advance_search').click()

		# Wait 5 seconds for Advanced Search
		time.sleep(5)

		# Check the Companies radio button
		self.driver.find_element_by_id('focus_corporate').click()

		# Get industry list
		industries_tree = self.driver.find_element_by_id('industry-tree').find_elements_by_class_name('expandable')

		for industry in industries_tree:
			industry_name = industry.find_element_by_tag_name('a').find_element_by_class_name('hit').text

			industry.find_element_by_class_name('hitarea').click()
			time.sleep(1)

			sub_industries_tree = industry.find_element_by_tag_name('ul').find_elements_by_tag_name('li')

			values_selected = False
			for sub_industry in sub_industries_tree:
				if selected_industry == industry_name and (selected_sub_industry == 'All' or selected_sub_industry == sub_industry.find_element_by_tag_name('a').find_element_by_class_name('hit').text):
					sub_industry.find_element_by_tag_name('a').click()
					values_selected = True

			if values_selected == True:
				break

		# Wait selections to be added to query
		time.sleep(3)

		# Click Perform Search
		self.driver.find_element_by_id('searchbtn').click()

		# Wait for list to load
		time.sleep(5)

		# Change loading options to get all possible results
		self.driver.execute_script("var select = document.getElementById('results_per_page');var opt = document.createElement('option');opt.value = 999999999;opt.innerHTML = 999999999;select.appendChild(opt);")

		# Wait for javascript to execute
		time.sleep(2)

		# Click on new filter option
		filter_options = self.driver.find_element_by_id('results_per_page').find_elements_by_tag_name('option')
		filter_options[len(filter_options)-1].click()

		# Wait for the list to reload
		time.sleep(15)

		companies_list = self.driver.find_element_by_id('results_table__container').find_element_by_tag_name('table').find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')

		for company in companies_list:
			company_name = company.find_element_by_class_name('info').find_element_by_tag_name('a').text
			companies.append(company_name)

			# Show company in the Log
			log.insert(END, company_name+"\n")
			log.yview(END)

		log.insert(END, "-----------------------\n")
		log.yview(END)

		return companies


	def get_company_type_ahead(self, companies_list, log):

		companies = []

		for company_name in companies_list:

			# Go back to Dashboard
			self.driver.find_element_by_id('nav-dashboard').click()

			# Check Corporate / Brand radio button
			self.driver.find_element_by_id('qsfocus_corporate').click()

			# Fill up login information
			searchBox = self.driver.find_element_by_id('keyword')
			company_name = company_name.replace('&', Keys.SHIFT + Keys.NUMPAD7 + Keys.SHIFT)
			company_name = company_name.replace('(', Keys.SHIFT + Keys.NUMPAD9 + Keys.SHIFT)
			searchBox.send_keys(company_name)

			# Wait 5 seconds for type ahead
			time.sleep(5)

			try:
				type_ahead_results = self.driver.find_element_by_class_name('ac_results').find_element_by_tag_name('ul').find_elements_by_tag_name('li')

				for company_name_type_ahead in type_ahead_results:
					if '(Company)' in company_name_type_ahead.text:
						company_name_type_ahead_clean = self.remove_category_from_company_name(company_name_type_ahead.text)
						companies.append(company_name_type_ahead_clean)
						# Show company in the Log
						log.insert(END, company_name_type_ahead_clean+"\n")
						log.yview(END)
			except:
				companies.append(company_name)
				# Show company in the Log
				log.insert(END, company_name+"\n")
				log.yview(END)

		log.insert(END, "-----------------------\n")
		log.yview(END)

		return companies


	def remove_category_from_company_name(self, company_name):
		company_name_clean = ""

		for character in company_name:
			if (character != '('):
				company_name_clean += character
			else:
				break

		return company_name_clean.strip()


	def has_keywords(self, keywords, title_keyphase):
		has_keyword = False
		for keyword in keywords:
			if ' ' in keyword:
				if keyword in title_keyphase:
					has_keyword = True
				else:
					has_keyword = False
			else:
				for title_word in title_keyphase.split(' '):
					if title_word == keyword:
						has_keyword = True
						break
					else:
						has_keyword = False

				if has_keyword == True:
					break

		return has_keyword

	def find_companies_data(self, companies, keywords, referral_keywords, special_keywords, log, user_validation):

		output_data_referral = []
		output_data_special = []
		output_data_normal = []

		companies_size = len(companies)
		counter = 1
		k = 0

		self.execution_exception = False

		while k >= 0 and k < companies_size:

			try:
				if user_validation == True:
					question = messagebox.askyesno(message='Are you sure you want to\
	 keep scraping?\nNext company is: ' + companies[k], \
					icon='question', title='Question')

					if question == False:
						raise Exception('User wants to stop scraping')

				company_name = companies[k];
				log.insert(END, "Company: " + company_name + ", number: " + str(counter) + " of " + str(companies_size) +"\n")
				log.yview(END)

				# Go back to Dashboard
				self.driver.find_element_by_id('nav-dashboard').click()

				# Check Corporate / Brand radio button
				self.driver.find_element_by_id('qsfocus_corporate').click()

				# Fill up login information
				searchBox = self.driver.find_element_by_id('keyword')
				searchBox.send_keys(company_name.replace('&', Keys.SHIFT + Keys.NUMPAD7 + Keys.SHIFT))

				self.driver.find_element_by_id('go').click()

				# Click on the table first row
				self.driver.find_element_by_id('results_table__container').find_element_by_tag_name('table').find_element_by_tag_name('tbody').find_element_by_tag_name('tr').find_element_by_class_name('info').find_element_by_tag_name('a').click()

				# Wait List to load
				time.sleep(8)

				contact_lists_size = None

				# Check if company is Brand
				is_brand = False
				try:
					if 'Brand Profile' in self.driver.find_element_by_class_name('profile-header').text:
						is_brand = True
						self.driver.find_element_by_class_name('profile-display').find_element_by_tag_name('dd').find_element_by_tag_name('a').click()
				except:
					if is_brand == True:
						raise('Not a valid Company')

				# Get Correct List of Contacts
				while contact_lists_size == None:
					try:
						contact_lists_size = len(self.driver.find_element_by_id('location_area').find_elements_by_class_name('icn-pad'))
					except:
						pass

				if contact_lists_size > 1:
					contact_lists_size = contact_lists_size - 1

				headquarters = 'None'
				media_spend = 'None'

				i = 0
				while i < contact_lists_size:

					try:
						company_name_clean = self.driver.find_element_by_class_name('profile-header').find_element_by_tag_name('strong').text.replace(',', '-').replace('\n', ' ')
					except:
						company_name_clean = 'None'

					try:
						headquarters = self.driver.find_element_by_id('location_area').find_elements_by_class_name('icn-pad')[i].find_elements_by_tag_name('div')[1].text.replace(',', '-').replace('\n', ' ')
					except:
						headquarters = 'None'

					try:
						media_spend = self.driver.find_element_by_xpath('/html/body/div[3]/div[2]/div[2]/strong').text.replace(',', '-').replace('\n', ' ')
					except:
						media_spend = 'None'

					# Get inside list of employees page
					self.driver.find_element_by_id('location_area').find_elements_by_class_name('icn-pad')[i].find_element_by_tag_name('div').find_element_by_tag_name('a').click()

					# Sort by Associated Brands
					self.driver.find_element_by_class_name('top-padding').find_element_by_xpath('a[3]').click()

					# Wait List to load
					time.sleep(5)


					# Check the linkedin property
					#self.driver.find_element_by_id('autoload_linkedin_profile').click()

					# Wait linkedin List to load
					#time.sleep(15)

					main_telephone  = 'None'
					main_fax        = 'None'
					primary_address = 'None'

					contact_details = self.driver.find_element_by_id('contact-details').find_elements_by_tag_name('div')

					for contact_detail in contact_details:
						phone_numbers = contact_detail.find_element_by_tag_name('dl').find_elements_by_css_selector('*')
						j = 0
						phone_numbers_size = len(phone_numbers)
						while j < phone_numbers_size:
							if 'Main Telephone' in phone_numbers[j].text.strip():
								try:
									main_telephone = phone_numbers[j+1].text.strip().replace(',', '-').replace('\n', ' ')
								except:
									main_telephone = 'None'
							elif 'Main Fax' in phone_numbers[j].text.strip():
								try:
									main_fax = phone_numbers[j+1].text.strip().replace(',', '-').replace('\n', ' ')
								except:
									main_fax = 'None'
							elif 'Primary Address' in phone_numbers[j].text.strip():
								try:
									primary_address = phone_numbers[j+1].text.strip().replace(',', '-').replace('\n', ' ')
								except:
									primary_address = 'None'
							j = j + 1

					contact_table = self.driver.find_element_by_id('tab-contacts').find_elements_by_class_name('contact')
					contact_table_size = len(contact_table)

					x = 0
					while x < contact_table_size:

						employee_firstname = 'None'
						employee_lastname  = 'None'
						employee_fullname  = 'None'
						employee_title     = 'None'
						direct_dial        = 'None'
						email              = 'None'
						#linkedin          = 'None'
						employee_associated_brands = 'None'

						employee = contact_table[x].find_element_by_tag_name('h5')

						try:
							employee_fullname = employee.find_element_by_class_name('name').text.strip().replace(',', '-').replace('\n', ' ')

							try:
								employee_fullname  = employee_fullname.split(' ', 2)
								employee_firstname = employee_fullname[1]
								employee_lastname  = employee_fullname[2]
							except:
								employee_lastname = 'None'
						except:
							employee_fullname  = 'None'
							employee_firstname = 'None'
							employee_lastname  = 'None'

						try:
							employee_title = employee.find_element_by_class_name('title').text.strip().replace(',', '-').replace('\n', ' ')
						except:
							employee_title = 'None'

						try:
							direct_dial_and_email = contact_table[x].find_element_by_xpath("div[2]/div[1]/div[contains(@class, 'div-email')]/p").text


							if '\n' in direct_dial_and_email:
								direct_dial_and_email = direct_dial_and_email.replace("Direct Dial:", "").replace("Email:", "")
								direct_dial = direct_dial_and_email.split('\n')[0]
								email = direct_dial_and_email.split('\n')[1]
							else:
								if "Direct Dial" in direct_dial_and_email:
									direct_dial_and_email = direct_dial_and_email.replace("Direct Dial:", "")
									direct_dial = direct_dial_and_email
								elif "Email" in direct_dial_and_email:
									direct_dial_and_email = direct_dial_and_email.replace("Email:", "")
									email = direct_dial_and_email
						except:
							direct_dial = 'None'
							email = 'None'


						self.driver.implicitly_wait(0)
						# Get associated brands
						try:
							associated_brands = contact_table[x].find_element_by_xpath("div[2]/div[3]/div[contains(@class, 'pct100')]").find_elements_by_class_name('pct033')

							# Show more brands
							try:
								contact_table[x].find_element_by_xpath("div[2]/div[3]/a[1]").click()
							except:
								pass

							for associated_brand in associated_brands:
								associated_brands_text = associated_brand.find_element_by_tag_name('ul').find_elements_by_tag_name('li')

								for associated_brand_text in associated_brands_text:
									brand_name = associated_brand_text.find_element_by_tag_name('a').text.replace(',', '.').replace('\n', ' ')
									if brand_name:
										if employee_associated_brands != 'None':
											employee_associated_brands = employee_associated_brands + '/' + brand_name
										else:
											employee_associated_brands = brand_name
						except:
							pass
						self.driver.implicitly_wait(15)


						#try:
						#	linkedin = contact_table[x].find_element_by_xpath("div[2]/div[contains(@class, 'float-box')]/ul/li/div/span/span/iframe/#document/html/body/div[1]/iframe/#document/html/body/div[1]/div/div/div[2]/div/div[1]/div/div[1]/h1/a").get_attribute("href")
						#except:
						#	linkedin = 'None'

						#print(linkedin)

						# Remove entries in the keywords input
						employee_title_keyphase = employee_title.lower().replace('-','').replace('\r', '').replace('\n', '').strip()
						invalid_professional = self.has_keywords(keywords, employee_title_keyphase)

						log.insert(END,'Loading: ' + employee_firstname + ', number: ' + str(x+1) + ' from ' + str(contact_table_size) + ', company: ' + company_name+"\n")
						log.yview(END)

						if email and not invalid_professional:
							if self.has_keywords(referral_keywords, employee_title_keyphase):
								output_data_referral.append("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(company_name_clean, headquarters, media_spend, main_telephone, main_fax, primary_address, employee_firstname, employee_lastname, employee_title, direct_dial, email, employee_associated_brands))
							elif self.has_keywords(special_keywords, employee_title_keyphase):
								output_data_special.append("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(company_name_clean, headquarters, media_spend, main_telephone, main_fax, primary_address, employee_firstname, employee_lastname, employee_title, direct_dial, email, employee_associated_brands))
							else:
								output_data_normal.append("{},{},{},{},{},{},{},{},{},{},{},{}\n".format(company_name_clean, headquarters, media_spend, main_telephone, main_fax, primary_address, employee_firstname, employee_lastname, employee_title, direct_dial, email, employee_associated_brands))

						x = x + 1


					log.insert(END, "-----------------------\n")
					log.yview(END)
					i = i + 1
					self.driver.back()

				k = k + 1
				counter = counter + 1

			except Exception as e:
				File().generate_log_file(self.industry, self.sub_industry, companies[k])
				self.execution_exception = True

				if str(e) == 'User wants to stop scraping':
					log.insert(END, "User stoped scraping at company: " + companies[k] + "\n")
					log.insert(END, "-----------------------\n")
					log.yview(END)
				else:
					log.insert(END, "Error during " + companies[k] + " processing!\n")
					log.insert(END, "Try again!\n")
					log.insert(END, "-----------------------\n")
					log.yview(END)

				break

		# Delete log file
		if not self.execution_exception:
			File().delete_log_file()

		return (output_data_referral, output_data_special, output_data_normal)

	def destroy(self):
		self.driver.close()


class Interface(Frame):

	left_align = 20
	left_align_field = 130

	def __init__(self, parent):

		frame = Frame.__init__(self, parent)

		self.thelist_extractor = TheListExtractor()

		self.parent = parent
		self.industries = self.thelist_extractor.get_industry_list()

		self.initUI()


	def initUI(self):

		self.parent.title("The List Scraper")

		self.pack(fill=BOTH, expand=1)
		self.center_window()

		self.logo_frame()
		self.industry_dropdown()
		self.sub_industry_dropdown()
		self.user_validation_checkbox()
		self.companies_text()
		self.keywords_text()
		self.field_keywords_checkbox()
		self.referral_keywords_text()
		self.field_referral_keywords_checkbox()
		self.special_keywords_text()
		self.field_special_keywords_checkbox()

		self.quit_button()
		self.csv_button()

		self.log_text()

	def center_window(self):

		self.width = 600
		self.heigth = 800

		sw = self.parent.winfo_screenwidth()
		sh = self.parent.winfo_screenheight()

		x = (sw - self.width)/2
		y = (sh - self.heigth)/2
		self.parent.geometry('%dx%d+%d+%d' % (self.width, self.heigth, x, y))


	def logo_frame(self):

		script_dir = os.path.dirname(os.path.abspath(__file__))

		logo_img = Image.open(os.path.join(script_dir, 'logo.jpg')).resize((350, 90),Image.ANTIALIAS)

		self.photo = ImageTk.PhotoImage(logo_img)

		self.logo = Label(self, image=self.photo)
		self.logo.image = self.photo # keep a reference!
		self.logo.place(x=115, y=10)

	def industry_label(self):

		self.industry_label = Label(self, text="Industry: ", font=("Helvetica", 18))
		self.industry_label.place(x=self.left_align, y=110)

	def field_update(self, option):

		sub_industries = []
		sub_industries.append('All')
		for industry in self.industries:
			if industry['name'] == option:
				for sub_industry in industry['list']:
					sub_industries.append(sub_industry)

		self.sub_industry_dropdown_default.set(sub_industries[0])

		self.sub_industry_dropdown['menu'].delete(0, "end")
		for sub_industry in sub_industries:
			self.sub_industry_dropdown['menu'].add_command(label=sub_industry, command=tkinter._setit(self.sub_industry_dropdown_default, sub_industry))

	def industry_dropdown(self):

		self.industry_label()

		industries = []
		for industry in self.industries:
			industries.append(industry['name'])

		self.industry_dropdown_default = StringVar()
		self.industry_dropdown_default.set(industries[0])

		self.industry_dropdown = OptionMenu(self, self.industry_dropdown_default, *industries, command=self.field_update)
		self.industry_dropdown.config(bd=0, bg=None)
		self.industry_dropdown.place(x=self.left_align+self.left_align_field, y=110)

	def sub_industry_dropdown(self):

		sub_industries = []
		sub_industries.append('All')
		for sub_industry in self.industries[0]['list']:
			sub_industries.append(sub_industry)

		self.sub_industry_dropdown_default = StringVar()
		self.sub_industry_dropdown_default.set(sub_industries[0])

		self.sub_industry_dropdown = OptionMenu(self, self.sub_industry_dropdown_default, *sub_industries)
		self.sub_industry_dropdown.config(bd=0, bg=None)
		self.sub_industry_dropdown.place(x=self.left_align+self.left_align_field, y=140)

	def user_validation_checkbox(self):

		self.user_validation_checkbox_val = IntVar()
		self.user_validation_checkbox_val.set(1)

		self.user_validation_checkbox = Checkbutton(self, text="User validation", variable=self.user_validation_checkbox_val)
		self.user_validation_checkbox.place(x=self.left_align+self.left_align_field+250, y=110)

	def companies_label(self):

		self.companies_label_details()

		self.companies_label = Label(self, text="Companies: ", font=("Helvetica", 18))
		self.companies_label.place(x=self.left_align, y=175)

	def companies_label_details(self):

		self.companies_label_details = Label(self, text="(separate by ';') ", font=("Helvetica", 12))
		self.companies_label_details.place(x=self.left_align, y=205)

	def companies_text(self):

		self.companies_label()

		self.companies_text = Text(self, height=4, width=50)
		self.companies_text.config(bd=0,  insertbackground="white", bg="black", fg="white")
		self.companies_text.place(x=self.left_align+self.left_align_field, y=175)

	def keywords_label(self):

		self.keywords_label_details()

		self.keywords_label = Label(self, text="Keywords: ", font=("Helvetica", 18))
		self.keywords_label.place(x=self.left_align, y=245)

	def keywords_label_details(self):

		self.keywords_label_details = Label(self, text="(separate by ';') ", font=("Helvetica", 12))
		self.keywords_label_details.place(x=self.left_align, y=275)

	def keywords_text(self):

		self.keywords_label()

		self.keywords_text = Text(self, height=4, width=50)
		self.keywords_text.config(bd=0, insertbackground="white", bg='black', fg="white")
		self.keywords_text.place(x=self.left_align+self.left_align_field, y=245)

	def select_keywords_checkbox(self):

		if self.field_keywords_checkbox_val.get() == 1:
			self.keywords_text.insert(END, "CFO;\nChief Financial Officer;\nHuman Resources;\nChairman;\nGeneral Counsel;\nTreasurer;\nController;\nFinance;\nTax;\nCopywriter;\nOperations;\nBudget;\nBilling;\nOffice Services;\nInvestment;\nSearch Engine;\nEnrollment;\nAcademic;\nCEO;\nCorporate Issues;\nAnalytics;\nModelling;\nCTO;\nChief Technology Officer;\nWriter;\nLeadership;\nSustainability;\nCitizenship;\nPrincipal;\nTechnology;\nRecruitment;\nTalent;\nPublic Affairs;\nGovernment;\nLegal;\nBusiness Intelligence;\nPractice;\nFinancial;\nStrategy;\nChief Strategy Officer;\nChief Talent Officer;\nTalent Acquisition;\nRetail Consultancy;\nStrategic Planning;\nCorporate Affairs;\nResearch;\nInvestor Relations;\nChief Operating Officer;\nExperience Planning;\nMedia Acquisition;\nPublic Relations;\nChief Revenue Officer;\nGroup Publisher;\nSales;\nLogistics;\nChief Commercial Officer;\nInsight;\nInformation Technology;\nMulticultural Strategy;\nConnections Planning;\nHuman Services;\nInternal Audit;\nManagement Supervisor;\nMedia Buyer;\nMedia Planner;\nOfficer Manager;\nTalent & Development;\nTrade Marketing;\nMedia Relations;\nProcurement;\nHome Care Division;\nStudio;\nPayable;\nAccountant;\nChief Recruitment Officer;\nChief Information Officer;\nPublisher;\nAudit;\nAdministration;\nChief Administrative Officer")
		else:
			self.keywords_text.delete(1.0, END)

	def field_keywords_checkbox(self):

		self.field_keywords_checkbox_val = IntVar()
		self.field_keywords_checkbox_val.set(0)

		self.field_keywords_checkbox = Checkbutton(self, text="Standard keywords", variable=self.field_keywords_checkbox_val, command=self.select_keywords_checkbox)
		self.field_keywords_checkbox.place(x=self.left_align+self.left_align_field, y=315)

	def referral_keywords_label(self):

		self.referral_keywords_label_details()

		self.referral_keywords_label = Label(self, text="Referral\nKeywords: ", font=("Helvetica", 18))
		self.referral_keywords_label.place(x=self.left_align, y=335)

	def referral_keywords_label_details(self):

		self.referral_keywords_label_details = Label(self, text="(separate by ';') ", font=("Helvetica", 12))
		self.referral_keywords_label_details.place(x=self.left_align, y=395)

	def referral_keywords_text(self):

		self.referral_keywords_label()

		self.referral_keywords_text = Text(self, height=4, width=50)
		self.referral_keywords_text.config(bd=0, insertbackground="white", bg='black', fg="white")
		self.referral_keywords_text.place(x=self.left_align+self.left_align_field, y=335)

	def select_referral_keywords_checkbox(self):

		if self.field_referral_keywords_checkbox_val.get() == 1:
			self.referral_keywords_text.insert(END, "VP;\nHead;\nPresident;\nFounder;\nVice;\nChief;\nExecutive;\nPartner;\nSVP")
		else:
			self.referral_keywords_text.delete(1.0, END)

	def field_referral_keywords_checkbox(self):

		self.field_referral_keywords_checkbox_val = IntVar()
		self.field_referral_keywords_checkbox_val.set(1)

		self.field_referral_keywords_checkbox = Checkbutton(self, text="Standard referral keywords", variable=self.field_referral_keywords_checkbox_val, command=self.select_referral_keywords_checkbox)
		self.field_referral_keywords_checkbox.place(x=self.left_align+self.left_align_field, y=405)

		# Set default values
		self.select_referral_keywords_checkbox()

	def special_keywords_label(self):

		self.special_keywords_label_details()

		self.special_keywords_label = Label(self, text="Special\nKeywords: ", font=("Helvetica", 18))
		self.special_keywords_label.place(x=self.left_align, y=435)

	def special_keywords_label_details(self):

		self.special_keywords_label_details = Label(self, text="(separate by ';') ", font=("Helvetica", 12))
		self.special_keywords_label_details.place(x=self.left_align, y=495)


	def special_keywords_text(self):

		self.special_keywords_label()

		self.special_keywords_text = Text(self, height=4, width=50)
		self.special_keywords_text.config(bd=0, insertbackground="white", bg='black', fg="white")
		self.special_keywords_text.place(x=self.left_align+self.left_align_field, y=435)

	def select_special_keywords_checkbox(self):

		if self.field_special_keywords_checkbox_val.get() == 1:
			self.special_keywords_text.insert(END, "Brand Managers;\nDirector of Marketing;\nDigital;\nSocial Media")
		else:
			self.special_keywords_text.delete(1.0, END)

	def field_special_keywords_checkbox(self):

		self.field_special_keywords_checkbox_val = IntVar()
		self.field_special_keywords_checkbox_val.set(1)

		self.field_special_keywords_checkbox = Checkbutton(self, text="Standard special keywords", variable=self.field_special_keywords_checkbox_val, command=self.select_special_keywords_checkbox)
		self.field_special_keywords_checkbox.place(x=self.left_align+self.left_align_field, y=505)

		# Set default values
		self.select_special_keywords_checkbox()

	def quit_button(self):

		self.quit_button = Button(self, text="Quit", command=self.close)
		self.quit_button.place(x=self.left_align+120, y=535)

	def csv_button(self):

		self.csv_button = Button(self, text="Generate CSV", command=self.generate_csv)
		self.csv_button.place(x=self.left_align, y=535)

	def log_label(self):

		self.log_label = Label(self, text="Log: ", font=("Helvetica", 18))
		self.log_label.place(x=self.left_align, y=565)

	def log_text(self):

		self.log_label()

		self.log_text = Text(self, height=10, width=80)
		self.log_text.config(bd=0, bg='black', fg="white", state='normal')
		self.log_text.place(x=self.left_align, y=605)


	def generate_csv(self):

		def callback():

			output_data_referral = []
			output_data_special = []
			output_data_normal = []
			companies = []
			file_name = "Companies"

			# Disable buttons
			self.quit_button.config(state='disabled')
			self.csv_button.config(state='disabled')

			self.log_text.insert(END, "-----------------------\n")
			self.log_text.insert(END, "Start date: " + str(datetime.datetime.now())+"\n")
			self.log_text.insert(END, "-----------------------\n")
			self.log_text.yview(END)
			self.log_text.insert(END, "Companies to be queried:\n")
			self.log_text.yview(END)

			company_filter = False

			# Get companies list
			if self.companies_text.get('0.0',END) and self.companies_text.get('0.0',END).isspace() == False:
				company_filter = True
				file_name = "Companies-filter" #self.companies_text.get('0.0',END).replace('\n', '').replace('\r', '').strip().replace(';','-')
				companies_list = self.companies_text.get('0.0',END).replace('\n', '').replace('\r', '').strip().split(';')
				companies = self.thelist_extractor.get_company_type_ahead(companies_list, self.log_text)
			else:
				file_name = self.industry_dropdown_default.get()
				if self.sub_industry_dropdown_default.get():
					file_name = file_name + '-' + self.sub_industry_dropdown_default.get()
				companies = self.thelist_extractor.get_companies_inside_industry(self.industry_dropdown_default.get(), self.sub_industry_dropdown_default.get(), self.log_text)

			# Check log to recover query
			companies = File().check_log_file(self.industry_dropdown_default.get(),
											self.sub_industry_dropdown_default.get(),
											company_filter,
											companies)

			# Get keywords list
			keywords_phrase = self.keywords_text.get('0.0',END).lower().replace('\n', '').replace('\r', '').strip().split(';')
			keywords = []
			for phrase in keywords_phrase:
				keyword = phrase.strip()
				if keyword:
					keywords.append(keyword)

			# Get referral keywords list
			referral_keywords_phrase = self.referral_keywords_text.get('0.0',END).lower().replace('\n', '').replace('\r', '').strip().split(';')
			referral_keywords = []
			for phrase in referral_keywords_phrase:
				keyword = phrase.strip()
				if keyword:
					referral_keywords.append(keyword)

			# Get special keywords list
			special_keywords_phrase = self.special_keywords_text.get('0.0',END).lower().replace('\n', '').replace('\r', '').strip().split(';')
			special_keywords = []
			for phrase in special_keywords_phrase:
				keyword = phrase.strip()
				if keyword:
					special_keywords.append(keyword)

			# Save query parameters
			if not (self.companies_text.get('0.0',END) and self.companies_text.get('0.0',END).isspace() == False):
				self.thelist_extractor.store_industry_params(self.industry_dropdown_default.get(), self.sub_industry_dropdown_default.get())
			else:
				self.thelist_extractor.store_industry_params(None, None)

			user_validation = None
			if self.user_validation_checkbox_val.get() == 1:
				user_validation = True
			else:
				user_validation = False

			# Generate file
			output_data_referral, output_data_special, output_data_normal  = self.thelist_extractor.find_companies_data(companies, keywords, referral_keywords, special_keywords, self.log_text, user_validation)

			if len(output_data_referral) > 0 or len(output_data_special) > 0  or len(output_data_normal) > 0:
				try:
					File().generate_report_file(output_data_referral, output_data_special, output_data_normal, self.log_text, file_name)
				except:
					self.log_text.insert(END,"Failed to create file -> " + file_name + "\n")
					self.log_text.yview(END)
			else:
				self.log_text.insert(END,"No companies found for this query!\n")
				self.log_text.yview(END)

			if not self.thelist_extractor.execution_exception:
				self.industries = self.thelist_extractor.get_industry_list()

			# Enable buttons
			self.quit_button.config(state='normal')
			self.csv_button.config(state='normal')

			self.log_text.insert(END, "-----------------------\n")
			self.log_text.insert(END, "End date: " + str(datetime.datetime.now())+"\n")
			self.log_text.insert(END, "-----------------------\n")
			self.log_text.yview(END)

		t = threading.Thread(target=callback)
		t.start()

	def close(self):
		self.thelist_extractor.destroy()
		self.quit()

def main():

	root = Tk()
	app = Interface(root)

	root.mainloop()

main()
