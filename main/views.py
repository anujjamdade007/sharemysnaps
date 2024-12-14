from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GoogleDriveFolder
from social_django.models import UserSocialAuth
import requests
from social_django.utils import load_strategy
from django.contrib import messages

 

@login_required
def dashboard(request):
    try:
        # Retrieve the user's Google OAuth2 social authentication info
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception as e:
        messages.error(request, f"Session Time Out Please Login Again")
        return redirect('login')
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
    except Exception as e:
        messages.error(request, f"Session Time Out Please Login Again")
        return redirect('login')

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
        # Retrieve the user's Google OAuth2 social authentication info
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception as e:
        messages.error(request, f"Session Time Out Please Login Again")
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


import json
import requests
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import default_storage


import json
import requests
from django.contrib import messages
from django.shortcuts import redirect, render
from django.core.files.storage import default_storage
from requests_toolbelt.multipart.encoder import MultipartEncoder
from io import BytesIO

@login_required
def upload_image_to_folder(request, folder_id):
    if not request.user.is_authenticated:
        messages.error(request, "You need to be logged in to access this page.")
        return redirect('login')

    try:
        # Retrieve the user's Google OAuth2 social authentication info
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception as e:
        messages.error(request, f"Session Time Out Please Login Again")
        return redirect('login')

    if not access_token:
        messages.error(request, "No access token found. Please re-authenticate with Google.")
        return redirect('login')

    if request.method == 'POST' and request.FILES.get('image_file'):
        image_file = request.FILES['image_file']
        image_name = image_file.name
        upload_simple_image(request, access_token, image_name, folder_id, image_file)

        # Check the file size and decide on upload type (simple or resumable)
        # file_size = image_file.size
        # if file_size <= 10 * 1024 * 1024:  # Small file (<= 10MB) - Simple Upload
        #     return upload_simple_image(request, access_token, image_name, folder_id, image_file)
        # else:  # Large file (> 10MB) - Resumable Upload
        #     return upload_resumable_image(request, access_token, image_name, folder_id, image_file)

    return render(request, 'upload.html', {'folder_id': folder_id})

def upload_simple_image(request, access_token, image_name, folder_id, image_file):
    # Prepare the metadata for the image upload
    metadata = {
        'name': image_name,
        'parents': [folder_id],  # Ensure the 'parents' field points to the folder
    }

    # Create a multipart encoder to send metadata and file together
    multipart_data = MultipartEncoder(
        fields={
            'metadata': ('metadata', json.dumps(metadata), 'application/json'),
            'file': ('file', image_file, image_file.content_type)  # Dynamically use the content type
        }
    )

    # Define the URL and headers for the simple upload
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': multipart_data.content_type,  # Set the correct content type for multipart
    }

    # Send the POST request to upload the image to Google Drive
    response = requests.post(url, headers=headers, data=multipart_data)

    if response.status_code == 200:
        file_data = response.json()
        file_name = file_data.get('name')
        messages.success(request, f"File '{file_name}' uploaded successfully to folder!")
        return redirect('dashboard')
    else:
        messages.error(request, f"Failed to upload file. Error: {response.text}")
        return redirect('upload_image')
    

def upload_resumable_image(request, access_token, image_name, folder_id, image_file):
    # Initiate the resumable upload session
    url = "https://www.googleapis.com/upload/drive/v3/files?uploadType=resumable"
    metadata = {
        'name': image_name,
        'parents': [folder_id],
    }
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json; charset=UTF-8',
    }

    # Prepare the data for the initial POST request to initiate the resumable upload
    response = requests.post(url, headers=headers, json=metadata)
    
    if response.status_code == 200:
        resumable_session_url = response.headers['Location']

        # Now, upload the file data in chunks
        upload_file_in_chunks(resumable_session_url, image_file)
        
        messages.success(request, f"File '{image_name}' uploaded successfully!")
        return redirect('dashboard')
    else:
        messages.error(request, f"Failed to initiate resumable upload. Error: {response.text}")
        return redirect('upload_image')

def upload_file_in_chunks(resumable_session_url, image_file):
    # Set the chunk size for the upload (e.g., 5MB)
    CHUNK_SIZE = 5 * 1024 * 1024
    
    # Get the total size of the image file
    file_size = image_file.size
    
    # Create a generator to read the file in chunks
    def generate_chunks():
        while True:
            chunk = image_file.read(CHUNK_SIZE)  # Read chunk by chunk from the uploaded file
            if not chunk:
                break
            yield chunk
    
    # Initialize the upload request
    headers = {
        'Content-Range': f'bytes 0-{file_size - 1}/{file_size}',
        'Content-Type': 'application/octet-stream'
    }

    # Send the initial chunk request
    for chunk in generate_chunks():
        response = requests.put(resumable_session_url, headers=headers, data=chunk)
        
        if response.status_code == 200:
            # The upload completed successfully
            print("Upload complete")
        elif response.status_code == 308:
            # Continue uploading if the server responds with a 308 (Resume Incomplete)
            continue
        else:
            # Handle errors
            print(f"Error occurred: {response.status_code} - {response.text}")
            break

