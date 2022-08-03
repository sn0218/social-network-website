from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
import json

from network.forms import NewPostForm
from django.core.paginator import Paginator
from .models import User, Post, Comment, Like, Following
from itertools import chain


def index(request):
    # check the request method is GET
    if request.method == "GET":
        # get the page request user
        user = request.user
        
        # get all posts
        posts = Post.objects.order_by('-date').all()

        liked_posts= []
        
        # get all liked posts by logged user
        if user.is_authenticated:
            likes = Like.objects.filter(user=user).all()
            liked_posts = [like.post for like in likes]

        # create paginator
        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "network/index.html", {
            "user": user,
            "postForm": NewPostForm(),
            "posts": posts,
            "page_obj": page_obj,
            "liked_posts": liked_posts
        })


def profile(request, name):
    if request.method == "GET":
        # get the page request user
        user = request.user

        # get the user info for profile page
        profile_user = User.objects.get(username=name)

        # get all posts belong to the user
        posts = profile_user.user_post.order_by('-date').all()

        # get post count
        post_count = profile_user.user_post.count()

        # get follower count
        follower_count = profile_user.follower.count()

        # get following count
        following_count = profile_user.following.count()

        # validate if the login user follows the profile user 
        is_following = False

        liked_posts= []

        if user.is_authenticated:
            # get all the liked posts by the logged user
            likes = Like.objects.filter(user=user).all()
            liked_posts = [like.post for like in likes]

            if Following.objects.filter(user=user, followed_user=profile_user).exists():
                is_following = True
                
            
        # create paginator
        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    return render(request, "network/profile.html", {
        "user": user,
        "profile_user": profile_user,
        "posts": posts,
        "page_obj": page_obj,
        "post_count" : post_count,
        "follower_count": follower_count,
        "following_count": following_count,
        "is_following": is_following,
        "liked_posts": liked_posts
    })


@login_required(login_url="login")
def following(request):
    # check the request method is GET
    if request.method == "GET":
        # get the page request user
        user = request.user

        # get the current user object from database
        current_user = User.objects.get(pk=user.id)

        # get all posts that current user follow
        posts = [following.followed_user.user_post.order_by('-date').all() for following in current_user.following.all()]
        
        # flatten the 2d structure of posts obtaining from multiple users and sort the post in reverse chronological order
        posts = list(sorted(chain(*posts), key=lambda post: post.date, reverse=True))

        liked_posts= []
        
        # get all liked posts by logged user
        if user.is_authenticated:
            likes = Like.objects.filter(user=user).all()
            liked_posts = [like.post for like in likes]
        

        # create paginator
        paginator = Paginator(posts, 10) 
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, "network/following.html", {
            "user": user,
            "posts": posts,
            "page_obj": page_obj,
            "liked_posts": liked_posts
        }) 


""" API routes """
# API route for like count
@csrf_exempt
def likeCount(request, post_id):
    # get the post object from database
    post = Post.objects.get(pk=post_id)

    # get like count
    like_count = post.post_like.count()
    
    return JsonResponse({
        "post_id": post.id,
        "like_count": like_count
    })



# API route for like
@csrf_exempt
def like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})
    
    # get the requsted user
    user = request.user

    # get the post object from database
    post = Post.objects.get(pk=post_id)

    # get the json data from POST request
    data = json.loads(request.body)

    # retrieve the like boolean value, if like is true
    if data.get("like", ""):
        like = Like(
            user = user,
            post = post
        )
        like.save()
        return JsonResponse({"message": "Like action is executed sucessfully."}, status=201)

    # if like is false => unlike
    else:
        likeRecord = Like.objects.filter(user=user, post=post)
        likeRecord.delete()
        return JsonResponse({"message": "Unlike action is executed sucessfully."}, status=201)


# API route for follower count
def followerCount(request, name):
    # get the user info for profile page
    profile_user = User.objects.get(username=name)

     # get follower count
    follower_count = profile_user.follower.count()

    return JsonResponse({
        "id": profile_user.id,
        "username": profile_user.username,
        "follower_count": follower_count
    })


# API route for following a user
@login_required(login_url="login")
def follow(request):
    # following a user must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})

    # get the json data from POST request
    data = json.loads(request.body)

    # get the requested user 
    user = request.user

    # retrieve the username of the followed_user and get the followed_user from database
    followed_username = data.get("followed_user", "")
    followed_user = User.objects.get(username=followed_username)

    if not user == followed_user:
        # save the retrieved data into model
        follow = Following(
            user = user,
            followed_user = followed_user
        )
        follow.save()
    
    else:
        return JsonResponse({"error": "You cannot follow yourself."}, status=403)

    return JsonResponse({"message": "Follow action is executed sucessfully."}, status=201)


# API route for unfollowing a user
@login_required(login_url="login")
def unfollow(request):
    # following a user must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required"})
    # get the requested user 
    user = request.user

    # get the json data from POST request
    data = json.loads(request.body)

    # retrieve the username of the unfollowed_user and get the unfollowed_user from database
    unfollowed_username = data.get("unfollowed_user", "")
    unfollowed_user = User.objects.get(username=unfollowed_username)

    # delete the record from database
    followingRecord = Following.objects.filter(user=user, followed_user=unfollowed_user)
    followingRecord.delete()

    return JsonResponse({"message": "Unfollow action is executed sucessfully."}, status=201)


# API route for sending a post
@csrf_exempt
@login_required(login_url="login")
def composePost(request):
    # Composing a new post must be via POST
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    
    # get the json data from POST request 
    data = json.loads(request.body)

    """ .get("sth", "") ==> 
        the 2nd arg is default value which is set empty if the key does not exist """
    # get the headline and content of the post from json data
    headline = data.get("headline", "")
    content = data.get("content", "")

    # save the retrieved data into model
    new_post = Post(
        user=request.user,
        headline=headline,
        content=content
    )
    new_post.save()

    return JsonResponse({"message": "Post saved sucessfully."}, status=201)


# API route for querying all posts
def getAllPosts(request):
    # get all the posts from database
    posts = Post.objects.order_by('-date').all()

    # return all posts in json format
    return JsonResponse([post.serialize() for post in posts], safe=False)


# API route for querying a single post
def getPost(request, post_id):
    # check the existence of the requesting post
    try:
        post = Post.objects.get(pk=post_id)
    except Post.DoesNotExist:
        return JsonResponse({"error": "The requested post does not exist."}, status=400)
    
    # check the request method is GET
    if request.method == "GET":
        # return the post in json format
        return JsonResponse(post.serialize())
    else:
        return JsonResponse({"error": "GET request required."}, status=400)


# API route for saving the edited post
@login_required(login_url="login")
def editPost(request, post_id):
    # check the existence of the requesting post and the requested user
    try:
        post = Post.objects.get(pk=post_id, user=request.user)
    except Post.DoesNotExist:
        return JsonResponse({"error": "The requested post does not exist."}, status=400)
    
    # check the request method is PUT
    if request.method != "PUT":
        return JsonResponse({"error": "PUT request required."})
    
    # get the json data from POST request 
    data = json.loads(request.body)

    # get the edited content of the post
    editedContent = data.get("content", "")

    # update the content of the post
    post.content = editedContent
    post.save()

    return JsonResponse({"message": "Post is edited sucessfully."}, status=201)


""" register, login and logout views """
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")



