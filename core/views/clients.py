# core/views/clients.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.db.models import Q
from core.models import Client, ClientEmail, ClientPhone
from core.forms import (
    ClientForm, ClientSearchForm, 
    ClientEmailFormSet, ClientPhoneFormSet
)

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
            client_type = form.cleaned_data.get('client_type')
        
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
                
            if client_type:
                queryset = queryset.filter(client_type=client_type)
        
        # Handle sorting
        sort_field = self.request.GET.get('sort', 'name')  # Default sort by name
        direction = self.request.GET.get('direction', 'asc')
        
        if sort_field in ['name', 'company_name']:
            order_field = f"{'-' if direction == 'desc' else ''}{sort_field}"
            queryset = queryset.order_by(order_field)
    
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
        # Get related emails and phones
        context['emails'] = self.object.emails.all()
        context['phones'] = self.object.phones.all()
        return context

class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('client-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['email_formset'] = ClientEmailFormSet(self.request.POST, instance=self.object)
            context['phone_formset'] = ClientPhoneFormSet(self.request.POST, instance=self.object)
        else:
            context['email_formset'] = ClientEmailFormSet(instance=self.object)
            context['phone_formset'] = ClientPhoneFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        email_formset = context['email_formset']
        phone_formset = context['phone_formset']
        
        if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
            self.object = form.save()
            email_formset.instance = self.object
            email_formset.save()
            phone_formset.instance = self.object
            phone_formset.save()
            messages.success(self.request, 'Client created successfully!')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_form.html'
    form_class = ClientForm
    success_url = reverse_lazy('client-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['email_formset'] = ClientEmailFormSet(self.request.POST, instance=self.object)
            context['phone_formset'] = ClientPhoneFormSet(self.request.POST, instance=self.object)
        else:
            context['email_formset'] = ClientEmailFormSet(instance=self.object)
            context['phone_formset'] = ClientPhoneFormSet(instance=self.object)
        return context
    
    def form_valid(self, form):
        context = self.get_context_data()
        email_formset = context['email_formset']
        phone_formset = context['phone_formset']
        
        if form.is_valid() and email_formset.is_valid() and phone_formset.is_valid():
            self.object = form.save()
            email_formset.instance = self.object
            email_formset.save()
            phone_formset.instance = self.object
            phone_formset.save()
            messages.success(self.request, 'Client updated successfully!')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))

class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = 'clients/client_confirm_delete.html'
    success_url = reverse_lazy('client-list')
    context_object_name = 'client'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Client deleted successfully!')
        return super().delete(request, *args, **kwargs)