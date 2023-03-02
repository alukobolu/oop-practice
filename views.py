from django.shortcuts import render, redirect
from django.contrib.auth.models import User, auth
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Profile, Post, LikePost, FollowersCount
from itertools import chain
import random
from django.views import View
# Create your views here.



class Index(View):
    @login_required(login_url='signin')
    def get(self,request):
        user_object = User.objects.get(username=request.user.username)
        user_profile = Profile.objects.get(user=user_object)

        user_following_list = []
        feed = []

        user_following = FollowersCount.objects.filter(follower=request.user.username)

        for users in user_following:
            user_following_list.append(users.user)

        for usernames in user_following_list:
            feed_lists = Post.objects.filter(user=usernames)
            feed.append(feed_lists)

        feed_list = list(chain(*feed))

        # user suggestion starts
        all_users  = User.objects.all()
        user_following_all = []

        for user in user_following:
            user_list = User.objects.get(username=user.user)
            user_following_all.append(user_list)

        new_suggestions_list = [x for x in list(all_users)if (x not in list(user_following_all))]
        current_user = User.objects.filter(username=request.user.username)
        final_suggestions_list = [x for x in list(new_suggestions_list) if(x not in list(current_user))]
        random.shuffle(final_suggestions_list)

        username_profile = []
        username_profile_list = []

        for users in final_suggestions_list:
            username_profile.append(users.id)

        for ids in username_profile:
            profile_lists = Profile.objects.filter(id_user=ids)
            username_profile_list.append(profile_lists)

        suggestions_username_profile_list = list(chain(*username_profile_list))

        posts = Post.objects.all()
        return render(request, 'MediaApp/index.html', {'user_profile': user_profile, 'posts': feed_list,'suggestions_username_profile_list': suggestions_username_profile_list[:4] })

class PostClass:
    def __init__(self,request):
        self.username = request.user.username
        self.request = request

    def act(self):
        raise NotImplementedError("There is no act for this !!!")

class Post_a_Post(PostClass):
    def act(self):
        image = self.request.FILES.get("image_upload")
        caption = self.request.POST["caption"]

        new_post = Post.objects.create(user=self.username, image=image, caption=caption)
        new_post.save()

class Like_a_Post(PostClass):
    def act(self):
        post_id = self.request.GET.get('post_id')

        post = Post.objects.get(id=post_id)

        like_filter = LikePost.objects.filter(
            post_id=post_id, username=self.username).first()

        if like_filter == None:
            new_like = LikePost.objects.create(post_id=post_id, username=self.username)
            new_like.save()
            post.no_of_likes = post.no_of_likes+1
            post.save()
        else:
            like_filter.delete()
            post.no_of_likes = post.no_of_likes-1
            post.save()
            

def operator(operate):
    operate.act()


class Uploads(View):

    @login_required(login_url='signin')
    def post(self,request):
        act = Post_a_Post(request)
        operator(act)
        return redirect('/')
    
    @login_required(login_url='signin')
    def get(self,request):
        return redirect('/')


class Like_Post(View):
    @login_required(login_url='signin')
    def get(self,request):
        act = Like_a_Post(request)
        operator(act)
        return redirect('/')


class Profile(View):
    @login_required(login_url='signin')
    def get(self,request, pk):
        user_object = User.objects.get(username=pk)
        user_profile = Profile.objects.get(user=user_object)
        user_posts = Post.objects.filter(user=pk)
        user_post_length = len(user_posts)

        follower = request.user.username
        user = pk

        if FollowersCount.objects.filter(follower = follower, user=user).first():
            button_text = 'Unfollow'
        else:
            button_text = 'Follow'

        user_followers = len(FollowersCount.objects.filter(user=pk))
        user_following = len(FollowersCount.objects.filter(follower=pk))

        context = {
            'user_object': user_object,
            'user_profile': user_profile,
            'user_posts': user_posts,
            'user_post_length': user_post_length,
            'button_text': button_text,
            'user_followers': user_followers,
            'user_following': user_following
        }
        return render(request, 'MediaApp/profile.html', context )


class Follow(View):
    @login_required(login_url='signin')
    def post(self,request):
        follower = request.POST['follower']
        user = request.POST['user']

        if FollowersCount.objects.filter(follower=follower, user=user).first():
            delete_follower = FollowersCount.objects.get(follower=follower, user=user)
            delete_follower.delete()
            return redirect('/profile/'+user)
        else:
            new_follower = FollowersCount.objects.create(follower=follower, user=user)
            new_follower.save()
            return redirect('/profile/'+user)

    @login_required(login_url='signin')
    def get(self,request):
        return redirect('/')


class Setting(View):
    @login_required(login_url='signin')
    def post(self,request):
        user_profile = Profile.objects.get(user=request.user)
        if request.FILES.get('image') == None:
            image = user_profile.profileImg
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileImg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            messages.info(request, 'Profile updated Successfully!')
        if request.FILES.get('image') != None:
            image = request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileImg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
            messages.info(request, 'Profile updated Successfully!')
        return redirect('setting')
    @login_required(login_url='signin')
    def get(self,request):
        user_profile = Profile.objects.get(user=request.user)
        return render(request, 'MediaApp/setting.html', {'user_profile': user_profile})

class UserClass:
    def __init__(self,request):
        self.__username = request.POST['username']
        self.__password = request.POST['password']

    def getter(self):
        return self.__username,self.__password

class Signin(View):
    def post(self,request):
        credencials = UserClass(request)
        username,password = credencials.getter()
        if username == '' or password == '':
            messages.info(request, 'Fields cannot be empty')
            return redirect('signin')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            messages.info(request, 'Invalid Login credentials!')
            return redirect('signin')

    def get(self,request):
        return render(request, 'MediaApp/signin.html')

class Signup(View):
    def post(self,request):
        credencials = UserClass(request)
        username,password = credencials.getter()
        confirmPassword = request.POST['confirmPassword']
        if username == "" or password == "" or confirmPassword == "":
            messages.info(request, 'Fields cannot be left empty!')
            return redirect('signup')

        if password == confirmPassword:
            if User.objects.filter(username=username).exists():
                messages.info(request, 'Username already exist!')
                return redirect('signup')
            else:
                user = User.objects.create_user(
                    username=username, password=password)
                user.save()
                # log user in and redirect to setting page
                user_login = auth.authenticate(
                    username=username, password=password)
                auth.login(request, user_login)

                # create a profile object for the new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(
                    user=user_model, id_user=user_model.id)
                new_profile.save()
                return redirect('setting')
        else:
            messages.info(request, 'Password does not Match!')
            return redirect('signup')

    def get(self,request):
        return render(request, 'MediaApp/signup.html')

class Logout(View):
    @login_required(login_url='signin')
    def post(self,request):
        auth.logout(request)
        return redirect('signin')
