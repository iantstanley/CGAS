# core/views/resources.py
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from django.http import HttpResponse
from django.db.models import Q

from core.models import GateCode, Ordinance
from core.forms import GateCodeForm, GateCodeSearchForm, OrdinanceForm

# Gate Code Views
class GateCodeListView(LoginRequiredMixin, ListView):
    model = GateCode
    template_name = 'field_resources/gate_code_list.html'
    context_object_name = 'gate_codes'
    paginate_by = 25
    
    def get_queryset(self):
        queryset = GateCode.objects.all()
        form = GateCodeSearchForm(self.request.GET)
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search')
            
            if search_term:
                queryset = queryset.filter(
                    Q(community_name__icontains=search_term) |
                    Q(gate_code__icontains=search_term) |
                    Q(notes__icontains=search_term)
                )
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = GateCodeSearchForm(self.request.GET)
        return context

class GateCodeCreateView(LoginRequiredMixin, CreateView):
    model = GateCode
    template_name = 'field_resources/gate_code_form.html'
    form_class = GateCodeForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Gate code added successfully!')
        return response

class GateCodeUpdateView(LoginRequiredMixin, UpdateView):
    model = GateCode
    template_name = 'field_resources/gate_code_form.html'
    form_class = GateCodeForm
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Gate code updated successfully!')
        return response

class GateCodeDeleteView(LoginRequiredMixin, DeleteView):
    model = GateCode
    template_name = 'field_resources/gate_code_confirm_delete.html'
    success_url = reverse_lazy('gate-code-list')
    context_object_name = 'gate_code'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Gate code deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Ordinance Views
class OrdinanceListView(LoginRequiredMixin, ListView):
    model = Ordinance
    template_name = 'ordinances/ordinance_list.html'
    context_object_name = 'ordinances'

class OrdinanceDetailView(LoginRequiredMixin, DetailView):
    model = Ordinance
    template_name = 'ordinances/ordinance_detail.html'
    context_object_name = 'ordinance'

class OrdinanceCreateView(LoginRequiredMixin, CreateView):
    model = Ordinance
    form_class = OrdinanceForm
    template_name = 'ordinances/ordinance_form.html'
    success_url = reverse_lazy('ordinance-list')

class OrdinanceUpdateView(LoginRequiredMixin, UpdateView):
    model = Ordinance
    form_class = OrdinanceForm
    template_name = 'ordinances/ordinance_form.html'
    success_url = reverse_lazy('ordinance-list')

class OrdinanceDeleteView(LoginRequiredMixin, DeleteView):
    model = Ordinance
    template_name = 'ordinances/ordinance_confirm_delete.html'
    success_url = reverse_lazy('ordinance-list')

class OrdinanceRedirectView(LoginRequiredMixin, DetailView):
    model = Ordinance
    
    def get(self, request, *args, **kwargs):
        ordinance = self.get_object()
        
        if ordinance.is_url and ordinance.url:
            return redirect(ordinance.url)
        elif ordinance.document:
            # For documents, serve the file
            response = HttpResponse(ordinance.document.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'inline; filename="{ordinance.get_document_name()}"'
            return response
        else:
            return redirect('ordinance-detail', pk=ordinance.pk)