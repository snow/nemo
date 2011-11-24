# -*- coding: UTF-8 -*-
import urllib2
import json
import logging

from django.views.generic import View, TemplateView, CreateView, ListView, \
                                 FormView, DetailView, RedirectView, UpdateView
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ModelForm, Textarea, HiddenInput, RadioSelect
from django.shortcuts import render_to_response
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.utils.http import urlquote
from django.contrib.auth.forms import UserCreationForm
from django import forms

from wishlist.models import Wish, UserProfile, Vote

l = logging.getLogger(__name__)

class WishForm(ModelForm):
    '''TODO'''
    content = forms.CharField(max_length=140, initial='what do u want?', 
                              widget=Textarea)
    class Meta:
        model = Wish
        fields = ('content',)
        
class ResponseForm(ModelForm):
    '''TODO'''    
    response = forms.CharField(max_length=140, widget=Textarea, required=False)
    class Meta:
        model = Wish
        fields = ('status', 'response')

class IndexV(TemplateView):
    '''TODO'''
    template_name = 'wishlist/index.html'
    
    def get(self, request, *args, **kwargs):
        kwargs['form'] = WishForm()
        
        return super(IndexV, self).get(request, *args, **kwargs)
        #context = self.get_context_data(**kwargs)
        #return self.render_to_response(context)
        
class CreateV(CreateView):    
    '''TODO'''    
    form_class = WishForm
    template_name = 'wishlist/create.html'
    success_url = '/'
    user = False

    def post(self, request, *args, **kwargs):
        # for passing user to form_valid
        self.user = request.user
        return super(CreateV, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        wish = form.instance
        wish.author = UserProfile.objects.get_by_user(self.user)

        return super(CreateV, self).form_valid(form)
    
class UpdateV(UpdateView):
    '''TODO'''    
    form_class = WishForm
    template_name = 'wishlist/create.html'
    success_url = '/'
    model = Wish
    
class ResponseV(UpdateView):
    '''TODO'''    
    form_class = ResponseForm
    template_name = 'wishlist/response.html'
    success_url = '/'
    model = Wish
    
class ListV(ListView):
    '''TODO'''
    template_name = 'wishlist/list.html'
    
    def get_queryset_(self, type, user):
        if 'hot' == type:
            return Wish.objects.with_user(user).hot().all()
        elif 'top' == type:
            return Wish.objects.with_user(user).top().all()
        elif 'all' == type:
            return Wish.objects.with_user(user).recent().all()
        elif 'done' == type:
            return Wish.objects.with_user(user).done().all()

    def get(self, request, *args, **kwargs):
        # force queryset to be executed 
        # to make sure subsequnced access pointing to the same object
        self.queryset = list(self.get_queryset_(kwargs['stream_type'], 
                                                request.user))
        for e in self.queryset:
            if e.author.user == request.user:
                e.edit_form = WishForm(instance=e)
            if request.user.has_perm('wishlist.response_wish'):
                e.response_form = ResponseForm(instance=e)    
        
        return super(ListV, self).get(request, *args, **kwargs)
    
class VoteV(View):
    '''TODO'''
    def post(self, request, *args, **kwargs):
        user = UserProfile.objects.get_by_user(request.user)
        wish = Wish.objects.get(pk=kwargs['pk'])
        try:
            count = user.vote(wish, int(request.POST['count']))
        except UserProfile.OutOfVoteException as e:
            return HttpResponse(json.dumps({
                                    'done': False,
                                    'has': e.has,
                                    'want': e.want,
                                    'origin': e.origin
                                }),
                                content_type='application/json')
        else:
            return HttpResponse(json.dumps({
                                    'done': True,
                                    'count': count
                                }),
                                content_type='application/json')