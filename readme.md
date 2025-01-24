<div align="center">

  <img src="static/glr/images/sharemysnaps_black.png" alt="logo" width="200" height="auto" />
  <h1>Personalized Photo Gallery Web App</h1>
  
<!-- Badges -->
<p>
  <a href="https://github.com/anujjamdade007/sharemysnaps/graphs/contributors">
    <img src="https://img.shields.io/github/contributors/anujjamdade007/sharemysnaps" alt="contributors" />
  </a>
  <a href="https://github.com/anujjamdade007/sharemysnaps/network/members">
    <img src="https://img.shields.io/github/forks/anujjamdade007/sharemysnaps" alt="forks" />
  </a>
  <a href="https://github.com/anujjamdade007/sharemysnaps/stargazers">
    <img src="https://img.shields.io/github/stars/anujjamdade007/sharemysnaps" alt="stars" />
  </a>
  <a href="https://github.com/anujjamdade007/sharemysnaps/issues/">
    <img src="https://img.shields.io/github/issues/anujjamdade007/sharemysnaps" alt="open issues" />
  </a>
</p>
</div>

---
A web application that allows users to create personalized photo galleries with seamless Google OAuth integration and storage on Google Drive. Users can easily upload, manage, and display their images in a custom-designed gallery layout.


<!-- About the Project -->
## :star2: About the Project


<!-- Screenshots -->
### :camera: Screenshots

<div align="center"> 
  
  <img src="static/glr/images/11.png" alt="screenshot" />
  <img alt="dashboard" src="https://github.com/user-attachments/assets/d030857e-0724-4ace-af8b-2997b27e43f0" />
  <img alt="home page" src="https://github.com/user-attachments/assets/ed157a80-f39c-4c20-b71c-e12178c590f3" />

</div>
  


## 🚀 **Features**

- **🔐 Google OAuth Integration**: Secure user sign-up and authentication using Google accounts.
- **☁️ Google Drive Storage**: Directly upload and store images to your Google Drive.
- **🎨 Custom Gallery Layouts**: Personalize your gallery with custom-designed pages and layouts.
- **📸 Easy Image Management**: Effortlessly organize, view, and manage images from your Google Drive via the app.
- **⚡ Seamless File Handling**: Powered by the Google Drive API for efficient file management and storage.

---

## 🛠 **Technologies Used**
[![My Skills](https://skillicons.dev/icons?i=py,django,tailwind)](https://skillicons.dev)

- **Python**: Backend development with Python.
- **Django**: Web framework for building the application.
- **Tailwind CSS**: For modern, responsive, and customizable front-end design.
- **Google Drive API**: To manage image uploads and storage.

---

## 🌟 **How It Works**

1. **User Authentication**: Users sign in securely using their Google account through Google OAuth.
2. **Image Upload**: Users can upload images directly to their Google Drive.
3. **Custom Gallery Creation**: The web app auto-generates personalized gallery pages to display the images in a beautifully designed layout.
4. **View and Manage**: Users can view their gallery, add or remove images, and adjust the layout as needed.

---

## 💻 **Installation & Setup**

### 1. Clone this repository

```bash
git clone https://github.com/anujjamdade007/sharemysnaps.git
cd sharemysnaps

```

### 2. Set up the virtual environment

```bash
python -m venv venv
source venv/bin/activate   # For Linux/macOS
venv\Scripts\activate      # For Windows

```

### 3. Install required dependencies

Ensure you have the `requirements.txt` file in the root directory. Install the necessary dependencies:

```bash
pip install -r requirements.txt

```

### 4. Set up Environment Variables

Create a `.env` file in the root directory of your project and add the following credentials:

```dotenv
# Google API Key
API_KEY='Your API Key'

# Google OAuth2 credentials
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY='Your API Key'
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET='Your API Key'

SECRET_KEY='Your Secret Key'

# Debug setting (set to False for production)
DEBUG=True

# Database Credentials
NAME='Database Name'
USER='Database User'
PASSWORD='Database Password'

```

### 5. Configure Google OAuth and Google Drive API

-   Set up **Google OAuth credentials** in the [Google Developer Console](https://console.developers.google.com/).
-   Enable the **Google Drive API** and make sure your project is linked to the OAuth credentials.
-   Place your **client_id** and **client_secret** values into the `.env` file under `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` and `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET`.

### 6. Set Up the Database

Ensure that your PostgreSQL database is running. Update the `.env` file with your **database** credentials as needed.

Run the following commands to set up the database:

```bash
python manage.py makemigrations
python manage.py migrate

```

### 7. Run the development server

```bash
python manage.py runserver

```

Now, navigate to `http://127.0.0.1:8000/` to start using the app!


----------

## 💬 **Contributions**

Contributions are welcome! If you'd like to contribute, please fork the repository and submit a pull request.

----------

## 💬 **Contact**

For any inquiries, please feel free to reach out via [ajk952626@gmail.com](mailto:ajk952626@gmail.com).

----------
