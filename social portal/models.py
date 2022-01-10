from django.db import models
from django.db.models.deletion import CASCADE, DO_NOTHING
from django.db.models.expressions import Case
from django.db.models.indexes import Index
from datetime import date, datetime
from django.contrib import auth
from django.contrib.auth.models import User
from PIL import Image as img, ImageOps, ExifTags
import math, uuid

# Create your models here.
#from social.models import Images

class Profile(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete = models.CASCADE, related_name = 'userProfile')
    created_at = models.DateTimeField(auto_now_add = True)
    verified = models.BooleanField(default = False)
    activated = models.BooleanField(default=False)
    displayName = models.CharField(max_length=32)
    totalLikes = models.IntegerField(default=0)
    bonusPoints = models.IntegerField(default=0)

    def follows(self):
        followsCount = Follow.objects.filter(followed=self).count()
        return followsCount
        
    def totalLikesUpdate(self):
        likesCount = Like.objects.filter(liked=self).count()
        self.totalLikes = likesCount
        self.save()

    class Meta:
        indexes = [models.Index(fields=['-totalLikes',]), ]

    def __str__(self):
        return "id: {0} name: {1}".format(self.id, self.displayName)
    
    def checkPoints(self):
        if int(self.totalLikes / 100) != self.bonusPoints:
            self.bonusPoints = int(self.totalLikes / 100)
            self.save()

    def refflinkPoints(self, myIP):
        myReff = Refflink.objects.get(profile=self)
        reffs = UserInfo.objects.filter(ip=myIP, refflinkUsed=myReff).count()
        if reffs <= 10:
            self.bonusPoints += 1
            self.save()

class Category(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=32)

class Post(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=False)
    category = models.ForeignKey(Category, on_delete=DO_NOTHING, default=1)
    verified = models.BooleanField(default = False)
    owner = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='userProfile')
    tags = models.TextField(max_length=128, name='tags')
    
    def commentCount(self):
        return Comment.objects.filter(post=self).count()

    def getAll():
        return Post.objects.filter(is_active=True).order_by('-created_at')

    def getFirstPhoto(self):
        return Photo.objects.get(post=self.id, isFirstPhoto=True)

    def likesCount(self):
        return Like.objects.filter(post=self, likeStatus=True).count()

    def tagsList(self):
        try:
            return eval(self.tags)
        except:
            return None
    def __str__(self):
        return "ID: {0}, TotalLikes: {1}, TotalComments: {2}".format(self.id, self.likesCount(), self.commentCount())
    
    def getProfileDisplayName(self):
        return self.owner.displayName
    
    def deactivate(self):
        self.is_active = False
        self.save()

    def activate(self):
        self.is_active = True
        self.save()

def user_directory_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.post.owner.id, filename)

class Photo(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, default=None, on_delete=CASCADE)
    isFirstPhoto = models.BooleanField(default=False)
    image = models.FileField(upload_to=user_directory_path)

    def save(self, *args, **kwargs):
        instance = super(Photo, self).save(*args, **kwargs)
        _img = img.open(self.image.path)
        _img = ImageOps.exif_transpose(_img)
        _img.save(self.image.path, quality=30)
        return instance

class LoginAntyBruteForce(models.Model):
    id = models.AutoField(primary_key=True)
    ip = models.CharField(max_length=20)
    lastTry = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False) #True if banned 
    attempts = models.IntegerField(default=0)

    def __str__(self):
        statusText = ""
        if self.status:
            statusText = "Banned"
        else:
            statusText = "Unbanned"
        return  "IP: {0}, attempts: ({1}), Last Try: {2}, Status: {3}".format(self.ip, self.attempts, self.lastTry, statusText)

    def minutesAgo(self):
        now = datetime.now()
        nowTimestamp = datetime.timestamp(now)
        timestamp = datetime.timestamp(self.lastTry)
        ago = nowTimestamp - timestamp
        ago = int(ago) / 60
        ago = math.floor(ago)
        return ago

class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='to_post')
    context = models.CharField(max_length=256)
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE)

class Like(models.Model):
    id = models.AutoField(primary_key=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='for_post')
    liked = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='like_profile')
    whoLiked = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='liker_profile')
    created_at = models.DateTimeField(auto_now_add=True)
    likeStatus = models.BooleanField(default=True)    

    def __str__(self):
        return "User: {0} liked current status is {1}".format(self.profile, self.likeStatus)

    def save(self, *args, **kwargs):
        instance = super(Like, self).save(*args, **kwargs)
        self.liked.totalLikesUpdate()
        return instance

class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    followed = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followed')
    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='follower')
    followed_at = models.DateTimeField(auto_now_add=True)
    isFollowed = models.BooleanField(default=True)

    def followAge(self):
        today = datetime.now()
        diff = today - self.followed_at
        return "{0} days ago".format(diff.days)

class Refflink(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.DO_NOTHING) 
    code = models.UUIDField(default=uuid.uuid4, editable=False)
    used = models.IntegerField(default=0)

    def __str__(self):
        return "Profile: {0} with code: {1} used: {2} times".format(self.profile, self.code, self.used)

def code6():
    return uuid.uuid4().hex.upper()[0:6]

class ActivateCode(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=models.DO_NOTHING) 
    code = models.CharField(default=code6, editable=False, max_length=6)

    def __str__(self):
        return "Activation code for profile {0} is {1}".format(self.profile, self.code)

class UserInfo(models.Model):
    id = models.AutoField(primary_key=True)
    profile = models.ForeignKey(Profile, on_delete=DO_NOTHING, related_name='accountCreatedDetails')
    refflinkUsed = models.ForeignKey(Refflink, on_delete=DO_NOTHING, null=True, blank=True)
    ip = models.GenericIPAddressField()

    def __str__(self):
        return "Created from IP: {0} used refflink {1}".format(self.ip, self.refflinkUsed)

class ReportType(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64) # 1. post / 2. comment / 3. user

class Report(models.Model):
    id = models.AutoField(primary_key=True)
    chcecked = models.BooleanField(default=False) # checkin when reacted on it
    type = models.ForeignKey(ReportType, on_delete=models.DO_NOTHING, related_name='reportType')
    reason = models.CharField(max_length=64) # values separated by "," ex. reason:'1,2,3,4,5'
    targetID = models.BigIntegerField()
    