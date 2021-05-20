#!/usr/bin/env/python3


__author__ = 'nimish.chalkar@gmail.com'
__version__ = '1.0'


import requests
from time import strftime
from time import sleep
import pandas as pd
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_centers_by_district(district):

	date = strftime("%d-%m-%Y")

	url = f"https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={district}&date={date}"

	headers={'User-Agent': 'Mozilla/5.0'} # for the server to identify the request is coming a browser

	s = requests.Session()

	resp = s.get(url, headers=headers)

	if resp.status_code == 200:

		return resp.json()["centers"]

	elif resp.status_code != 200:

		return resp.status_code


def check_min18_sessions(sessions):

	min18_sessions = []

	for session in sessions:

		if session["min_age_limit"] == 18 and session["available_capacity"] > 0:

			min18_sessions.append([session["date"],session["vaccine"],session["available_capacity_dose1"],session["available_capacity_dose2"]])

	return min18_sessions


def send_alert(to_addrs, data):

	from_addrs = "smtpbot25@gmail.com"

	msg = MIMEMultipart("multipart")

	msg["From"] = from_addrs

	msg["Subject"] = "Vaccine slots available for 18+ in Mumbai [CoWin]"

	text = """

	To book a slot, login to https://www.cowin.gov.in/home

	**This is an auto-generated email. Do not reply**

"""
	html = data

	# Record the MIME types of both parts - text/plain and text/html.

	part2 = MIMEText(text, 'plain')

	part1 = MIMEText(html, 'html')

	msg.attach(part1)
	
	msg.attach(part2)

	s = SMTP("smtp.gmail.com")

	s.connect(host="smtp.gmail.com", port=587)

	s.ehlo()

	s.starttls()
	
	s.ehlo()

	s.login(from_addrs,"Password@2022")

	s.sendmail(from_addrs, to_addrs, msg.as_string())

	s.quit()



if __name__ == "__main__":

	district = 395 # Mumbai

	# for other districts in Maharashtra check the link "https://cdn-api.co-vin.in/api/v2/admin/location/districts/21"

	while True:
		
		centers = get_centers_by_district(district)
		
		if centers != 200:
			
			print(f"Unable to fetch data")
			
			break

		available_sessions = []

		for center in centers:

			available_slots = check_min18_sessions(center["sessions"])

			if available_slots != []:

				available_sessions.append([center["name"],center["address"],center["district_name"],"-".join([center["from"],center["to"]]),center["vaccine_fees"],available_slots])
		
		if available_sessions != []:

			available_sessions_df = pd.DataFrame(available_sessions,columns=["Center","Address","District","Timing","Vaccine fees","Session (Date, Vaccine, Avl. Dose 1, Avl. Dose 2)"])

			print(f"{strftime("%Y/%m/%d %I:%M:%S %p")} Slot Available!")

			send_alert("email address", available_sessions_df.to_html()) # Enter your email id

		sleep(300)
