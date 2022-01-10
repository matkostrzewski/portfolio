from django.db.models.expressions import Case
from django.shortcuts import redirect, render
import requests, array
from django.contrib.auth import login as _login
from django.contrib.auth import authenticate, logout as _logout
from django.contrib.auth.models import User
from board.models import *
from django.conf import settings
from datetime import datetime, timedelta
from django.http import HttpResponse, JsonResponse
from django.utils import dateparse
# Create your views here.

API_ENDPOINT = 'https://discord.com/api/v8'
CLIENT_ID = ''
CLIENT_SECRET = ''
REDIRECT_URI = 'http://127.0.0.1:8000/login/'

def exchange_code(code):
  data = {
    'client_id': CLIENT_ID,
    'client_secret': CLIENT_SECRET,
    'grant_type': 'authorization_code',
    'code': code,
    'redirect_uri': REDIRECT_URI
  }
  headers = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  r = requests.post('%s/oauth2/token' % API_ENDPOINT, data=data, headers=headers)
  r.raise_for_status()
  return r.json()

def getUserData(token_type, access_token):
    headers = {
        'Authorization': '{0} {1}'.format(token_type, access_token),
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    r = requests.get('{0}/users/@me'.format(API_ENDPOINT), headers=headers)
    r.raise_for_status()
    return r.json()

def parseInt(value):
    try:
        return int(value)
    except ValueError:
        return value

def isInt(value):
    if isinstance(value, int):
        return True
    else:
        return False

def home(request):
    if request.user.is_authenticated and request.user.userProfile.myChar.name != '':
        today = datetime.now() 
        myWars = Member.objects.filter(character=request.user.userProfile.myChar, war__dateStart__gt=today)
        return render(request, 'home.html', context={'myWars':myWars})
    elif not request.user.is_authenticated:
        return render(request, 'home.html')
    else:
        return redirect('character')

def characterValidate(name, level, faction, guild):
    valid = True
    if len(name) > 32:
        valid = False
    if not isInt(level) or level > 60:
        valid = False
    if not isInt(faction) or faction > 3:
        valid = False
    if len(guild) > 64:
        valid = False
    return valid

def character(request):
    if request.user.is_authenticated:
        if request.method == "POST":
            char = Character.objects.filter(profile_id=request.user.userProfile.id)
            _name = request.POST.get("charName")
            _level = parseInt(request.POST.get("level"))
            _faction = parseInt(request.POST.get("faction"))
            _guild = request.POST.get("guildName")
            valid = characterValidate(_name, _level, _faction, _guild)
            if char.exists() and characterValidate(_name, _level, _faction, _guild):
                #edit
                char = char.first()
                char.name = _name
                char.level = _level
                char.faction = Faction.objects.get(id=_faction)
                char.guild = _guild
                char.save()
            else:
                #create
                if characterValidate(_name, _level, _faction, _guild):
                    char = Character()
                    char.name = _name
                    char.level = _level
                    char.faction = Faction.objects.get(id=_faction)
                    char.guild = _guild
                    char.save()
        factions = Faction.objects.all()
        char = Character.objects.filter(profile_id=request.user.userProfile.id)
        if char.exists():
            myChar = char.first()
        return render(request, 'character.html', context={'char':myChar, 'factions':factions})
    else:
        return redirect('home')

def warValidate(warName, faction, date):
    valid = True
    if not isInt(faction) or faction > 3:
        valid = False
    if len(warName) > 256:
        valid = False
    if not isinstance(date, datetime):
        valid = False
    return valid 

def createWar(request):
    if request.method == "POST" and request.user.is_authenticated and request.user.userProfile.myChar.name != '':
        _warName = request.POST.get("warName")
        _faction = parseInt(request.POST.get("faction"))
        _date = request.POST.get("warStart")
        _date = dateparse.parse_datetime(_date)
        if warValidate(_warName, _faction, _date):
            newWar = War()
            newWar.creator = User.objects.get(id=request.user.id)
            newWar.warName = _warName
            newWar.faction = Faction.objects.get(id=_faction)
            newWar.dateStart = _date
            newWar.save()
            return redirect('war', warName=newWar.name)
        else:
            return redirect('createWar')
    elif request.user.userProfile.myChar.name == '':
        return redirect('character')
    else:
        factions = Faction.objects.all()
        isInLimit = War.objects.filter(creator=request.user, created_at=datetime.now()).count()
        return render(request, 'createWar.html', context={'isInLimit':isInLimit, 'factions':factions})

def setNullIfEmpty(requestData):
    if requestData == None:
        return 0
    else:
        return requestData

def armorsFilter(armors):
    armor = []
    for a in armors:
        if a != None:
            armor.append(a)
    return armor

def warAutoCreate(request, warName):
    thisWar = War.objects.filter(name=warName)
    if thisWar.exists() and request.user.is_authenticated:
        thisWar = thisWar.first()
        if thisWar.creator == request.user:
            _tank = parseInt(setNullIfEmpty(request.GET.get("tanks")))
            _healer = parseInt(setNullIfEmpty(request.GET.get("healers")))
            _rdps = parseInt(setNullIfEmpty(request.GET.get("rdps")))
            _mdps = parseInt(setNullIfEmpty(request.GET.get("mdps")))
            tanks = Member.objects.filter(war_id=thisWar.id, weapon1_id=1, status=True).order_by("gs")[:_tank]
            healers = Member.objects.filter(war_id=thisWar.id, weapon1_id=10, status=True).order_by("gs")[:_healer]
            rangeDPS = Member.objects.filter(war_id=thisWar.id, weapon1_id__in=RANGE_WEAPONS, status=True).order_by("gs")[:_rdps]
            meleeDPS = Member.objects.filter(war_id=thisWar.id, weapon1_id__in=MELEE_WEAPONS, status=True).order_by("gs")[:_mdps]
            return render(request, 'warauto.html', context={
            'warName':warName,
            'tanks': tanks,
            'healers': healers,
            'rangeDPS': rangeDPS,
            'meleeDPS': meleeDPS,
            'isOwner': True,
            })
        else:
            return redirect('home')
    else:
        return redirect('home')

def armorType(typeId):
    if typeId == 1:
        return "Light"
    elif typeId == 2:
        return "Medium"
    elif typeId == 3:
        return "Heavy"
    else:
        return "()"

def newMemberValidate(position, gs, weapon1, weapon2, armorWeight):
    valid = True
    if not isInt(position):
        valid = False
    if not isInt(gs) or int(gs) > 600:
        valid = False
    if not isInt(weapon1):
        valid = False
    if not isInt(weapon2):
        valid = False
    if not isInt(armorWeight):
        valid = False
    return valid

MELEE_WEAPONS = [2, 3, 4, 5, 6]
RANGE_WEAPONS = [7, 8, 9, 11, 12]

def war(request, warName):
    thisWar = War.objects.filter(name=warName)
    if thisWar.exists():
        thisWar = thisWar.first()
        if request.method == "POST" and request.user.is_authenticated:
            if not Member.objects.filter(war=thisWar, character=request.user.userProfile.myChar).exists():
                _pos = parseInt(request.POST.get("position"))
                _gs = parseInt(request.POST.get("gs"))
                _weap1 = parseInt(request.POST.get("weapon1"))
                _weap2 = parseInt(request.POST.get("weapon2"))
                _armor = parseInt(request.POST.get("armor"))
                if newMemberValidate(_pos, _gs, _weap1, _weap2, _armor):
                    newMember = Member()
                    newMember.position = _pos
                    newMember.gs = _gs
                    newMember.weapon1 = Weapon.objects.get(id=_weap1)
                    newMember.weapon2 = Weapon.objects.get(id=_weap2)
                    newMember.armorWeight = _armor
                    newMember.character = request.user.userProfile.myChar
                    newMember.war = thisWar
                    newMember.status = True
                    newMember.save()
        singUpChecker = True
        isOwner = False
        weapons = Weapon.objects.all()
        if request.user.is_authenticated:
            me = Member.objects.filter(war_id=thisWar.id, character=request.user.userProfile.myChar).exists()
            if me:
                singUpChecker = False
            if thisWar.creator == request.user:
                isOwner = True
        tanks = Member.objects.filter(war_id=thisWar.id, weapon1_id=1, status=True)
        healers = Member.objects.filter(war_id=thisWar.id, weapon1_id=10, status=True)
        rangeDPS = Member.objects.filter(war_id=thisWar.id, weapon1_id__in=RANGE_WEAPONS, status=True)
        meleeDPS = Member.objects.filter(war_id=thisWar.id, weapon1_id__in=MELEE_WEAPONS, status=True)
        kicked = Member.objects.filter(war_id=thisWar.id, status=False)
        return render(request, 'war.html', context={
            'warName': warName,
            'tanks':tanks,
            'healers':healers,
            'rangeDPS':rangeDPS,
            'meleeDPS':meleeDPS,
            'kicked':kicked,
            'singUpChecker':singUpChecker,
            'isOwner':isOwner,
            'weapons':weapons
            })
    else:
        return redirect('home')

def login(request):

    code = request.GET.get("code")
    user = exchange_code(code)
    userData = getUserData(user['token_type'], user['access_token'])
    if userData != None:
        if not Profile.objects.filter(userDiscordID=userData['id']).exists():
            userName = userData['username'] + userData['discriminator']
            newUser = User()
            newUser.username = userName
            newUser.save()

            profile = Profile()
            profile.user = newUser
            profile.userDiscordID = userData['id']
            profile.userName = userData['username']
            profile.tag = userData['discriminator']
            profile.locale = userData['locale']
            profile.save()

            blankChar = Character()
            blankChar.profile = profile
            blankChar.level = 0
            blankChar.faction = Faction.objects.get(id=1)
            blankChar.save()
            _login(request, newUser)
        else:
            profile = Profile.objects.get(userDiscordID=userData['id'])
            _login(request, profile.user)

    return redirect('home')

def logout(request):
    _logout(request)
    return redirect('home')

def checkWarOwner(name, me):
    check = War.objects.filter(name=name, creator_id=me).exists()
    if check:
        return True
    else:
        return False

def ajaxKick(request):
    if request.user.is_authenticated:
        name = request.POST.get("name")
        if checkWarOwner(name, request.user):
            id = request.POST.get("id")
            member = Member.objects.get(id=id)
            member.status = False
            member.save()
    return JsonResponse({'status':'200'})

def ajaxReturn(request): 
    if request.user.is_authenticated:
        name = request.POST.get("name")
        if checkWarOwner(name, request.user):
            id = request.POST.get("id")
            member = Member.objects.get(id=id)
            member.status = True
            member.save()
    return JsonResponse({'status':'200'})