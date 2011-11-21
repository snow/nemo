from django.db import models
from django.contrib.auth.models import User as Account

# Create your models here.
class User(models.Model):
    account = models.ForeignKey(Account, unique=True) 

class Wish(models.Model):
    content = models.CharField(max_length=200)
    author = models.ForeignKey(User)
    created = models.DateTimeField(auto_now_add=True)
    #duedate = models.DateTimeField(null=True, blank=True, auto_now_add=True)

    ayes = models.ManyToManyField(User, related_name='likes')
    negatives = models.ManyToManyField(User, related_name='bans')