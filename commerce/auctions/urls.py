from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("createListing", views.createListing, name="createListing"),
    path("listing/<str:item_name>", views.listing, name="listing"),
    path("add_watchlist/<str:item_name>", views.add_watchlist, name="add_watchlist"),
    path("watchList", views.watchlist, name="watchlist"),
    path("bidding/<str:item_name>", views.bidding, name="bidding"),
    path("close/<str:item_name>", views.close, name="close"),
    path("comment/<str:item_name>", views.comment, name="comment"),
    path("categories", views.categories, name="categories"),
    path("auctionCategories/<str:category>", views.auctionCategories, name="auctionCategories")
]
