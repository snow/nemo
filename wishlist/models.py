from django.db import models
from django.contrib.auth.models import User

class UserProfileManager(models.Manager):
    '''TODO'''
    def get_by_user(self, user):
        try:
            up = self.get_query_set().get(user=user)
        except self.model.DoesNotExist:        
            up = self.model()
            up.user = user
            up.save()
            
        return up

# Create your models here.
class UserProfile(models.Model):
    user = models.ForeignKey(User, unique=True)
    vote_limit = 10
    
    objects = UserProfileManager()
    
    def username(self):
        return self.user.username
    
    def vote_left(self):
        return self.vote_limit - \
            sum([abs(vote.count) 
                 for vote in Vote.objects.filter(user_profile=self)])
            
    class OutOfVoteException(Exception):
        def __init__(self, has, want, origin):
            self.has = has
            self.want = want
            self.origin = origin
            
    def vote(self, wish, count):        
        try:
            vote = Vote.objects.filter(wish=wish, user_profile=self).get()
        except Vote.DoesNotExist:
            vote = Vote(wish=wish, user_profile=self)
            
        if (abs(count) - abs(vote.count)) > self.vote_left():
            raise self.OutOfVoteException(has=self.vote_left(), want=count, 
                                          origin=vote.count)
        vote.count = count
        vote.save()
        
        return count      
    
class WishManager(models.Manager):
    _queryset = None

    def _get_query_set(self):
        if None is self._queryset:
            self._queryset = super(WishManager, self).get_query_set()

        return self._queryset

    def _update_query_set(self, queryset):
        self._queryset = queryset

    def get_query_set(self):
        if None is self._queryset:
            return super(WishManager, self).get_query_set()
        else:
            tmp = self._queryset
            self._queryset = None
            return tmp

    def recent(self):
        self._update_query_set(self._get_query_set().order_by('-created'))
        return self

    def with_user(self, user):
        self.model.current_user = user
        return self
    
class Wish(models.Model):
    content = models.CharField(max_length=200)
    author = models.ForeignKey(UserProfile, related_name='wishes')
    created = models.DateTimeField(auto_now_add=True)
    #duedate = models.DateTimeField(null=True, blank=True, auto_now_add=True)
    STATUS_UNREAD = 0
    STATUS_READ = 1
    STATUS_ONGOING = 2
    STATUS_DONE = 3
    STATUSES = {
        STATUS_UNREAD: 'unread',
        STATUS_READ: 'read',
        STATUS_ONGOING: 'ongoing',
        STATUS_DONE: 'done'
    }
    
    status = models.SmallIntegerField(default=0, choices=STATUSES.items())
    response = models.CharField(max_length=200, blank=True)

    votes = models.ManyToManyField(UserProfile, through='Vote', 
                                  related_name='votes')
    
    objects = WishManager()
    
    class Meta:
        permissions = (
            ('response_wish', 'could response a wish'),
        )
    
    def count_ayes(self):
        return sum([ay.count for ay in Vote.ayes.filter(wish=self)])
    
    def count_user_ayes(self):
        up = UserProfile.objects.get_by_user(self.current_user)
        if self.current_user:
            return Vote.ayes.filter(wish=self, user_profile=up).get().count
        else:
            return 0
        
    def count_negatives(self):
        return abs(sum([negative.count 
                    for negative in Vote.negatives.filter(wish=self)]))
    
    def count_user_negatives(self):
        up = UserProfile.objects.get_by_user(self.current_user)
        if self.current_user:
            return abs(Vote.negatives.filter(wish=self, user_profile=up).\
                get().count)
        else:
            return 0
        
    def status_label(self):
        return self.STATUSES[self.status]

class AyManager(models.Manager):
    '''TODO'''
    def get_query_set(self):
        return super(AyManager, self).get_query_set().filter(count__gt=0)
    
class NegativeManager(models.Manager):
    '''TODO'''
    def get_query_set(self):
        return super(NegativeManager, self).get_query_set().filter(count__lt=0)    
    
class Vote(models.Model):
    user_profile = models.ForeignKey(UserProfile)
    wish = models.ForeignKey(Wish)
    count = models.SmallIntegerField(default=0,
                                     choices=[(i, i) for i in range(-3, 4)])
    updated = models.DateTimeField(auto_now=True)
    
    objects = models.Manager()
    ayes = AyManager()
    negatives = NegativeManager()