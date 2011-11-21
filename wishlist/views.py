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
from django.contrib.auth.models import User as Account
from django.contrib.auth import authenticate, login
from django.utils.http import urlquote
from django.contrib.auth.forms import UserCreationForm
from django import forms

from wishlist.models import Wish, User

l = logging.getLogger(__name__)

class WishForm(ModelForm):
    content = forms.CharField(max_length=140, initial='what do u want?', 
                              widget=Textarea)
    class Meta:
        model = Wish
        fields = ('content',)

class IndexView(TemplateView):
    template_name = 'wishlist/index.html'
    
    def get(self, request, *args, **kwargs):
        kwargs['form'] = WishForm()
        
        return super(IndexView, self).get(request, *args, **kwargs)
        #context = self.get_context_data(**kwargs)
        #return self.render_to_response(context)
        
class CreateWishView(CreateView):        
    form_class = WishForm
    template_name = 'wishlist/create.html'
    success_url = '/'
    account = False

    def post(self, request, *args, **kwargs):
        # for passing user to form_valid
        self.account = request.user
        return super(CreateWishView, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        wish = form.instance
        try:
            user = User.objects.get(pk=self.account.id)
        except User.DoesNotExist:        
            user = User()
            user.account = self.account
            user.save()

        wish.author = user

        return super(CreateWishView, self).form_valid(form)
