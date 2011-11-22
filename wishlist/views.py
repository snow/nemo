# -*- coding: UTF-8 -*-
import urllib2
import json
import logging

from django.views.generic import View, TemplateView, CreateView, ListView, \
                                 FormView, DetailView, RedirectView
from django.http import HttpResponse, HttpResponseRedirect
from django.forms import ModelForm, Textarea, HiddenInput
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
    
class ListV(ListView):
    '''TODO'''
    template_name = 'wishlist/list.html'

    def get(self, request, *args, **kwargs):
        self.queryset = Wish.objects.with_user(request.user).recent().all()

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