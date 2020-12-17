from django.shortcuts import render,redirect
from django.http import HttpResponse
from .models import Tutorials,TutorialSeries,TutorialCategory
#from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.forms import AuthenticationForm
from .form import NewUserForm
from django.contrib.auth import login,logout,authenticate
from django.contrib import messages

# Create your views here.
def single_url(request, single_url):
    categories = [c.category_url_part for c in TutorialCategory.objects.all()]

    if single_url in categories:
        matching_series = TutorialSeries.objects.filter(tutorial_category__category_url_part = single_url) #__ represents we are fetching category_url_part attribute from tutorial_category
        
        series_urls = {}
        
        for m in matching_series.all():
            part_one = Tutorials.objects.filter(tutorial_series__tutorial_series=m.tutorial_series).earliest("tutorial_published") #fetching TutorialSeries.tutorial_series attribute for Tutorials.tutorial_series
        
            series_urls[m] = part_one.tutorial_url_part
        
        #return HttpResponse(f"{single_url} is a category!!!")
        return render(request=request, 
                    template_name="main/category.html",
                     context={ "tutorial_series": matching_series,"part_ones": series_urls})

    tutorials = [t.tutorial_url_part for t in Tutorials.objects.all()]

    if single_url in tutorials:
        this_tutorial = Tutorials.objects.get(tutorial_url_part = single_url)

        tutorials_from_series = Tutorials.objects.filter(tutorial_series__tutorial_series = this_tutorial.tutorial_series).order_by("tutorial_published")
        
        this_tutorial_idx = list(tutorials_from_series).index(this_tutorial)
        return render(request= request,
                    template_name="main/tutorial.html",
                   context={"tutorial" : this_tutorial,
                   "sidebar": tutorials_from_series,
                   "this_tutorial_idx": this_tutorial_idx} )

    return HttpResponse(f'{single_url} does not correspond to anything.')
    



def homepage(request):
    return render(request = request,
                template_name = "main/categories.html",
                context = {"categories" : TutorialCategory.objects.all()} 
    )

def register(request):
    if request.method == "POST":
        #form = UserCreationForm(request.POST)
        form = NewUserForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f"New Account Created : {username}")
            login(request,user) #to login user after registering
            messages.info(request, f'You are now logged in as : {username}')
            return redirect("WebApp:homepage") #used to redirect to in urls.py -> app_name:name without mentioning url explicitly which helps incase urls change
        else:
            for msg in form.error_messages:
                messages.error(request, f'{msg} : {form.error_messages}')
            


    #form = UserCreationForm
    form = NewUserForm
    return render(request,
                "main/register.html",
                context = {"form" : form})


def logout_request(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect("WebApp:homepage")

def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data = request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username') 
            password = form.cleaned_data.get('password')
            user = authenticate(username = username,password = password)
            if user is not None:
                login(request, user)
                messages.info(request, f'You are now logged in as : {username}')
                return redirect("WebApp:homepage")
            else:
                messages.error(request, "Invalid username or password")
        else:
                messages.error(request, "Invalid username or password")
    form = AuthenticationForm()
    return render(request, "main/login.html",{"form" : form})
    