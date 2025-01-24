from django.shortcuts import render
from django.contrib.auth import login 


# Create your views here.
# Home page
def index(request):
    return render(request, 'index.html')

# # signup page
# def user_signup(request):

#     if request.user.is_authenticated:
#         return redirect('dashboard')
    
#     if request.method == 'POST':
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             form.save()
#             return redirect('login')
#     else:
#         form = SignupForm()
#     return render(request, 'signup.html', {'form': form})

# login page
def login(request):
    
    # if request.user.is_authenticated:
    #     return redirect('dashboard')
    
    return render(request, 'login.html')


def privacy(request):
    
    return render(request, 'privacy.html')

def terms(request):
    
    return render(request, 't&c.html')
