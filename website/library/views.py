from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.views import generic
from django.views.generic import View
from .models import Book, Request
from django.contrib.auth.models import User, auth, Group
from datetime import date,datetime, timedelta

def index(request):
    book_list = []
    if request.method=='POST':
        search_query = request.POST['search']
        book_list_title = Book.objects.filter(title__icontains=search_query)
        book_list_author = Book.objects.filter(author__icontains=search_query)
        book_list_genre = Book.objects.filter(genre__icontains=search_query)
        book_list_ISBN = Book.objects.filter(ISBN__icontains=search_query)
        book_list = book_list_title.union(book_list_author,book_list_genre,book_list_ISBN)
        if(len(book_list)==0):
            messages.info(request,"No search result found.")
    else:
        book_list = Book.objects.all()
    return render(request, 'library/index.html',{'books':book_list})

def user_profile(request):
    user = request.user
    if not user.is_authenticated:
        return redirect('library:login')
    else:
        request_list = Request.objects.filter(user=user)
        return render(request, 'library/user_profile.html',{'user':user,'request_list':request_list})

def detail(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    return render(request, 'library/detail.html',{'book':book})

def request_book(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, "You need to log in to make a request")
            return redirect('library:login')
        
        old_requests = Request.objects.filter(user=request.user,book=book)  #check if user has another request with same book
        for req in old_requests:
            if req.is_ongoing() and req.status!=2:
                messages.info(request,'You have ongoing requests of same book')
                return render(request, 'library/request.html', {'book':book})
        
        
        if book.available == False:
            #return render(request, 'library/request.html', {'book':book,'messages':['Book not available']})
            messages.info(request, "Book not available")
            return render(request, 'library/request.html', {'book':book})
        elif request.user.groups.filter(name="Librarian").exists():
            messages.info(request, "Librarian can't reqeust books")
            #return render(request, 'library/request.html', {'book':book,'messages':["Librarian can't request books"]})
            return render(request, 'library/request.html', {'book':book})
        else:
            time = request.POST['time']
            if time == '' or not time.isnumeric():
                messages.info(request, "Input not a valid number")
                return render(request, 'library/request.html', {'book':book})
            start_date = date.today()
            end_date = date.today() + timedelta(days=int(time))
            user = request.user
            request_book_entry = Request(user=user,book=book,start_date=start_date,end_date=end_date)
            request_book_entry.save()
            return redirect('library:index')
    else:
        return render(request, 'library/request.html', {'book':book})

def renew(request, book_request_id):
    book_request = get_object_or_404(Request, pk=book_request_id)
    book = book_request.book
    if not request.user == book_request.user:
        return HttpResponse("<h3>Unauthroized Access</h3>")

    if request.method=='POST':
        time = request.POST['time']
        book_request.end_date = book_request.end_date + timedelta(days=int(time))
        book_request.status = 0
        book_request.save()
        messages.info(request, "Renew requested successfully")
        return redirect('library:user_profile')
    else:
        return render(request, 'library/renew.html', {'book':book})


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        password_verify = request.POST['password_verify']
        username = request.POST['username']

        if password==password_verify:
            if User.objects.filter(username=username).exists():
                messages.info(request,'Username Taken')
                return redirect('library:register')
            elif User.objects.filter(email=email).exists():
                messages.info(request,'Email Taken')
                return redirect('library:register')
            else:                
                user = User.objects.create_user(username=username,password=password,email=email)
                user.save()
                return redirect('library:login')
        else:
            messages.info(request,"Passwords don't match")
            return redirect('library:register')
    else:
        return render(request, 'library/register.html')

def login(request):
    if request.method == 'POST':
        password = request.POST['password']
        username = request.POST['username']
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect("library:index")
        else:
            messages.info(request, 'Invalid username and/or password')
            return redirect("library:login")
    else:
        return render(request, 'library/login.html')

def logout(request):
    auth.logout(request)
    return redirect('library:index')


# class RegisterUserView(View):
#     form_class = RegisterUser
#     template_name = 'library/registration.html'

#     def get(self, request):
#         form = self.form_class(None)
#         return render(request, self.template_name, {'form':form})

#     def post(self, request):
#         form = self.form_class(request.POST)

#         if form.is_valid():
#             user = form.save(commit=False)
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']
#             user.set_password(password)
#             user.save()

#             user = authenticate(username=username, password=password)

#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('library:index')
#         return render(request, self.template_name, {'form':form})



# class LoginView(View):
#     form_class = LoginUser
#     template_name = 'library/login.html'

#     def get(self, request):
#         form = self.form_class(None)
#         return render(request, self.template_name, {'form':form})

#     def post(self, request):
#         form = self.form_class(request.POST)
#         if form.is_valid():
#             user = form.save(commit=False)
#             username = form.cleaned_data['username']
#             password = form.cleaned_data['password']

#             user = authenticate(username=username, password=password)

#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('library:index')
#                 else:
#                     return render(request, 'library/login.html',{'error_message':'Account Disabled'})
#             else:
#                 return render(request, 'library/login.html',{'error_message':'Invalid Login'})
#         return render(request, self.template_name, {'form':form})

