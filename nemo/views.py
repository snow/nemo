# -*- coding: UTF-8 -*-
import json
import logging

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import django.views.generic as gv

import nemo.models as nemo

class IndexV(gv.TemplateView):
    '''Render index'''
    template_name = 'nemo/index.html'
    
    def get(self, request, stream_type='hot', *args, **kwargs):
        '''TODO'''
        kwargs['form'] = nemo.WishForm()
        kwargs['stream_type'] = stream_type
        return super(IndexV, self).get(request, *args, **kwargs)
        
class CreateV(gv.CreateView):    
    '''Create a wish'''    
    form_class = nemo.WishForm
    template_name = 'nemo/create.html'
    success_url = settings.NEMO_URI_ROOT + 'all/'

    def form_valid(self, form):
        '''override to set author'''
        wish = form.instance
        wish.author = self.request.user

        return super(CreateV, self).form_valid(form)
    
class UpdateV(gv.UpdateView):
    '''update wish content'''    
    form_class = nemo.WishForm
    template_name = 'nemo/create.html'
    model = nemo.Wish
    
    def dispatch(self, request, *args, **kwargs):
        '''override to set success_url'''
        self.success_url = request.META.get('HTTP_REFERER', 
                                            settings.NEMO_URI_ROOT)
        return super(UpdateV, self).dispatch(request, *args, **kwargs)
    
class ResponseV(gv.UpdateView):
    '''Reponse to a wish'''    
    form_class = nemo.ResponseForm
    template_name = 'nemo/response.html'
    model = nemo.Wish
    
    def post(self, request, *args, **kwargs):
        '''TODO'''
        wish = self.object = self.get_object()
        form = self.get_form(self.get_form_class())
        
        if form.is_valid():
            wish.update_status(form.cleaned_data['status'], 
                               form.cleaned_data['status_message'], 
                               request.user)
            wish.save()
            return HttpResponseRedirect(self.get_success_url())
        else:
            return self.form_invalid(form)
        
    def dispatch(self, request, *args, **kwargs):
        '''TODO'''
        # why separete this from post()?
        self.success_url = request.META.get('HTTP_REFERER', 
                                            settings.NEMO_URI_ROOT)
        return super(ResponseV, self).dispatch(request, *args, **kwargs)
    
class ListV(gv.ListView):
    '''TODO'''
    template_name = 'nemo/list.html'
    
    def get_queryset_(self, type, user):
        '''TODO'''
        # why cant override get_queryset()?
        if 'hot' == type:
            return nemo.Wish.objects.with_user(user).hot().all()
        elif 'top' == type:
            return nemo.Wish.objects.with_user(user).top().all()
        elif 'all' == type:
            return nemo.Wish.objects.with_user(user).recent().all()
        elif 'done' == type:
            return nemo.Wish.objects.with_user(user).done().all()

    def get(self, request, stream_type='hot', *args, **kwargs):
        '''TODO'''
        # force queryset to be executed 
        # to make sure subsequnced access pointing to the same object
        self.queryset = list(self.get_queryset_(stream_type, request.user))
        for e in self.queryset:
            if e.author == request.user:
                e.edit_form = nemo.WishForm(instance=e)
            if request.user.has_perm('nemo.response_wish'):
                e.response_form = nemo.ResponseForm(instance=e)    
        
        return super(ListV, self).get(request, *args, **kwargs)
    
class VoteV(gv.View):
    '''TODO'''
    def post(self, request, pk, *args, **kwargs):
        '''TODO'''
        user = nemo.UserProfile.objects.get_by_user(request.user)
        wish = nemo.Wish.objects.get(pk=pk)
        try:
            count = user.vote(wish, int(request.POST['count']))
        except nemo.UserProfile.OutOfVoteException as e:
            resp = dict(done=False, has=e.has, want=e.want, origin=e.origin)
        else:
            resp = dict(done=True, count=count)
            
        return HttpResponse(json.dumps(resp), content_type='application/json')