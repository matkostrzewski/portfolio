from datetime import date, datetime
import json, random
from django.contrib.auth import models
from django.core import serializers
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login as _login, logout as _logout
from django.views.decorators import cache as cache_decorator
from social.models import Category, Post, LoginAntyBruteForce, Profile, Like, Comment, Follow, Refflink, ReportType, UserInfo, ActivateCode, Category, Photo, Report, ReportType
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from social.staticStrings import StaticString
from django.core.paginator import Paginator
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.core.cache.utils import make_template_fragment_key
from social.collectData import getFollows, getLikes

#TODO: make validate page for admins only
#TODO: comment posts
#TODO: cookies
#TODO: ads


def home(request):
    #TODO: enable search
    #TODO: add filters
    posts = None
    try:
        _refflink = cache.get('refflink')
    except:
        _refflink = None
    c = None
    tag = None
    if request.GET.get('category'):
        c = request.GET.get('category')
        c = str(c)[1:]
        c = c.split('.')
    if request.GET.get('tag'):
        tag = request.GET.get('tag')
    if c != None and tag != None:
        posts = Post.objects.filter(tags__icontains=tag, category_id__in=c, is_active=True).order_by('-created_at')
    elif c != None:
        posts = Post.objects.filter(category_id__in=c, is_active=True).order_by('-created_at')
    elif tag != None:
        posts = Post.objects.filter(tags__icontains=tag, is_active=True).order_by('-created_at')
    else:
        posts = Post.getAll()
        
    if request.GET.get('page'):
        pageNum = request.GET.get('page')
    else:
        pageNum = 1
    pages = Paginator(posts, 10)
    page1 = pages.page(pageNum)     

    try:
        _categories = cache.get('categories')
    except:
        _categories = Category.objects.all()
        cache.set('categories', _categories)
    if _categories == None:
        _categories = Category.objects.all()
        cache.set('categories', _categories)
        
    return render(request, 'home.html', context= {
        'title': "Home",
        'posts':page1, 
        'listings': page1, 
        'paginator':pages, 
        'likes': getLikes(request, page1), 
        'follows':  getFollows(request, page1), 
        'categories': _categories,
        'refflink':_refflink
        })

def profile(request, profileName):
    profile = get_object_or_404(Profile, displayName=profileName)
    reff = Refflink.objects.get(profile=profile)
    posts = Post.objects.filter(owner=profile, is_active=True)
    return render(request, 'profile.html', context={
        'title': 'Profile', 
        'profile': profile, 'posts': posts, 'refflink': reff
        })

def profileById(request, profileId):
    profile = Profile.objects.get(pk=profileId)
    return redirect('profile', profileName=profile.displayName)
    
def newPost(request):

    return render(request, 'newPost.html', context={
        'title': 'new post'
    })

def uploadImage(request):
    if request.method == "POST" and request.user.is_authenticated:
        post = Post()
        tags = request.POST.get('tags')
        dictionary = []
        tagsArray = tags.split(",")
        for tag in tagsArray:
            if len(tag) > 32:
                tagsArray.remove(tag)
            for d in dictionary:
                if tag == d:
                    tagsArray.remove(tag)
        post.tags = tagsArray
        post.owner = Profile.objects.get(user=request.user.id)
        if request.FILES.get('photo'):
            post.category = Category.objects.get(id=1)
            post.save()

            #multiple files future
            photo = Photo()
            photo.image = request.FILES.get('photo')
            photo.isFirstPhoto = True
            photo.post = post
            photo.save()
            return JsonResponse({"status": "ok"})
        else:
            return JsonResponse({"status": "no-file found"})
    return JsonResponse({"status": "bad request"})

def postId(request, id):
    #TODO: Comments and likes 
    post = get_object_or_404(Post, pk=id)
    return render(request, 'post.html', context={
        'title': 'post',
        'post': post
    })

def report(request, _type, targetID):
    #TODO: add captcha
    #TODO: send reports
    #TODO: add prefabs list
    report = Report()
    report.type = ReportType.objects.get(name=_type)
    report.reason = request.GET.get("reasons")
    report.targetID = targetID
    report.save()
    
    return render(request, 'report.html', context={
        'title': 'report',
        'type': _type
    })

def ranking(request):
    profiles = Profile.objects.all().order_by('-totalLikes')[:25]
    you = None
    if request.user.is_authenticated:
        you = Profile.objects.get(user=request.user.id)
    return render(request, 'ranking.html', context={
        'title': 'ranking', 'profiles': profiles, 'you': you
    })

def liked(request):
    #TODO: Display your liked posts
    posts = Like.objects.filter(whoLiked=request.user.userProfile, likeStatus=True).order_by('-created_at')

    return render(request, 'liked.html', context={
        'title': 'Liked posts',
        'posts': posts
    })

def followed(request):
        me = Profile.objects.get(id=request.user.userProfile.id)
        yourFollows = Follow.objects.filter(follower=me, isFollowed=True).order_by('followed_at')
        return render(request, 'followed.html', context={
        'title': 'Followed',
        'yourFollows': yourFollows,
    })

