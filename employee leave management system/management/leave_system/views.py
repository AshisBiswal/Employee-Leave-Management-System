from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, redirect
from .models import *
from .forms import register_form,login_form,LeaveForm,CommentForm,ProfileUpdateForm, UserUpdateForm
from datetime import date
from django.db.models import Q
from django.http import JsonResponse
from django.urls import reverse



def register(request):
    if request.method == "POST":
        form = register_form(request.POST)
        if form.is_valid():
         
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            role = form.cleaned_data['role']

           
            if User.objects.filter(username=username).exists():
                messages.info(request, "Username already taken!")
                return redirect('/register/')
            
         
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
                password=password  
            )

           
            profile = Profile.objects.create(
                user=user,
                role=role,
                email=email
            )

            return redirect('/login/')
    else:
        form = register_form()
    return render(request, 'register.html', {'form': form})

  
def login_f(request):
    if request.method == "POST":
        form = login_form(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            if not User.objects.filter(username = username).exists():
                messages.error(request, 'Invalid Username')
                return redirect('/login/')

            user = authenticate(username=username, password=password)

            if user is None:
                messages.error(request, "Invalid Password")
                return redirect('/login/')
            else:
              
                login(request, user)
                profile = Profile.objects.get(user = user)
                if(profile.role == 'manager'):
                    return render(request,'manager.html')
                else:
                    
                   
                    return render(request,'employee.html',calculate_leave_stats(profile))


               
    else:
        form = login_form()
        return render(request,'login.html',{'form':form})

def employee(request):
        profile = Profile.objects.get(user = request.user)
        
        return render(request,'employee.html',calculate_leave_stats(profile))



def manager(request):
        
        return render(request,'manager.html')

def requests(request):
        leave_requests = Request.objects.filter(manager=request.user.profile)
        return render(request, 'request_leave.html', {'leave_requests': leave_requests})

        
        
def notification(request):
        received_notifications = Notification.objects.filter(recipient=request.user)
        return render(request, 'notifications.html', {'received_notifications': received_notifications})
        




def apply(request):
        
        return render(request,'applyleave.html',{'form':LeaveForm})

def applied(request):
        leaves = Leave.objects.filter(profile=request.user.profile)
        return render(request, 'applied.html', {'leaves': leaves})
        
        


def leave_request(request):
    if request.method == 'POST':
        form = LeaveForm(request.POST)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.profile = request.user.profile  
            leave.save()
            
            
            manager = leave.manager
            Notification.objects.create(
                sender=request.user,
                recipient=manager.user,
                leave=leave,
                message=f"A new leave request from {request.user.username} is awaiting your approval."
            )
            
       
            Request.objects.create(
                leave=leave,
                manager=manager
            )
            
            return redirect('employee')  
    else:
        form = LeaveForm()
    return render(request, 'applyleave.html', {'form': form})

def approve_leave(request, request_id):

    leave_request = get_object_or_404(Request, pk=request_id)
    
    leave_request.leave.status = 'approved'
    leave_request.leave.save()
    
    #leave_request.delete()
    
    return redirect('requests')

def reject_leave(request, request_id):
  
    leave_request = get_object_or_404(Request, pk=request_id)
   
    leave_request.leave.status = 'rejected'
    leave_request.leave.save()
    
    #leave_request.delete()
   
    return redirect('requests')


def calculate_leave_stats(profile):
    
    approved_leaves = Leave.objects.filter(profile=profile, status='approved')

  
    total_leave_days = 25  
    total_sick_leave_days = 11  
    total_used_leave_days = 0
    total_used_sick_leave_days = 0
    Nopay_leaves = 0
  
    for leave in approved_leaves:
        days = (leave.end_date - leave.start_date).days + 1  
        if leave.type == 'Vacation':
            total_used_leave_days += days
        elif leave.type == 'Sick':
            total_used_sick_leave_days += days

   
    remaining_leave_days = total_leave_days - total_used_leave_days
    remaining_sick_leave_days = total_sick_leave_days - total_used_sick_leave_days

    if(remaining_sick_leave_days < 0):
         Nopay_leaves+=abs(remaining_sick_leave_days)
         remaining_sick_leave_days = 0
    
    if(remaining_leave_days < 0):
         Nopay_leaves+=abs(remaining_leave_days)
         remaining_leave_days = 0

    return {
        'remaining_leave_days': remaining_leave_days,
        'remaining_sick_leave_days': remaining_sick_leave_days,
        'No_pay_leaves':Nopay_leaves
        
    }


def leave_events(request):
    leave_events = []
    user = request.user
    if hasattr(user, 'profile'):  
        profile_id = user.profile.pk
    leaves = Leave.objects.filter(manager_id = profile_id,status="approved")
    for leave in leaves:
        leave_events.append({
            'title': leave.profile.user.username,
            'start': leave.start_date.strftime('%Y-%m-%d'),
            'end': leave.end_date.strftime('%Y-%m-%d'),
            'backgroundColor': '#75CE9' if leave.type == 'Vacation' else '#09eef4'
        })
    return JsonResponse(leave_events, safe=False)


def calendar(request):
     
     return render(request,'calendar.html')


def add_comment(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.leave = leave
            comment.commenter = request.user
            comment.save()
        
    
        form = CommentForm()
    
  
        comments = leave.comments.all()

        return render(request, 'addcomment.html', {'form': form, 'comments': comments})
    
def leave_comment(request,leave_id):
  
      
        return add_comment(request, leave_id)
   
        #return applied(request)


def markread_notification(request,notification_id):
    notification = get_object_or_404(Notification, pk=notification_id)
    if request.method == 'POST':
        notification.status = "read"
        notification.save() 
    return redirect('notifications')

def delete_notification(request,notification_id):
     
    notification = get_object_or_404(Notification, pk=notification_id)
    if request.method == 'POST':
        notification.delete()
        return redirect('notifications')  
    return redirect('notifications') 




def profile_update(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile_update')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)
    return render(request, 'update.html', {'user_form': user_form, 'profile_form': profile_form})




def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    leave_id = comment.leave_id
    leave = get_object_or_404(Leave, id=leave_id)

    if request.user == comment.commenter:
        comment.delete()

    comments = leave.comments.all()
    form = CommentForm()
    return render(request,'addcomment.html',{'comments':comments,'form':form})



def manager_comment(request, leave_id):
    leave = get_object_or_404(Leave, id=leave_id)

    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.leave = leave
            comment.commenter = request.user
            comment.save()
            #return redirect('comment/')  # Redirect to a success URL
    
        form = CommentForm()
    
 
        comments = leave.comments.all()

        return render(request, 'manager_comment.html', {'form': form, 'comments': comments})