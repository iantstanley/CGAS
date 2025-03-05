# core/views/clients.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from core.models import Client
from core.forms import ClientForm, ClientSearchForm

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'clients/client_list.html'
    context_object_name = 'clients'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Client.objects.all()
        form = ClientSearchForm(self.request.GET)
    
        if form.is_valid():
            search_term = form.cleaned_data.get('search')
            status = form.cleaned_data.get('status')
        
            if search_term:
                queryset = queryset.filter(
                    Q(name__icontains=search_term) |
                    Q(company_name__icontains=search_term) |
                    Q(contact_person__icontains=search_term) |
                    Q(email__icontains=search_term) |
                    Q(phone__icontains=search_term) |
                    Q(address__icontains=search_term) |
                    Q(city__icontains=search_term)
                )
        
            if status == 'active':
                queryset = queryset.filter(active=True)
            elif status == 'inactive':
                queryset = queryset.filter(active=False)
    
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ClientSearchForm(self.request.GET)
        return context

class ClientDetailView(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'clients/client_detail.html'
    context_object_name = 'client'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related projects for this client
        context['projects'] = self.object.projects.all()
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('client-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Client created successfully!')
        return super().form_valid(form)

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('client-list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Client updated successfully!')
        return super().form_valid(form)

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('client-list')
    context_object_name = 'client'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Client deleted successfully!')
        return super().delete(request, *args, **kwargs)