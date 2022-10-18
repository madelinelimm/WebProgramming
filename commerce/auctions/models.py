from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass

class AuctionListing(models.Model):
    item_name = models.CharField(max_length = 200)
    item_description = models.CharField(max_length = 300)
    item_price = models.DecimalField(max_digits = 10, decimal_places=2)
    item_category = models.CharField(max_length = 200)
    item_URL = models.URLField(max_length = 200, blank = True)
    item_owner = models.ForeignKey(User, null = True, blank = True, on_delete = models.CASCADE, related_name = "owner")
    item_winner = models.ForeignKey(User, null = True, blank = True, on_delete = models.CASCADE, related_name = "winner")
    item_exist = models.BooleanField(max_length = 20, default = True)
    
    def __str__(self):
        return f"{self.id}: {self.item_name} ({self.item_category})"

class Bids(models.Model):
    bid_auction = models.ForeignKey(AuctionListing, on_delete = models.CASCADE, related_name = "bid_auction")
    bid_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "bidder")
    bid = models.DecimalField(max_digits = 10, decimal_places=2)

    def __str__(self):
        return f"{self.id}: {self.bid_user} bid {self.bid} on {self.bid_auction}"
    

class Comments(models.Model):
    comment_auction = models.ForeignKey(AuctionListing, on_delete = models.CASCADE, related_name = "comment_auction")
    comment_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "commenter")
    comment = models.CharField(max_length = 200)
    
    def __str__(self):
        return f"{self.id}: {self.comment_user} commented {self.comment} on {self.comment_auction}"

class WatchList(models.Model):
    watchlist_user = models.ForeignKey(User, on_delete = models.CASCADE, related_name = "watcher")
    watchlist_auction = models.ManyToManyField(AuctionListing, blank = True, related_name = "watch_auction")
    
    def __str__(self):
        return f"{self.id}: {self.watchlist_user} watching {self.watchlist_auction}"