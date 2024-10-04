from datetime import datetime
import pygame
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os  # For environment variables

# GraphQL endpoint
url = "https://e5mquma77feepi2bdn4d6h3mpu.appsync-api.us-east-1.amazonaws.com/graphql"
refresh_url = "https://hiring.amazon.ca/app#/jobSearch?query=&postal=&locale=en-CA"

# Headers including Authorization token (replace with environment variable)
headers = {
    "Authorization": f"Bearer {os.getenv('AUTH_TOKEN')}",  # Token stored in environment variable
    "Content-Type": "application/json",
}

# Full GraphQL query
query = """
query searchJobCardsByLocation($searchJobRequest: SearchJobRequest!) {
  searchJobCardsByLocation(searchJobRequest: $searchJobRequest) {
    nextToken
    jobCards {
      jobId
      language
      dataSource
      requisitionType
      jobTitle 
      jobType
      employmentType
      city 
      state
      postalCode
      locationName
      totalPayRateMin
      totalPayRateMax
      tagLine
      bannerText
      image
      jobPreviewVideo
      distance
      featuredJob
      bonusJob
      bonusPay
      scheduleCount
      currencyCode
      geoClusterDescription
      surgePay
      jobTypeL10N
      employmentTypeL10N
      bonusPayL10N
      surgePayL10N
      totalPayRateMinL10N
      totalPayRateMaxL10N
      distanceL10N
      monthlyBasePayMin
      monthlyBasePayMinL10N
      monthlyBasePayMax
      monthlyBasePayMaxL10N
      jobContainerJobMetaL1
      virtualLocation
      poolingEnabled
      __typename
    }
    __typename
  }
}
"""

# Expanded variables based on the payload you provided
variables = {
    "searchJobRequest": {
        "locale": "en-CA",  # Locale
        "country": "Canada",  # Country
        "keyWords": "",  # Keywords for job search (e.g., "Developer", "Engineer")
        "equalFilters": [],  # Filters that must match exactly
    }
}

# Email configuration (stored in environment variables)
SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')  # Use environment variable for password
TO_EMAIL = os.getenv('TO_EMAIL')

# Path to siren sound file (replace with environment variable or relative path)
siren_sound = os.getenv('SIREN_SOUND', 'path/to/default/siren.wav')

# Initialize pygame mixer
pygame.mixer.init()

def send_email(subject, body):
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # Secure the connection
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)

def play_siren():
    pygame.mixer.music.load(siren_sound)
    pygame.mixer.music.play()

def refresh_session():
    """Refresh the URL to keep the session alive"""
    response = requests.get(refresh_url, headers=headers)
    if response.status_code == 200:
        print("Session refreshed successfully. Time now: " + datetime.now().strftime("%H:%M:%S"))
    else:
        print(f"Failed to refresh session: {response.status_code}")

def fetch_job_postings():
    response = requests.post(url, json={"query": query, "variables": variables}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        job_cards = data['data']['searchJobCardsByLocation']['jobCards']
        return job_cards
    else:
        print(f"Failed to fetch data: {response.status_code}")
        return []

def monitor_jobs():
    seen_jobs = set()
    while True:
        refresh_session()  # Refresh the session every 1 minute
        job_cards = fetch_job_postings()
        new_jobs = [job for job in job_cards if job['jobId'] not in seen_jobs]

        if new_jobs:
            for job in new_jobs:
                seen_jobs.add(job['jobId'])
                job_details = (f"Location: {job['city']}, {job['state']}\n"
                               f"Job Id: {job['jobId']}\n"
                               f"Job Title: {job['jobTitle']}\n"
                               f"Pay: {job['totalPayRateMin']} - {job['totalPayRateMax']}\n"
                               f"Distance: {job['distance']} km\n")
                print(job_details)

                send_email("New Job Alert! ", job_details)

                # Only play the siren if job is located in QC
                if job['state'] == "QC":
                    play_siren()
        else:
            print("No new jobs found. \n")

        time.sleep(60)  # Check every 1 minute (60 seconds)

if __name__ == "__main__":
    monitor_jobs()
