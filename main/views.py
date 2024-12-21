from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GoogleDriveFolder
from social_django.models import UserSocialAuth
import requests
from social_django.utils import load_strategy
from django.contrib import messages
import os
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()
 

@login_required
def dashboard(request):
    try:
        # Retrieve the user's Google OAuth2 social authentication info
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception as e:
        messages.error(request, "Session Time Out. Please Login Again.")
        return redirect('login')

    # Get Google Drive storage usage
    storage_url = "https://www.googleapis.com/drive/v3/about?fields=storageQuota"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(storage_url, headers=headers)

    if response.status_code == 200:
        # Parse the storage quota information
        storage_data = response.json()
        total_storage = int(storage_data['storageQuota']['limit'])  # Total storage in bytes
        used_storage = int(storage_data['storageQuota']['usage'])  # Used storage in bytes

        # Convert bytes to GB (with more precision, avoid premature rounding)
        total_storage_gb = total_storage / (1024 ** 3)  # GB
        used_storage_gb = used_storage / (1024 ** 3)  # GB

        # Calculate the percentage of used storage
        storage_percentage = (used_storage / total_storage) * 100
        storage_percentage = round(storage_percentage, 2)

    else:
        # Handle error fetching storage information
        storage_percentage = None
        messages.error(request, "Failed to retrieve Google Drive storage information.")

    folders = GoogleDriveFolder.objects.filter(user=request.user)

    return render(request, 'dashboard.html', {
        'folders': folders,
        'storage_percentage': storage_percentage,
        'used_storage_gb': round(used_storage_gb, 2),
        'total_storage_gb': round(total_storage_gb, 2)
    })

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
        messages.error(request, f"Session Time Out. Please Login Again.")
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

        # Now, update the permissions to make it publicly viewable
        permission_url = f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions"
        permission_data = {
            "role": "reader",  # 'reader' means view-only access
            "type": "anyone",  # Make the folder accessible to anyone
            "withLink": True   # Anyone with the link can view the folder
        }

        # Send POST request to set the permission
        permission_response = requests.post(permission_url, headers=headers, json=permission_data)

        if permission_response.status_code == 200:
            # Save folder details to your backend (database)
            GoogleDriveFolder.objects.create(
                user=request.user,
                folder_name=folder_name,
                folder_id=folder_id,
                event_name=event_name
            )

            # Show success message to the user
            messages.success(request, f"Folder '{folder_name}' created successfully and is now publicly viewable.")
            return redirect('dashboard')  # Redirect to the dashboard
        else:
            messages.error(request, f"Failed to set public access for the folder. Error: {permission_response.text}")
            return render(request, 'error.html', {'message': 'Failed to set public access for the folder.'})

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
        # print("access token: ", access_token)
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

    
    messages.success(request, "Folders synchronized successfully!")

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
            # print(f"Error occurred: {response.status_code} - {response.text}")
            break



@login_required
def redirect_to_folder(request, folder_id):
    try:
        # Retrieve the user's Google OAuth2 social authentication info
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception as e:
        messages.error(request, "Session timed out. Please log in again.")
        return redirect('login')

    if not access_token:
        messages.error(request, "No access token found. Please re-authenticate with Google.")
        return redirect('login')

    # Construct the URL to the Google Drive folder
    drive_folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

    # Redirect the user to the folder in Google Drive
    return redirect(drive_folder_url)


import requests
from django.shortcuts import render
from django.http import HttpResponse

# Add your Google API key here

# def gallery(request, folder_id):
#     # Public API call to fetch files from the folder using the API key
#     url = f"https://www.googleapis.com/drive/v3/files?q='{folder_id}' in parents&fields=files(id,name,mimeType)&key={API_KEY}"
#     response = requests.get(url)

#     if response.status_code == 200:
#         files_data = response.json().get('files', [])
#         # Filter for image files
#         images = [
#             {'id': file['id'], 'name': file['name'], 'mimeType': file['mimeType']}
#             for file in files_data if file['mimeType'].startswith('image/')
#         ]
#     else:
#         images = []

#     return render(request, 'gallary1.html', {'images': images, 'folder_id': folder_id})


# def viewimages(request, file_id):
#     # Public API call to fetch the image file from Google Drive (no authentication needed)
#     url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media&key={API_KEY}"
#     response = requests.get(url)

#     # Debugging: print status code and URL to fetch the image
#     print(f"Fetching image {file_id} from Google Drive. URL: {url}")
        
#     if response.status_code == 200:
#         # Serve the image as a download
#         return HttpResponse(response.content, content_type='image/jpeg')  # This can be adjusted based on the file type
#     else:
#         pass

# f"https://drive.google.com/uc?export=view&id={image_ids}"

import requests
from urllib.parse import quote_plus

# URL to fetch files from a Google Drive folder (use your own API key here)
BASE_URL = "https://www.googleapis.com/drive/v3/files"

# Function to fetch image IDs from Google Drive folder
def fetch_image_ids_from_folder(folder_id, api_key):
    # URL encode the folder ID for safe query string formatting
    encoded_folder_id = quote_plus(folder_id)

    # Construct the URL to get all files in the folder, filtering for images
    url = f"{BASE_URL}?q='{encoded_folder_id}' in parents and mimeType contains 'image/'&key={api_key}"

    # Make the GET request to Google Drive API
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        files = data.get('files', [])
        
        # Extract and return the file IDs
        image_ids = [file['id'] for file in files]
        # print(image_ids)
        return image_ids
    else:
        # If an error occurs, print the error response
        # print(f"Error: {response.status_code} - {response.text}")
        return []


import requests
from django.http import HttpResponse

import requests
from django.http import HttpResponse
import mimetypes

def serve_image(request, image_ids):
    # Build the URL for Google Drive image
    image_url = f"https://drive.google.com/uc?export=view&id={image_ids}"

    try:
        # Public API call to fetch the image file
        response = requests.get(image_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Get the content type from the response headers
            content_type = response.headers.get('Content-Type', '').split(';')[0]
            
            # If the content type is not provided, try to deduce it from the file extension (if possible)
            if not content_type:
                file_extension = image_ids.split('.')[-1].lower()
                content_type, _ = mimetypes.guess_type(f"image.{file_extension}")
            
            # If content type still not found, fallback to a generic image type (could be adjusted)
            if not content_type:
                content_type = 'application/octet-stream'
            
            # Serve the image as a response with the correct content type
            return HttpResponse(response.content, content_type=content_type)

        else:
            # Handle error gracefully, for example, returning a 404 page or error message
            return HttpResponse("Image not found", status=404)
    
    except Exception as e:
        # Catch any unexpected errors and return an internal server error
        return HttpResponse(f"An error occurred: {str(e)}", status=500)


# View function for the gallery


def image_gallery(request, folder_id):
    # Your public API key for Google Drive
    api_key =os.getenv('API_KEY') # Replace with your actual API key

    # Fetch image IDs from the folder
    image_ids = fetch_image_ids_from_folder(folder_id, api_key)
    # print(image_ids)
    # Render the gallery with the list of image URLs
    return render(request, 'gallary1.html', {'image_ids': image_ids})




