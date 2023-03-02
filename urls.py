from django.urls import path
from .views import *

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('setting', Setting.as_view(), name='setting'),
    path('uploads', Uploads.as_view(), name='uploads'),
    path('follow', Follow.as_view(), name='follow'),
    path('profile/<str:pk>', Profile.as_view(), name='profile'),
    path('like-post', Like_Post.as_view(), name='like-post'),
    path('signup', Signup.as_view(), name='signup'),
    path('signin', Signin.as_view(), name='signin'),
    path('logout', Logout.as_view(), name='logout'),
]
