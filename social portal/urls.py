
from django.urls import path

from . import views, ajax, control
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/<str:profileName>', views.profile, name='profile'),
    path('profileid/<int:profileId>', views.profileById, name='profileById'),
    path('post/new', views.newPost, name='newPost'),
    path('post/id/<int:id>', views.postId, name='postId'),
    path('liked', views.liked, name='liked'),
    path('followed', views.followed, name='followed'),
    path('ranking', views.ranking, name='ranking'),
    path('support', views.support, name='support'),
    path('contact', views.contact, name='contact'),
    path('changes', views.changes, name='changes'),
    path('report/<str:_type>/<str:targetID>', views.report, name='report'),
    path('login', views.login, name='login'),
    path('loginValidate', views.loginValidate, name='loginValidate'),
    path('registerValidate', views.registerValidate, name='registerValidate'),
    path('logout', views.logout, name='logout'),
    path('uploadImage', views.uploadImage, name='uploadImage'),
    path('refflink/<str:code>', views.refflinkView, name='refflink'),
    path('activate', views.activateView, name='activateView'),

    #this block is restricted only for admins
    path('manage/post/<int:id>', control.postManage, name='postManage'),
    path('manage/comment/<int:id>', control.commentManage, name='commentManage'),
    path('manage/user/<int:id>', control.userManage, name='userManage'),
    
    #ajax
    path('comment', ajax.comment, name='comment'),
    path('like', ajax.like, name='like'),
    path('follow', ajax.follow, name='follow'),
    path('changeUsername', ajax.changeUsername, name='changeUsername'),
    path('activateAccount', ajax.activateAccount, name='activateAccount'),
    path('deletePost', ajax.deletePost, name='deletePost')


] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
