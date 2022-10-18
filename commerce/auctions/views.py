from decimal import Decimal
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.db.models import Max
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django import forms

from .models import User, AuctionListing, Bids, Comments, WatchList


def index(request):
    return render(request, "auctions/index.html", {
        "listing": AuctionListing.objects.all()
    })

class NewTaskForm(forms.Form):
    item_name = forms.CharField(label="Item Name", max_length = 200, required = True, widget=forms.TextInput(attrs={'size': '160px'}))
    item_description = forms.CharField(label="Item Description", max_length = 200, required = True,  widget=forms.TextInput(attrs={'size': '160px'}))
    item_price = forms.DecimalField(label="Item Price",  decimal_places = 2, required = True,  widget=forms.TextInput(attrs={'size': '160px'}))
    item_category = forms.CharField(label="Category (Optional)", required = False, widget=forms.TextInput(attrs={'size': '160px'}))
    item_URL = forms.CharField(label="Image URL (Optional)", required = False, widget=forms.TextInput(attrs={'size': '160px'}))


def createListing(request):
    message = None
    if request.method == "POST":
        form = NewTaskForm(request.POST)
        if form.is_valid():
            item_name = form.cleaned_data["item_name"]
            item_description = form.cleaned_data["item_description"]
            item_price = form.cleaned_data["item_price"]
            item_category = form.cleaned_data["item_category"]
            item_URL = form.cleaned_data["item_URL"]

            # add new item into the database
            newauction = AuctionListing(item_name = item_name, item_description = item_description, 
                                        item_price = item_price, item_category = item_category, item_URL = item_URL, item_owner = request.user)
            newauction.save()
            message = "Submited the Auction Listing!"
            form = NewTaskForm(request.POST) # clear form once submitted
        return render(request, "auctions/create.html", {
            "forms" : form,
            "message" : message
        })
    return render(request, "auctions/create.html", {
        "forms" : NewTaskForm()
    })

def listing(request, item_name, message=None, comments = None):
    auction_item = AuctionListing.objects.get(item_name = item_name)
    highest_bid = Bids.objects.all().filter(bid_auction = auction_item).aggregate(Max("bid"))['bid__max']
    if highest_bid:
        highest_bid = round(highest_bid, 2)
    return render(request, "auctions/listing.html", {
        "item" : auction_item,
        "highest_bid": highest_bid,
        "message": message,
        "comments" : comments
    })

def add_watchlist(request, item_name):
    auction_item = AuctionListing.objects.get(item_name = item_name)
    watchlist = WatchList.objects.get(watchlist_user=request.user)
    if auction_item in watchlist.watchlist_auction.all():
        watchlist.watchlist_auction.remove(auction_item)
        watchlist.save()
        message = "{} is removed from Watchlist!".format(item_name)
    else:
        watchlist.watchlist_auction.add(auction_item)
        watchlist.save()
        message = "{} is added to Watchlist!".format(item_name)
    return listing(request, item_name, message, comments = None)


def watchlist(request):
    watchlist = WatchList.objects.get(watchlist_user=request.user)
    auction_items = watchlist.watchlist_auction.all()
    return render(request, "auctions/watchlist.html", {
        "items" : auction_items
    })

def bidding(request, item_name):
    message = None
    if request.method == "POST":
        bidding_amount = (request.POST.get("bidding"))
        
        # ensure that form is valid
        if bidding_amount == '':
            message = "Error: Plase key in the amount you want to bid for !"
        else:
            bidding_amount = float(bidding_amount)
            auction_item = AuctionListing.objects.get(item_name = item_name)
            max_bid = Bids.objects.all().filter(bid_auction = auction_item).aggregate(Max("bid"))['bid__max']
            # comparing new and current bid based on 2 decimal points
            if max_bid:
                if round(bidding_amount, 2) > round(max_bid, 2):
                    # add new bidding into the database
                    newbidding = Bids(bid_auction = auction_item, bid_user = request.user, bid = bidding_amount)
                    newbidding.save()
                    message = "Submited the bidding for " + item_name + "!"
                else:
                    message = "Error: The bidding amount has to be larger than current bidding amount of $" + str(round(max_bid, 2)) + "!"
            elif round(bidding_amount, 2) > round(auction_item.item_price, 2):
                    # add new bidding into the database
                    newbidding = Bids(bid_auction = auction_item, bid_user = request.user, bid = bidding_amount)
                    newbidding.save()
                    message = "Submited the bidding for " + item_name + "!"
            else:
                message = "Error: The bidding amount has to be larger than current bidding amount of " + auction_item.item_price + "!"

    return listing(request, item_name, message, comments = None)

def close(request, item_name):
    message = None
    auction_item = AuctionListing.objects.get(item_name = item_name)
    max_bid = Bids.objects.all().filter(bid_auction = auction_item).aggregate(Max("bid"))['bid__max']
    if max_bid:
        winner = Bids.objects.get(bid_auction = auction_item, bid = max_bid).bid_user
    else:
        winner = auction_item.item_owner
    auction_item.item_exist = False
    auction_item.item_winner = winner

    auction_item.save()
    return listing(request, item_name, message, comments = None)

def comment(request, item_name):
    message = None
    auction_item = AuctionListing.objects.get(item_name = item_name)
    
    if request.method == "POST":
        # add new comment into database
        item_comments = request.POST.get("item_comment")
        f = Comments(comment_auction = auction_item, comment_user = request.user, comment = item_comments)
        f.save()
        message = "Your comment has been submitted"
    
    comments = Comments.objects.filter(comment_auction = auction_item).all()
    return listing(request, item_name, message, comments)

def categories(request):
    allcategories = {}
    for item in AuctionListing.objects.all():
        if item.item_category not in allcategories.keys():
            allcategories[item.item_category] = [item.item_name]
        else:
            allcategories[item.item_category].append(item.item_name)

    return render(request, "auctions/categories.html", {
        "allcategories" : allcategories.keys()
    })

def auctionCategories(request, category):
    allcategories = {}
    for item in AuctionListing.objects.all():
        if item.item_category not in allcategories.keys():
            allcategories[item.item_category] = [item]
        else:
            allcategories[item.item_category].append(item)
    
    auction_items = allcategories[category]

    return render(request, "auctions/auctionCategories.html", {
        "items" : auction_items,
        "category" : category
    })



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
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
            watchlist = WatchList(watchlist_user = user)
            watchlist.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")


