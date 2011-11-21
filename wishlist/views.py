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

class IndexView(TemplateView):
    template_name = 'wishlist/index.html'

