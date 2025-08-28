from datetime import datetime

import pygame
import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import time
import os
from dotenv import load_dotenv
load_dotenv()

# GraphQL endpoint
url = "https://e5mquma77feepi2bdn4d6h3mpu.appsync-api.us-east-1.amazonaws.com/graphql"
refresh_url = "https://hiring.amazon.ca/app#/jobSearch?query=&postal=&locale=en-CA"

# Headers including Authorization token
headers = {

    "Authorization": "Bearer Status|unauthenticated|Session|eyJhbGciOiJLTVMiLCJ0eXAiOiJKV1QifQ.eyJpYXQiOjE3NTU3Njk2ODUsImV4cCI6MTc1NTc3MzI4NX0.AQICAHidzPmCkg52ERUUfDIMwcDZBDzd+C71CJf6w0t6dq2uqwFjuyjdc9OCcLxlT5drun2JAAAAtDCBsQYJKoZIhvcNAQcGoIGjMIGgAgEAMIGaBgkqhkiG9w0BBwEwHgYJYIZIAWUDBAEuMBEEDPFYQGcFbERDzn8+0QIBEIBtqwUsyNXBVavACPQcxj61SUMyPYwKrhBOvCYpdryX5hBvBz/JUxVAICl9PuTI6msn7nbPvucb8a/McAFUIbK0ppoxMl36Y+/nuRQsxqJwfb0IxiL9RJetL4lra1nA0lKw7xY433X6K9fPvYzHcg==",
    "Origin": "https://hiring.amazon.ca",
    "Referer": "https://hiring.amazon.ca/",
    "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36",
    "Content-Type": "application/json; charset=UTF-8",
    "x-amz-cf-id": "tLq_ggTpBR94fVStjHpqyI_CqiW-_YxkK7jb50aCoMZYbegpbbmFaA==",
    "x-amz-cf-pop": "YTO50-P3",
    "x-amzn-appsync-tokensconsumed": "1",
    "x-amzn-requestid": "e2333295-31ec-451d-baa3-5f178eb81f1e",
    "Accept": "*/*"
}

# Full GraphQL query
query = "query searchJobCardsByLocation($searchJobRequest: SearchJobRequest!) {\n  searchJobCardsByLocation(searchJobRequest: $searchJobRequest) {\n    nextToken\n    jobCards {\n      jobId\n      language\n      dataSource\n      requisitionType\n      jobTitle\n      jobType\n      employmentType\n      city\n      state\n      postalCode\n      locationName\n      totalPayRateMin\n      totalPayRateMax\n      tagLine\n      bannerText\n      image\n      jobPreviewVideo\n      distance\n      featuredJob\n      bonusJob\n      bonusPay\n      scheduleCount\n      currencyCode\n      geoClusterDescription\n      surgePay\n      jobTypeL10N\n      employmentTypeL10N\n      bonusPayL10N\n      surgePayL10N\n      totalPayRateMinL10N\n      totalPayRateMaxL10N\n      distanceL10N\n      monthlyBasePayMin\n      monthlyBasePayMinL10N\n      monthlyBasePayMax\n      monthlyBasePayMaxL10N\n      jobContainerJobMetaL1\n      virtualLocation\n      poolingEnabled\n      payFrequency\n      __typename\n    }\n    __typename\n  }\n}\n"

# Expanded variables based on the payload you provided
variables = {
    "searchJobRequest": {
        "locale": "en-CA",  # Locale
        "country": "Canada",  # Country
        "keyWords": "",  # Keywords for job search (e.g., "Developer", "Engineer")
        "equalFilters": [],  # Filters that must match exactly
    }
}

# Email configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")


# Path to your siren sound file
siren_sound = "C:/Users/Muqaddas/Downloads/mixkit-ambulance-siren-us-1642.wav"


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
    #locations_to_monitor = ["Laval", "Lachine", "Longueuil", "Montreal"]
    while True:
        refresh_session()  # Refresh the session every 1 minutes
        job_cards = fetch_job_postings()
        #new_jobs = [job for job in job_cards if job['jobId'] not in seen_jobs]
        new_jobs = [job for job in job_cards]

        if new_jobs:
            for job in new_jobs:
                seen_jobs.add(job['jobId'])


                job_location = job.get('city', '')
                job_details = (f"Location: {job['city']}, {job['state']}\n"
                               f"Job Id: {job['jobId']}\n"
                               f"Job Title: {job['jobTitle']}\n"
                               f"Pay: {job['totalPayRateMin']} - {job['totalPayRateMax']}\n"
                               f"Distance: {job['distance']} km\n")
                print(job_details)

                #send_email("New Job Alert! ", job_details)
                #  if job['state'] == "QC" and any(location in job_location for location in locations_to_monitor):
                if job['state'] == "ON" or job['state'] == "AB":
                    play_siren()
                    send_email("New Job Alert! ", job_details)
        else:
            print("No new jobs found. \n")

        time.sleep(60)  # Check every 1 minutes (60 seconds)


if __name__ == "__main__":
    monitor_jobs()
