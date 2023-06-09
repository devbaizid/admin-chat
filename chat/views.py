from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.contrib.auth.decorators import login_required
from django.http.response import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import User, Message
from django.db.models import Q
from django.shortcuts import redirect
import json
from .forms import *
from .models import UserProfile
from guest_user.decorators import allow_guest_user


def register(request):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST, files=request.FILES)
        user_profile_form = UserProfileForm(request.POST, files=request.FILES)
        if user_form.is_valid() and user_profile_form.is_valid():
            user = user_form.save()
            user_profile = user_profile_form.save(commit=False)
            user_profile.user  = user
            user_profile.save()
            return redirect('login')
        else:
            messages.error(request, "Please correct errors in the form")
    else:
        user_form = UserCreationForm()
        user_profile_form = UserProfileForm()

    return render(request, 'register.html', {'user_form': user_form, 'user_profile_form': user_profile_form})
@allow_guest_user
def homepage(request):
    users = User.objects.all()
    return render(request, 'homepage.html', {'users': users})


@allow_guest_user
@login_required
def chatroom(request, pk:int):
    other_user = get_object_or_404(User, pk=pk)
    messages = Message.objects.filter(
        Q(receiver=request.user, sender=other_user)
    )
    messages.update(seen=True)
    messages = messages | Message.objects.filter(Q(receiver=other_user, sender=request.user) )
    return render(request, "chatroom1.html", {"other_user": other_user, 'users': User.objects.all(), "user_messages": messages})


@login_required
def ajax_load_messages(request, pk):
    other_user = get_object_or_404(User, pk=pk)
    messages = Message.objects.filter(seen=False, receiver=request.user)
    
    print("messages")
    message_list = [{
        "sender": message.sender.username,
        "message": message.message,
        "sent": message.sender == request.user,
        "picture": other_user.profile.picture.url,

        "date_created": naturaltime(message.date_created),

    } for message in messages]
    messages.update(seen=True)
    
    if request.method == "POST":
        message = json.loads(request.body)['message']
        
        m = Message.objects.create(receiver=other_user, sender=request.user, message=message)
        message_list.append({
            "sender": request.user.username,
            "username": request.user.username,
            "message": m.message,
            "date_created": naturaltime(m.date_created),

            "picture": request.user.profile.picture.url,
            "sent": True,
        })
    print(message_list)
    return JsonResponse(message_list, safe=False)




def message_File_upload(request):
  
    if request.method == 'POST':
        form = MessageForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
       
    else:
        form = MessageForm()
    return render(request, 'chatroom.html', {'form': form})






def offer(request):
    if request.method == 'POST':
        # Handle the offer from the first user
        offer = request.POST.get('offer')
        # Store the offer or send it to the other user through a signaling mechanism

        # Code to handle offer and send it to the other user
        # ...

        # Return a JSON response indicating success
        return JsonResponse({'status': 'success'})
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def answer(request):
    if request.method == 'POST':
        # Handle the answer from the second user
        answer = request.POST.get('answer')
        # Send the answer to the first user through a signaling mechanism

        # Code to handle the answer and send it to the first user
        # ...

        # Return a JSON response indicating success
        return JsonResponse({'status': 'success'})
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def ice_candidate(request):
    if request.method == 'POST':
        # Handle ICE candidate from either user
        candidate = request.POST.get('candidate')
        # Send the ICE candidate to the other user through a signaling mechanism

        # Code to handle the ICE candidate and send it to the other user
        # ...

        # Return a JSON response indicating success
        return JsonResponse({'status': 'success'})
    else:
        # Return a JSON response indicating failure
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})