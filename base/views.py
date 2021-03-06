from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpResponse
from .models import Message, Room, Topic, User
from .forms import RoomForm, UserForm


def logoutUser(request):
    logout(request)
    return redirect('home')


def registerUser(request):
    form = UserCreationForm()

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Un error ha ocurrido durante el registro')
    context = {'form': form}
    return render(request, 'base/login_register.html', context)


def loginPage(request):

    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'El susuario no existe')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Error de credenciales')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)

    )

    room_count = rooms.count()
    room_messages = Message.objects.filter(
        Q(room__topic__name__icontains=q)
    )[:8]

    topics = Topic.objects.all()[:5]

    context = {'rooms': rooms,
               'topics': topics,
               'room_count': room_count,
               'room_messages': room_messages}
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all()
    participants = room.participants.all()

    if request.method == "POST":
        if not request.user.is_authenticated:
            return redirect('login')

        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)

        return redirect('room', pk=room.id)

    context = {'room': room,
               'room_messages': room_messages,
               'participants': participants}
    return render(request, 'base/room.html', context)


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    room_count = topics.count()

    context = {'user': user,
               'rooms': rooms,
               'topics': topics,
               'room_messages': room_messages,
               'room_count': room_count
               }

    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm
    topics = Topic.objects.all()

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(
            name=topic_name)  # return created=True if is created
        form = RoomForm(request.POST)  # create

        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),

        )

        # if form.is_valid():
        #    room = form.save(commit=False)
        #    room.host = request.user
        #    room.save()
        return redirect('home')

    context = {'form': form,
               'topics': topics,
               }
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('Not allowed!')

    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(
            name=topic_name)  # return created=True if is created
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        return redirect('home')

    context = {'form': form,
               'topics': topics,
               'room': room,
               }

    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('Not allowed')

    if request.method == "POST":
        room.delete()
        return redirect('home')

    context = {'obj': room}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('Not allowed')

    if request.method == "POST":
        message.delete()
        return redirect('home')

    context = {'obj': message}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def updateUser(request, pk):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update_user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ""
    topics_count = Topic.objects.all().count()
    topics = Topic.objects.filter(name__icontains=q)

    context = {'topics': topics,
               'topics_count': topics_count,
               }
    return render(request, 'base/topics.html', context)


def activityPage(request):
    room_messages = Message.objects.all()[:5]

    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)
