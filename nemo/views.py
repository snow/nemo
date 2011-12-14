# -*- coding: UTF-8 -*-
import json
import logging

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
import django.views.generic as gv

import nemo.models as nemo

class RedirectMixin():
    '''Nemo's redirect business logic'''
    
    @classmethod
    def _get_html_chunk_uri(cls, id):
        id = int(id)
        return '{}list/all/since{}/till{}/'.format(settings.NEMO_URI_ROOT, 
                                                   id-1, id+1)
        
    def get_html_chunk_uri(self):
        return self._get_html_chunk_uri(self.object.id)
        
    def get_back_uri(self):
        return self.request.META.get('HTTP_REFERER', settings.NEMO_URI_ROOT)
    
    def get_success_url(self):
        if self.request.is_ajax():
            self.success_url = self.get_html_chunk_uri()
        else:
            self.success_url = self.get_back_uri()
            
        return self.success_url    

class IndexV(gv.TemplateView):
    '''Render index'''
    template_name = 'nemo/index.html'
    
    def get(self, request, stream_type, *args, **kwargs):
        '''TODO'''
        kwargs['form'] = nemo.WishForm()
        kwargs['stream_type'] = stream_type or 'hot'
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
    
class UpdateV(RedirectMixin, gv.UpdateView):
    '''update wish content'''    
    form_class = nemo.WishForm
    template_name = 'nemo/create.html'
    model = nemo.Wish
        
    
class ResponseV(RedirectMixin, gv.UpdateView):
    '''Reponse to a wish'''    
    form_class = nemo.ResponseForm
    template_name = 'nemo/response.html'
    model = nemo.Wish
    
    def form_valid(self, form):
        self.object.update_status(form.cleaned_data['status'], 
                                  form.cleaned_data['status_message'], 
                                  self.request.user)
        self.object.save()
            
        return super(ResponseV, self).form_valid(form)
    
    
class ListV(gv.ListView):
    '''TODO'''
    template_name = 'nemo/list.html'
    
    def get_queryset_(self, type, user, since, till):
        '''TODO'''
        # why cant override get_queryset()?
        if 'hot' == type:
            qs = nemo.Wish.objects.with_user(user).hot()
        elif 'top' == type:
            qs = nemo.Wish.objects.with_user(user).top()
        elif 'all' == type:
            qs = nemo.Wish.objects.with_user(user).recent()
        elif 'done' == type:
            qs = nemo.Wish.objects.with_user(user).done()
    
        if since:
            qs = qs.filter(id__gt=since)
            
        if till:
            qs = qs.filter(id__lt=till)
            
        return qs.all()

    def get(self, request, stream_type, since, till, *args, **kwargs):
        '''TODO'''
        # force queryset to be executed 
        # to make sure subsequnced access pointing to the same object
        self.queryset = list(self.get_queryset_(stream_type, request.user, 
                                                since, till))
        for e in self.queryset:
            if e.author == request.user:
                e.edit_form = nemo.WishForm(instance=e)
            if request.user.has_perm('nemo.response_wish'):
                e.response_form = nemo.ResponseForm(instance=e)    
        
        return super(ListV, self).get(request, *args, **kwargs)
    
class VoteV(RedirectMixin, gv.View):
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
            
        #return HttpResponse(json.dumps(resp), content_type='application/json')
        return HttpResponseRedirect(RedirectMixin._get_html_chunk_uri(pk))