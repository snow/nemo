# -*- coding: UTF-8 -*-
import json
import logging

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.views.generic import View, TemplateView, CreateView, ListView, \
                                 UpdateView

from wishlist.models import Wish, UserProfile, Vote

l = logging.getLogger(__name__)

class WishForm(forms.ModelForm):
    '''TODO'''
    content = forms.CharField(max_length=140, initial='what do u want?', 
                              widget=forms.Textarea)
    class Meta:
        model = Wish
        fields = ('content',)
        
class ResponseForm(forms.ModelForm):
    '''TODO'''    
    status_message = forms.CharField(max_length=140, widget=forms.Textarea, 
                                     required=False)
    class Meta:
        model = Wish
        fields = ('status', 'status_message')

class IndexV(TemplateView):
    '''TODO'''
    template_name = 'wishlist/index.html'
    
    def get(self, request, *args, **kwargs):
        '''TODO'''
        kwargs['form'] = WishForm()        
        return super(IndexV, self).get(request, *args, **kwargs)
        
class CreateV(CreateView):    
    '''TODO'''    
    form_class = WishForm
    template_name = 'wishlist/create.html'
    success_url = '/all/'
    user = False

    def post(self, request, *args, **kwargs):
        '''TODO'''
        # for passing user to form_valid
        self.user = request.user
        return super(CreateV, self).post(request, *args, **kwargs)

    def form_valid(self, form):
        '''TODO'''
        wish = form.instance
        wish.author = UserProfile.objects.get_by_user(self.user)

        return super(CreateV, self).form_valid(form)
    
class UpdateV(UpdateView):
    '''TODO'''    
    form_class = WishForm
    template_name = 'wishlist/create.html'
    model = Wish
    
    def dispatch(self, request, *args, **kwargs):
        '''TODO'''
        self.success_url = request.META['HTTP_REFERER']
        return super(UpdateV, self).dispatch(request, *args, **kwargs)
    
class ResponseV(UpdateView):
    '''TODO'''    
    form_class = ResponseForm
    template_name = 'wishlist/response.html'
    model = Wish
    
    def post(self, request, *args, **kwargs):
        '''TODO'''
        wish = self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        
        if form.is_valid():
            wish.update_status(form.cleaned_data['status'], 
                               form.cleaned_data['status_message'], 
                               UserProfile.objects.get_by_user(request.user))
            wish.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)
        
    def dispatch(self, request, *args, **kwargs):
        '''TODO'''
        self.success_url = request.META['HTTP_REFERER']
        return super(ResponseV, self).dispatch(request, *args, **kwargs)
    
class ListV(ListView):
    '''TODO'''
    template_name = 'wishlist/list.html'
    
    def get_queryset_(self, type, user):
        '''TODO'''
        if 'hot' == type:
            return Wish.objects.with_user(user).hot().all()
        elif 'top' == type:
            return Wish.objects.with_user(user).top().all()
        elif 'all' == type:
            return Wish.objects.with_user(user).recent().all()
        elif 'done' == type:
            return Wish.objects.with_user(user).done().all()

    def get(self, request, *args, **kwargs):
        '''TODO'''
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
        '''TODO'''
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