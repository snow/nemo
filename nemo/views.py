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
    
    def get_unauthenticated_response(self, format='json'):
        go_to = settings.LOGIN_URL
        
        if 'json' == format:
            return HttpResponse(json.dumps(dict(signin_uri=go_to)),
                                status=401,
                                content_type='application/json')
        else:
            return HttpResponseRedirect(go_to)

class IndexV(gv.TemplateView):
    '''Render index'''
    template_name = 'nemo/index.html'
    
    def get(self, request, stream_type, *args, **kwargs):
        '''TODO'''
        kwargs['form'] = nemo.WishForm()
        kwargs['stream_type'] = stream_type or 'hot'
        
        return super(IndexV, self).get(request, *args, **kwargs)
        
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
        
class CreateV(RedirectMixin, gv.CreateView):    
    '''Create a wish'''    
    form_class = nemo.WishForm
    
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            self.template_name = 'nemo/create.html'
        # else use default wish_form.html
        
        if request.user.is_authenticated():
            return super(CreateV, self).dispatch(request, *args, **kwargs)
        else:
            return self.get_unauthenticated_response()
    
    def form_valid(self, form):
        '''override to set author'''
        form.instance.author = self.request.user
        self.object = form.save()
        
        if self.request.is_ajax():
            self.success_url = self.get_html_chunk_uri()
        else:
            self.success_url = settings.NEMO_URI_ROOT + 'all/'
            
        return HttpResponseRedirect(self.success_url)
    
    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.render_to_response(self.get_context_data(form=form),
                                           status=403)
        else:
            return super(CreateV, self).form_invalid(form)

class VoteV(RedirectMixin, gv.View):
    '''TODO'''
    def post(self, request, pk, *args, **kwargs):
        '''TODO'''
        if not request.user.is_authenticated():
            return self.get_unauthenticated_response()
        
        user = nemo.UserProfile.objects.get_by_user(request.user)
        wish = nemo.Wish.objects.get(pk=pk)
        try:
            count = user.vote(wish, int(request.POST['count']))
        except nemo.UserProfile.OutOfVoteException as e:
            return HttpResponse(json.dumps(dict(done=False, has=e.has, 
                                                want=e.want, origin=e.origin)),
                                status=403,
                                content_type='application/json')
        else:
            return HttpResponseRedirect(RedirectMixin._get_html_chunk_uri(pk))
         
class UpdateV(RedirectMixin, gv.UpdateView):
    '''update wish content'''    
    form_class = nemo.WishForm
    model = nemo.Wish
    
    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            self.template_name = 'nemo/create.html'
        # else use default wish_form.html
        
        return super(UpdateV, self).dispatch(request, *args, **kwargs)
    
    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.render_to_response(self.get_context_data(form=form),
                                           status=403)
        else:
            return super(UpdateV, self).form_invalid(form)
        
    
class ResponseV(RedirectMixin, gv.UpdateView):
    '''Reponse to a wish'''    
    form_class = nemo.ResponseForm
    model = nemo.Wish
    
    def dispatch(self, request, *args, **kwargs):
        if request.is_ajax():
            self.template_name = 'nemo/response_form.html'
        else:
            self.template_name = 'nemo/response.html'
            
        return super(ResponseV, self).dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        self.object.update_status(form.cleaned_data['status'], 
                                  form.cleaned_data['status_message'], 
                                  self.request.user)
        self.object.save()
            
        return super(ResponseV, self).form_valid(form)
    
    def form_invalid(self, form):
        if self.request.is_ajax():
            return self.render_to_response(self.get_context_data(form=form),
                                           status=403)
        else:
            return super(ResponseV, self).form_invalid(form)
        
class VotesLeftV(gv.View):
    '''Return votes left for current user'''
    
    def get(self, request):
        up = nemo.UserProfile.objects.filter(user=request.user).get()
        
        return HttpResponse(json.dumps(dict(done=True, 
                                            votes_left=up.votes_left())),
                                content_type='application/json')        