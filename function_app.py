import azure.functions as func
import logging
import os
import requests
import yagmail

app = func.FunctionApp()

def send_email(subject, body):
    # Set up your email credentials
    email_sender = os.environ['EmailSender']
    email_password = os.environ['EmailPassword']
    email_recipient = os.environ['EmailRecipient']

    # Initialize the yagmail SMTP client
    yag = yagmail.SMTP(email_sender, email_password)

    # Send the email
    yag.send(
        to=email_recipient,
        subject=subject,
        contents=body
    )
def main(req: func.HttpRequest) -> func.HttpResponse:
    # Define your Matomo API URL and access token
    MATOMO_API_URL = os.environ['MATOMO_API_URL']
    MATOMO_API_TOKEN = os.environ['MATOMO_API_TOKEN']

    # Define the API method to get the Matomo version
    api_method = 'API.getMatomoVersion'

    # Define the parameters for the API request
    params = {
        'module': 'API',
        'method': api_method,
        'format': 'JSON',
        'token_auth': MATOMO_API_TOKEN,
    }

    try:
        # Make the API request
        response = requests.get(MATOMO_API_URL, params=params)

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            matomo_version = data['value']
            return func.HttpResponse(f"The Matomo service is up and running with Matomo Version: {matomo_version}")
        else:
            # Prepare an email to send when there's an error
            email_subject = "Matomo API Error Notification"
            email_body = f"The Matomo service is Not up and running. HTTP Status Code: {response.status_code}"
            
            # Send email notification
            send_email(email_subject, email_body)
            
            return func.HttpResponse(email_body)
    except requests.exceptions.RequestException as e:
        email_subject = "Matomo API Error Notification"
        email_body = f"An error occurred while making the API request: {e}"
        
        # Send email notification
        send_email(email_subject, email_body)
            
        return func.HttpResponse(f"An error occurred while making the API request: {e}")
    except Exception as e:
        email_subject = "Matomo API Error Notification"
        email_body = f"An unexpected error occurred while making the API request: {e}"
        
        # Send email notification
        send_email(email_subject, email_body)
        return func.HttpResponse(f"An unexpected error occurred: {e}")