from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.fields import BigIntegerField
import math, uuid
from django.contrib.auth.models import User
# Create your models here.

class Faction(models.Model):
    name = models.CharField(max_length = 32)

class Weapon(models.Model):
    name = models.CharField(max_length = 64)

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'userProfile')
    userDiscordID = models.BigIntegerField()
    userName = models.CharField(max_length = 128)
    tag = models.CharField(max_length = 16)
    locale = models.CharField(max_length = 8)

class Character(models.Model):
    profile = models.OneToOneField(Profile, on_delete = models.CASCADE, related_name = 'myChar')
    name = models.CharField(max_length = 32)
    level = models.IntegerField()
    faction = models.ForeignKey(Faction, on_delete = models.DO_NOTHING)
    guild = models.CharField(max_length = 64)

class War(models.Model):
    name =  models.UUIDField(default = uuid.uuid4, unique = True) #/link -> url /war/id/{name}
    created_at = models.DateField(auto_now = True)
    dateStart = models.DateTimeField()
    creator = models.ForeignKey(User, on_delete = models.CASCADE)
    warName = models.CharField(max_length = 256, default = 'war')
    faction = models.ForeignKey(Faction, on_delete = models.DO_NOTHING)
    warStatus = models.BooleanField(default = True) #true = OPEN / false ended

class Member(models.Model):
    war = models.ForeignKey(War, on_delete = models.CASCADE)
    created_at = models.DateField(auto_now = True)
    character = models.ForeignKey(Character, on_delete = models.CASCADE)
    status = models.BooleanField(default = True) #False = Kicked
    position = models.IntegerField() #on the war board
    gs = models.IntegerField()
    weapon1 = models.ForeignKey(Weapon, on_delete = models.CASCADE, related_name = 'weapon_primary')
    weapon2 = models.ForeignKey(Weapon, on_delete = models.CASCADE, related_name = 'weapon_secondary')
    armorWeight = models.IntegerField()
