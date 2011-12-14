from datetime import datetime

from django import forms
from django.db import models
from django.contrib.auth.models import User

class UserProfileManager(models.Manager):
    '''TODO'''
    def get_by_user(self, user):
        '''TODO'''
        try:
            up = self.get_query_set().get(user=user)
        except self.model.DoesNotExist:        
            up = self.model()
            up.user = user
            up.save()
            
        return up

# Create your models here.
class UserProfile(models.Model):
    '''TODO'''
    user = models.ForeignKey(User, unique=True, related_name='nemo_user_profile_set')
    VOTE_LIMIT = 10
    
    objects = UserProfileManager()
    
#    def username(self):
#        '''TODO'''
#        return self.user.username
    
    def votes_left(self):
        '''TODO'''
        return self.VOTE_LIMIT - \
            sum([abs(vote.count) 
                 for vote in Vote.objects.filter(user=self.user)])
            
    class OutOfVoteException(Exception):
        '''TODO'''
        def __init__(self, has, want, origin):
            self.has = has
            self.want = want
            self.origin = origin
            
    def vote(self, wish, count):  
        '''TODO'''      
        try:
            vote = Vote.objects.filter(wish=wish, user=self.user).get()
        except Vote.DoesNotExist:
            vote = Vote(wish=wish, user=self.user)
            
        if (abs(count) - abs(vote.count)) > self.votes_left():
            raise self.OutOfVoteException(has=self.votes_left(), want=count, 
                                          origin=vote.count)
        vote.count = count
        vote.save()
        
        wish.count_ayes()
        wish.count_negatives()
        wish.save()
        
        return count      
    
class WishManager(models.Manager):
    '''TODO'''
    _queryset = None

    def _get_query_set(self):
        '''TODO'''
        if None is self._queryset:
            self._queryset = super(WishManager, self).get_query_set()

        return self._queryset

    def _update_query_set(self, queryset):
        '''TODO'''
        self._queryset = queryset

    def get_query_set(self):
        '''TODO'''
        if None is self._queryset:
            return super(WishManager, self).get_query_set()
        else:
            tmp = self._queryset
            self._queryset = None
            return tmp

    def recent(self):
        '''TODO'''
        self._update_query_set(self._get_query_set().order_by('-created'))
        return self
    
    def top(self):
        '''TODO'''
        self._update_query_set(self._get_query_set().
            exclude(status__gte=Wish.STATUS_DONE).order_by('-ayes', 
                                                           'negatives',
                                                           '-created'))
        return self
    
    def hot(self):
        '''TODO'''
        self._update_query_set(self._get_query_set().
            exclude(status__gte=Wish.STATUS_DONE).order_by('-status', 
                                                           '-ayes',
                                                           'negatives',
                                                           '-created'))
        return self
        
    def done(self):
        '''TODO'''
        self._update_query_set(self._get_query_set().
            filter(status=Wish.STATUS_DONE).order_by('-created'))
        return self

    def with_user(self, user):
        '''TODO'''
        self.model.current_user = user
        return self
    
class Wish(models.Model):
    '''TODO'''
    content = models.CharField(max_length=200)
    author = models.ForeignKey(User, related_name='nemo_wishes')
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
    status_message = models.CharField(max_length=200, blank=True)
    status_stamp = models.DateTimeField(auto_now_add=True)
    status_by = models.ForeignKey(User, null=True, blank=True)

    votes = models.ManyToManyField(User, through='Vote', 
                                   related_name='nemo_votes')
    ayes = models.IntegerField(default=0)
    negatives = models.IntegerField(default=0)
    
    objects = WishManager()
    
    class Meta:
        permissions = (
            ('response_wish', 'could response a wish'),
        )
    
    def count_ayes(self):
        '''TODO'''
        self.ayes = sum([ay.count for ay in Vote.ayes.filter(wish=self)])        
        return self.ayes
    
    def count_user_ayes(self):
        '''TODO'''
        if self.current_user:
            return Vote.ayes.filter(wish=self, 
                                    user=self.current_user).get().count
        else:
            return 0
        
    def count_negatives(self):
        '''TODO'''
        self.negatives = abs(sum([negative.count 
                    for negative in Vote.negatives.filter(wish=self)]))
        return self.negatives
    
    def count_user_negatives(self):
        '''TODO'''
        if self.current_user:
            return abs(Vote.negatives.filter(wish=self, 
                                             user=self.current_user).\
                                      get().count)
        else:
            return 0
        
    def status_label(self):
        '''TODO'''
        return self.STATUSES[self.status]
    
    def update_status(self, status, message, user):
        '''TODO'''
        self.status = status        
        self.status_message = message
        self.status_by = user
        self.status_stamp = datetime.now()
        
class WishForm(forms.ModelForm):
    '''TODO'''
    content = forms.CharField(max_length=140, initial='what do u want?',
                              error_messages={
                                  'required': 'Could not understand a wish '+\
                                              'with no words'
                              }, 
                              widget=forms.Textarea)
    
    def __init__(self, *args, **kwargs):
        super(WishForm, self).__init__(auto_id=False, *args, **kwargs)
        
    class Meta:
        model = Wish
        fields = ('content',)
        
class ResponseForm(forms.ModelForm):
    '''TODO'''
    status_message = forms.CharField(max_length=140, widget=forms.Textarea, 
                                     required=False)
    
    def __init__(self, *args, **kwargs):
        super(ResponseForm, self).__init__(auto_id=False, *args, **kwargs)
    
    class Meta:
        model = Wish
        fields = ('status', 'status_message')        

class AyManager(models.Manager):
    '''TODO'''
    def get_query_set(self):
        '''TODO'''
        return super(AyManager, self).get_query_set().filter(count__gt=0)
    
class NegativeManager(models.Manager):
    '''TODO'''
    def get_query_set(self):
        '''TODO'''
        return super(NegativeManager, self).get_query_set().filter(count__lt=0)    
    
class Vote(models.Model):
    '''TODO'''
    user = models.ForeignKey(User)
    wish = models.ForeignKey(Wish)
    count = models.SmallIntegerField(default=0,
                                     choices=[(i, i) for i in range(-3, 4)])
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    
    objects = models.Manager()
    ayes = AyManager()
    negatives = NegativeManager()