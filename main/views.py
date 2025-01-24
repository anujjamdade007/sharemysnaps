from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import GoogleDriveFolder
import requests
from social_django.utils import load_strategy
import os
from dotenv import load_dotenv
from django.contrib import messages
from urllib.parse import quote_plus
from django.http import HttpResponse
import mimetypes
from .forms import GoogleDriveFolderForm

# Load environment variables from .env file
load_dotenv()
 

@login_required
def dashboard(request):
    try:
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception:
        messages.error(request, "Session Time Out. Please Login Again.")
        return redirect('login')

   
    storage_url = "https://www.googleapis.com/drive/v3/about?fields=storageQuota"
    headers = {
        'Authorization': f'Bearer {access_token}',
    }
    response = requests.get(storage_url, headers=headers)

    if response.status_code == 200:    
        storage_data = response.json()
        total_storage = int(storage_data['storageQuota']['limit']) 
        used_storage = int(storage_data['storageQuota']['usage'])  

       
        total_storage_gb = total_storage / (1024 ** 3) 
        used_storage_gb = used_storage / (1024 ** 3)  

        
        storage_percentage = (used_storage / total_storage) * 100
        storage_percentage = round(storage_percentage, 2)

    else:
        storage_percentage = None
        messages.error(request, "Failed to retrieve Google Drive storage information. Consider review the permisions")
        # At this point we didnt got the permission to access Gdrive data, so user probaly
        # forget to given the permission
        return redirect('login')

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
        return redirect('login')  

    try:
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception:
        messages.error(request, "Session Time Out. Please Login Again.")
        return redirect('login')

    if not access_token:
        messages.error(request, "No access token found. Please re-authenticate with Google.")
        return redirect('login') 

    
    folder_name = request.POST.get('folder_name')
    event_name = request.POST.get('event_name')

    if not folder_name or not event_name:
        messages.error(request, "Both folder name and event name are required.")
        return redirect('dashboard')  

    
    url = "https://www.googleapis.com/drive/v3/files"
    headers = {
        'Authorization': f'Bearer {access_token}',  
        'Content-Type': 'application/json',
    }

   
    metadata = {
        'name': folder_name,
        'mimeType': 'application/vnd.google-apps.folder'  
    }

    
    response = requests.post(url, headers=headers, json=metadata)

    if response.status_code == 200:
        
        folder_data = response.json()
        folder_id = folder_data.get('id')
        folder_name = folder_data.get('name')

        
        permission_url = f"https://www.googleapis.com/drive/v3/files/{folder_id}/permissions"
        permission_data = {
            "role": "reader",  
            "type": "anyone",  
            "withLink": True   
        }

        
        permission_response = requests.post(permission_url, headers=headers, json=permission_data)

        if permission_response.status_code == 200:
            GoogleDriveFolder.objects.create(
                user=request.user,
                folder_name=folder_name,
                folder_id=folder_id,
                event_name=event_name
            )

           
            messages.success(request, f"Folder '{folder_name}' created successfully and is now publicly viewable.")
            return redirect('dashboard')  
        else:
            messages.error(request, f"Failed to set public access for the folder. Error: {permission_response.text}")
            return render(request, 'error.html', {'message': 'Failed to set public access for the folder.'})

    else:
        
        messages.error(request, f"Failed to create folder on Google Drive. Error: {response.text}")
        return render(request, 'error.html', {'message': 'Failed to create folder on Google Drive.'})




@login_required
def sync_folders(request):
    sync_success = False
    try:
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
        # print("access token: ", access_token)
    except Exception:
        messages.error(request, "Session Time Out Please Login Again")
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



@login_required
def redirect_to_folder(request, folder_id):
    try:
        # Retrieve the user's Google OAuth2 social authentication info
        social_user = request.user.social_auth.get(provider='google-oauth2')
        access_token = social_user.get_access_token(load_strategy())
    except Exception:
        messages.error(request, "Session timed out. Please log in again.")
        return redirect('login')

    if not access_token:
        messages.error(request, "No access token found. Please re-authenticate with Google.")
        return redirect('login')

    # Construct the URL to the Google Drive folder
    drive_folder_url = f"https://drive.google.com/drive/folders/{folder_id}"

    # Redirect the user to the folder in Google Drive
    return redirect(drive_folder_url)




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


def serve_image(request, image_ids):
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
    folder = GoogleDriveFolder.objects.get(folder_id=folder_id)
    # Fetch image IDs from the folder
    image_ids = fetch_image_ids_from_folder(folder_id, api_key)
    # print(image_ids)
    # Render the gallery with the list of image URLs
    return render(request, 'gallary.html', {'image_ids': image_ids , 'folder': folder})


@login_required
def customize(request, folder_id):
    folder = GoogleDriveFolder.objects.get(folder_id=folder_id)
    
    if request.method == 'POST':
        form = GoogleDriveFolderForm(request.POST, request.FILES, instance=folder)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = GoogleDriveFolderForm(instance=folder)
    
    return render(request, 'customize.html', {'form': form, 'folder': folder})


