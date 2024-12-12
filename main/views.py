from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GoogleDriveFolder
from social_django.models import UserSocialAuth
import requests
from social_django.utils import load_strategy
from django.contrib import messages

 

@login_required
def dashboard(request):
    folders = GoogleDriveFolder.objects.filter(user=request.user)

    return render(request , 'dashboard.html', {'folders': folders})



@login_required
def create_folder(request):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access this page.")
        return redirect('login')  # Redirect to your custom login page if the user is not authenticated

    try:
        # Retrieve the user's Google OAuth2 social authentication info
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except UserSocialAuth.DoesNotExist:
        # If social authentication doesn't exist, redirect to your custom login page
        messages.error(request, "You need to log in using Google first.")
        return redirect('login')  # Redirect to your custom login page instead of social auth

    if not access_token:
        # If no access token is available, prompt the user to reauthenticate
        messages.error(request, "No access token found. Please re-authenticate with Google.")
        return redirect('login')  # Redirect to your custom login page

    # Continue with folder creation after ensuring the user is authenticated and authorized with Google
    folder_name = request.POST.get('folder_name')
    event_name = request.POST.get('event_name')

    if not folder_name or not event_name:
        messages.error(request, "Both folder name and event name are required.")
        return redirect('dashboard')  # Redirect back to the dashboard if folder name or event name is missing

    # Make the API call to Google Drive to create the folder
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {
        'Authorization': f'Bearer {access_token}',  # Authorization header with OAuth2 access token
        'Content-Type': 'application/json',
    }

    # Prepare the metadata for the folder creation request
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'  # MIME type for a folder in Google Drive
    }

    # Send POST request to Google Drive API
    response = requests.post(url, headers=headers, json=metadata)

    if response.status_code == 200:
        # If the folder was successfully created, extract the folder details
        folder_data = response.json()
        folder_id = folder_data.get('id')
        folder_name = folder_data.get('name')

        # Save folder details to your backend (database)
        GoogleDriveFolder.objects.create(
            user=request.user,
            folder_name=folder_name,
            folder_id=folder_id,
            event_name=event_name
        )

        # Show success message to the user
        messages.success(request, f"Folder '{folder_name}' created successfully.")
        return redirect('dashboard')  # Redirect to the dashboard

    else:
        # Handle the error response from the Google API
        messages.error(request, f"Failed to create folder on Google Drive. Error: {response.text}")
        return render(request, 'error.html', {'message': 'Failed to create folder on Google Drive.'})




from django.contrib import messages


@login_required
def sync_folders(request):
    sync_success = False
    try:
        # Retrieve the user's social authentication info (Google OAuth2)
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
        print("Access token:", access_token)
    except UserSocialAuth.DoesNotExist:
        messages.error(request, "You are not authenticated with Google.")
        return redirect('login')

    if not access_token:
        messages.error(request, "No access token found.")
        return redirect('login')

    folders = GoogleDriveFolder.objects.filter(user=request.user)

    for folder in folders:
        url = f"https://www.googleapis.com/drive/v3/files/{folder.folder_id}"
        headers = {'Authorization': f'Bearer {access_token}'}

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            folder_data = response.json()
            new_folder_name = folder_data.get('name')
            if new_folder_name != folder.folder_name:
                folder.folder_name = new_folder_name
                folder.save()
                messages.success(request, f"Folder '{folder.folder_name}' updated successfully.")
                sync_success = True

        elif response.status_code == 404:
            folder.delete()
            messages.info(request, f"Folder '{folder.folder_name}' was deleted from Google Drive.")
            sync_success = True

        else:
            messages.error(request, f"Failed to sync folder '{folder.folder_name}': {response.status_code}")

    # Redirect to dashboard with messages
    if sync_success:
        messages.success(request, "Folders synchronized successfully!")
    else:
        messages.warning(request, "No changes detected or sync failed.")

    return redirect('dashboard')