def login(request):
    userIp = get_client_ip(request)
    try:
        isUserBanned = LoginAntyBruteForce.objects.get(ip=userIp)
    except ObjectDoesNotExist:
        isUserBanned = None
    if isUserBanned != None:
        if isUserBanned.minutesAgo() >= 5:
            isUserBanned.status = False
            isUserBanned.attempts = 0
            isUserBanned.save()
    if isUserBanned != None and isUserBanned.status:
        messages.error(request, StaticString.tooManyLoginAttempts)
        return redirect('home')
    else:
        return render(request, 'login.html', context={'title': 'Login'})

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def loginValidate(request):
    #TODO: add captcha
    userIp = get_client_ip(request)
    try:
        isUserBanned = LoginAntyBruteForce.objects.get(ip=userIp)
        isBanned = isUserBanned.status
    except ObjectDoesNotExist:
        isBanned = False
    if request.method == "POST" and isBanned == False:
        #try login
        success = 0
        username = request.POST.get('login')
        password = request.POST.get('pass')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            _login(request, user)
            success = 1
        elif User.objects.filter(username=username, is_active=False).exists():
            messages.error(request, StaticString.userBanned)
            return redirect("login")
        if success:
            messages.success(request, StaticString.loginSuccess)
            return redirect("home")
        else:
            if isBanned == False:
                if(LoginAntyBruteForce.objects.filter(ip=userIp).exists()):      
                    isUserBanned = LoginAntyBruteForce.objects.get(ip=userIp)
                else:
                    isUserBanned = LoginAntyBruteForce(ip=userIp)
                    isUserBanned.save()
                isUserBanned.attempts = isUserBanned.attempts + 1
                isUserBanned.lastTry = datetime.now()
                if isUserBanned.attempts == 5:
                    isUserBanned.status = True
                    isUserBanned.attempts = 0
                    isUserBanned.save()
                    messages.error(request,  StaticString.tooManyLoginAttempts)
                    return redirect('home')
                else:
                    isUserBanned.save()
                    messages.error(request,  StaticString.loginFailed)
                    return redirect("login")
            else:
                messages.error(request,  StaticString.loginFailed)
                return redirect("login")
    else:
        return redirect("home")

def registerValidate(request):
    #TODO: add captcha
    if request.method == "POST":
        username = request.POST.get('username')
        displayName = request.POST.get('displayName')
        pass1 = request.POST.get('pass1')
        pass2 = request.POST.get('pass2')

        canCreateNewAccount = True
        if User.objects.filter(username=username).exists():
            canCreateNewAccount = False
            messages.error(request, StaticString.usernameTaken)

        elif Profile.objects.filter(displayName=displayName).exists():
            canCreateNewAccount = False
            messages.error(request, StaticString.displayNameTaken)

        elif pass1 != pass2:
            canCreateNewAccount = False
            messages.error(request, StaticString.passwordNotMatch)
            
        if canCreateNewAccount:
            newUser = User()
            newUser.username = username
            newUser.set_password(pass1)
            newUser.email = "{0}@empty.com".format(username)
            newUser.save()
            newProfile = Profile()
            newProfile.user = newUser
            newProfile.displayName = displayName
            newProfile.save()
            newCode = ActivateCode(profile=newProfile)
            newCode.save()
            user = authenticate(request, username=username, password=pass1)
            if user is not None:
                success = 1
                while success:
                    try:
                        newReff = Refflink(profile=newProfile)
                        newReff.save()
                        success = 0
                    except:
                        success = 1
                try:
                    _ip = get_client_ip(request)
                    reff = cache.get('refflink')
                    reff = Refflink.objects.get(code=reff)
                    userInfo = UserInfo(profile=newProfile, ip=_ip, refflinkUsed=reff)
                    userInfo.save()
                    reff.used += 1
                    reff.save()
                    cache.delete('refflink')
                    print("Checking REFF")
                    print(reff.profile)
                    reff.profile.refflinkPoints(_ip)
                except:
                    userInfo = UserInfo(profile=newProfile, ip=get_client_ip(request))
                    userInfo.save()
                    pass
                _login(request, user)
            return redirect('activateView')
        else:
            return redirect('login')

def refflinkView(request, code):
    try:
        if Refflink.objects.filter(code=code).exists():
            cache.set('refflink', code, 60*10)
            return redirect('home')
        else:
            return redirect('home')
    except:
        return redirect('home')

def logout(request):
    if request.user.is_authenticated:
        _logout(request)
        messages.success(request, 'Logout Successful')
        return redirect('home')

def activateView(request):
    if request.user.is_authenticated and not request.user.userProfile.activated:
        activateCode = ActivateCode.objects.get(profile_id=request.user.userProfile.id)
        return render(request, 'activate.html', context={'title': "Activate account",
            'activateCode': activateCode.code
        })
    else:
        messages.success(request, 'Your account is activated')
        return redirect('home')

@cache_decorator.cache_page(60*10)
def support(request):
    return render(request, 'support.html', context={
        'title': 'Support'
    })
    
@cache_decorator.cache_page(60*10)
def changes(request):
    return render(request, 'changes.html', context={
        'title': 'Changelog'
    })

@cache_decorator.cache_page(60*10)
def contact(request):
    return render(request, 'contact.html', context={
        'title': 'Contact'
    })

@cache_decorator.cache_page(60*10)
def page404(request, exception):
    return render(request, "page404.html")

@cache_decorator.cache_page(60*10)
def page403(request, exception):   
    return render(request, "page403.html")
