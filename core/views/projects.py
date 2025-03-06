# core/views/projects.py
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseRedirect, HttpResponse

from core.models import (
    Client, Project, ProjectEmail, ProjectBillingEmail, 
    ProjectPhone, PropertyDeed, PropertyMap, ProjectAttachment,
    ProjectComment
)
from core.forms import (
    ProjectForm, ProjectSearchForm, ProjectEmailForm,
    ProjectBillingEmailForm, ProjectPhoneForm, PropertyDeedForm,
    PropertyMapForm, ProjectAttachmentForm, ProjectCommentForm,
    ProjectEmailFormSet, ProjectBillingEmailFormSet, ProjectPhoneFormSet,
    PropertyDeedFormSet, PropertyMapFormSet, ProjectAttachmentFormSet
)

class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Project.objects.all()
        form = ProjectSearchForm(self.request.GET)
        
        if form.is_valid():
            search_term = form.cleaned_data.get('search')
            status = form.cleaned_data.get('status')
            sort_by = form.cleaned_data.get('sort_by')
            
            # Apply filters based on search term
            if search_term:
                queryset = queryset.filter(
                    Q(title__icontains=search_term) |
                    Q(project_number__icontains=search_term) |
                    Q(client__name__icontains=search_term) |
                    Q(property_address__icontains=search_term) |
                    Q(property_tax_parcel__icontains=search_term)
                )
            
            # Filter by status if provided
            if status:
                queryset = queryset.filter(status=status)
            
            # Apply sorting if provided
            if sort_by:
                # Check if sort parameter is in the request
                direction = self.request.GET.get('sort', '')
                if direction == sort_by:
                    # Already sorted ascending, switch to descending
                    queryset = queryset.order_by(f'-{sort_by}')
                else:
                    queryset = queryset.order_by(sort_by)
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = ProjectSearchForm(self.request.GET)
        # Add sorting information for column headers
        sort_param = self.request.GET.get('sort', '')
        context['current_sort'] = sort_param
        return context

class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_detail.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add calendar events related to this project
        context['calendar_events'] = self.object.calendar_events.all().order_by('start_time')
        return context

class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectForm
    
    def form_valid(self, form):
        # Set the created_by field to the current user
        form.instance.created_by = self.request.user
        
        # First save the project to get an ID
        response = super().form_valid(form)
        project = self.object
        
        # Process client emails
        client_emails = self.request.POST.getlist('client_email[]')
        client_email_primaries = self.request.POST.getlist('client_email_primary[]')
        
        # Create client emails
        for i in range(len(client_emails)):
            if client_emails[i]:  # Make sure we have an email
                # Check if this email is marked as primary
                is_primary = False
                
                # Convert values to strings for comparison
                str_i = str(i)
                client_email_primaries_str = [str(x) for x in client_email_primaries]
                
                if client_email_primaries and str_i in client_email_primaries_str:
                    is_primary = True
                    # If this is primary, set all others to non-primary
                    ProjectEmail.objects.filter(project=project, is_primary=True).update(is_primary=False)
                
                ProjectEmail.objects.create(
                    project=project,
                    email=client_emails[i],
                    is_primary=is_primary
                )
        
        # Process billing emails
        billing_emails = self.request.POST.getlist('billing_email[]')
        billing_email_primaries = self.request.POST.getlist('billing_email_primary[]')
        
        # Create billing emails
        for i in range(len(billing_emails)):
            if billing_emails[i]:  # Make sure we have an email
                # Check if this email is marked as primary
                is_primary = False
                
                # Convert values to strings for comparison
                str_i = str(i)
                billing_email_primaries_str = [str(x) for x in billing_email_primaries]
                
                if billing_email_primaries and str_i in billing_email_primaries_str:
                    is_primary = True
                    # If this is primary, set all others to non-primary
                    ProjectBillingEmail.objects.filter(project=project, is_primary=True).update(is_primary=False)
                
                ProjectBillingEmail.objects.create(
                    project=project,
                    email=billing_emails[i],
                    is_primary=is_primary
                )
        
        # Process phone numbers
        phone_numbers = self.request.POST.getlist('phone_number[]')
        phone_descriptions = self.request.POST.getlist('phone_description[]')
        phone_primaries = self.request.POST.getlist('phone_primary[]')
        
        # Create phone numbers
        for i in range(len(phone_numbers)):
            if phone_numbers[i]:  # Make sure we have a phone number
                # Get corresponding description if available
                description = phone_descriptions[i] if i < len(phone_descriptions) else ""
                
                # Check if this phone is marked as primary
                is_primary = False
                
                # Convert values to strings for comparison
                str_i = str(i)
                phone_primaries_str = [str(x) for x in phone_primaries]
                
                if phone_primaries and str_i in phone_primaries_str:
                    is_primary = True
                    # If this is primary, set all others to non-primary
                    ProjectPhone.objects.filter(project=project, is_primary=True).update(is_primary=False)
                
                ProjectPhone.objects.create(
                    project=project,
                    phone=phone_numbers[i],
                    description=description,
                    is_primary=is_primary
                )
        
        # NEW CODE: Process property maps
        map_names = self.request.POST.getlist('map_name[]')
        map_descriptions = self.request.POST.getlist('map_description[]')
        map_files = self.request.FILES.getlist('map_file[]')
        
        # Create property maps if data is provided
        for i in range(len(map_names)):
            if i < len(map_files) and map_names[i] and map_files[i]:
                # Get corresponding description if available
                description = map_descriptions[i] if i < len(map_descriptions) else ""
                
                PropertyMap.objects.create(
                    project=project,
                    name=map_names[i],
                    description=description,
                    file=map_files[i]
                )
        
        # NEW CODE: Process property deeds
        deed_books = self.request.POST.getlist('deed_book[]')
        deed_descriptions = self.request.POST.getlist('deed_description[]')
        deed_files = self.request.FILES.getlist('deed_file[]')
        deed_pages = self.request.POST.getlist('deed_page[]')
        
        # Create property deeds if data is provided
        for i in range(len(deed_books)):
            if deed_books[i]:
                # Get corresponding description and file if available
                description = deed_descriptions[i] if i < len(deed_descriptions) else ""
                page = deed_pages[i] if i < len(deed_pages) else ""
                
                deed = PropertyDeed.objects.create(
                    project=project,
                    book=deed_books[i],
                    page=page,
                    description=description
                )
                
                # If there's a file, save it as an attachment with the deed name
                if i < len(deed_files) and deed_files[i]:
                    ProjectAttachment.objects.create(
                        project=project,
                        name=f"Deed {deed_books[i]}-{page}",
                        description=f"Property deed {deed_books[i]}, page {page}",
                        file=deed_files[i]
                    )
        
        # NEW CODE: Process other attachments
        attachment_names = self.request.POST.getlist('attachment_name[]')
        attachment_descriptions = self.request.POST.getlist('attachment_description[]')
        attachment_files = self.request.FILES.getlist('attachment_file[]')
        
        # Create attachments if data is provided
        for i in range(len(attachment_names)):
            if i < len(attachment_files) and attachment_names[i] and attachment_files[i]:
                # Get corresponding description if available
                description = attachment_descriptions[i] if i < len(attachment_descriptions) else ""
                
                ProjectAttachment.objects.create(
                    project=project,
                    name=attachment_names[i],
                    description=description,
                    file=attachment_files[i]
                )
        
        messages.success(self.request, 'Project created successfully!')
        return response
    
    def get_initial(self):
        # Pre-populate client field if passed in URL
        initial = super().get_initial()
        client_id = self.request.GET.get('client')
        if client_id:
            try:
                initial['client'] = Client.objects.get(pk=client_id)
            except Client.DoesNotExist:
                pass
        return initial

class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    template_name = 'projects/project_form.html'
    form_class = ProjectForm
    
    def form_valid(self, form):
        messages.success(self.request, 'Project updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        # Return to project detail page after update
        return reverse_lazy('project-detail', kwargs={'pk': self.object.pk})

class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/project_confirm_delete.html'
    success_url = reverse_lazy('project-list')
    context_object_name = 'project'
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Project deleted successfully!')
        return super().delete(request, *args, **kwargs)

# Print Project View
class ProjectPrintView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/project_print.html'
    context_object_name = 'project'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

# Additional Project-related Views
@login_required
def add_project_email(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        is_primary = 'is_primary' in request.POST
        
        if email:
            # If is_primary is true, set all others to false
            if is_primary:
                ProjectEmail.objects.filter(project=project, is_primary=True).update(is_primary=False)
            
            ProjectEmail.objects.create(
                project=project,
                email=email,
                is_primary=is_primary
            )
            messages.success(request, 'Email address added successfully!')
        
    return redirect('project-update', pk=project.pk)

@login_required
def delete_project_email(request, pk, email_id):
    project = get_object_or_404(Project, pk=pk)
    email = get_object_or_404(ProjectEmail, pk=email_id, project=project)
    email.delete()
    messages.success(request, 'Email address removed successfully!')
    return redirect('project-update', pk=project.pk)

@login_required
def add_project_billing_email(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        is_primary = 'is_primary' in request.POST
        
        if email:
            # If is_primary is true, set all others to false
            if is_primary:
                ProjectBillingEmail.objects.filter(project=project, is_primary=True).update(is_primary=False)
            
            ProjectBillingEmail.objects.create(
                project=project,
                email=email,
                is_primary=is_primary
            )
            messages.success(request, 'Billing email address added successfully!')
        
    return redirect('project-update', pk=project.pk)

@login_required
def delete_project_billing_email(request, pk, email_id):
    project = get_object_or_404(Project, pk=pk)
    email = get_object_or_404(ProjectBillingEmail, pk=email_id, project=project)
    email.delete()
    messages.success(request, 'Billing email address removed successfully!')
    return redirect('project-update', pk=project.pk)

@login_required
def add_project_phone(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        phone = request.POST.get('phone')
        description = request.POST.get('description', '')
        is_primary = 'is_primary' in request.POST
        
        if phone:
            # If is_primary is true, set all others to false
            if is_primary:
                ProjectPhone.objects.filter(project=project, is_primary=True).update(is_primary=False)
            
            ProjectPhone.objects.create(
                project=project,
                phone=phone,
                description=description,
                is_primary=is_primary
            )
            messages.success(request, 'Phone number added successfully!')
        
    return redirect('project-update', pk=project.pk)

@login_required
def delete_project_phone(request, pk, phone_id):
    project = get_object_or_404(Project, pk=pk)
    phone = get_object_or_404(ProjectPhone, pk=phone_id, project=project)
    phone.delete()
    messages.success(request, 'Phone number removed successfully!')
    return redirect('project-update', pk=project.pk)

@login_required
def add_property_deed(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        book = request.POST.get('book')
        page = request.POST.get('page', '')
        description = request.POST.get('description', '')
        
        if book:
            deed = PropertyDeed.objects.create(
                project=project,
                book=book,
                page=page,
                description=description
            )
            
            # Check if file was uploaded
            if 'deed_file' in request.FILES:
                ProjectAttachment.objects.create(
                    project=project,
                    name=f"Deed {book}-{page}",
                    description=f"Property deed {book}, page {page}",
                    file=request.FILES['deed_file']
                )
                
            messages.success(request, 'Property deed added successfully!')
        
    # Redirect to Documents tab
    return redirect(f'{reverse("project-detail", kwargs={"pk": project.pk})}#documents')

@login_required
def delete_property_deed(request, pk, deed_id):
    project = get_object_or_404(Project, pk=pk)
    deed = get_object_or_404(PropertyDeed, pk=deed_id, project=project)
    deed.delete()
    messages.success(request, 'Property deed removed successfully!')
    # Redirect to Documents tab
    return redirect(f'{reverse("project-detail", kwargs={"pk": project.pk})}#documents')

@login_required
def add_property_map(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name and 'file' in request.FILES:
            PropertyMap.objects.create(
                project=project,
                name=name,
                description=description,
                file=request.FILES['file']
            )
            messages.success(request, 'Property map added successfully!')
        else:
            messages.error(request, 'Name and file are required for property maps.')
        
    # Redirect to Documents tab
    return redirect(f'{reverse("project-detail", kwargs={"pk": project.pk})}#documents')

@login_required
def delete_property_map(request, pk, map_id):
    project = get_object_or_404(Project, pk=pk)
    map_obj = get_object_or_404(PropertyMap, pk=map_id, project=project)
    map_obj.delete()
    messages.success(request, 'Property map removed successfully!')
    # Redirect to Documents tab
    return redirect(f'{reverse("project-detail", kwargs={"pk": project.pk})}#documents')

@login_required
def add_project_attachment(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        
        if name and 'file' in request.FILES:
            ProjectAttachment.objects.create(
                project=project,
                name=name,
                description=description,
                file=request.FILES['file']
            )
            messages.success(request, 'Attachment added successfully!')
        else:
            messages.error(request, 'Name and file are required for attachments.')
        
    # Redirect to Documents tab
    return redirect(f'{reverse("project-detail", kwargs={"pk": project.pk})}#documents')

@login_required
def delete_project_attachment(request, pk, attachment_id):
    project = get_object_or_404(Project, pk=pk)
    attachment = get_object_or_404(ProjectAttachment, pk=attachment_id, project=project)
    attachment.delete()
    messages.success(request, 'Attachment removed successfully!')
    # Redirect to Documents tab
    return redirect(f'{reverse("project-detail", kwargs={"pk": project.pk})}#documents')

@login_required
def add_project_comment(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        text = request.POST.get('text')
        
        if text:
            ProjectComment.objects.create(
                project=project,
                user=request.user,
                text=text
            )
            messages.success(request, 'Comment added successfully!')
        
    # Get the current URL's hash fragment if it exists
    referer = request.META.get('HTTP_REFERER', '')
    hash_part = '#comments'
    
    if '#' in referer:
        base_url, hash_value = referer.split('#', 1)
        if hash_value:
            hash_part = f'#{hash_value}'
    
    # Redirect back to the appropriate tab
    return redirect(f'{reverse("project-detail", kwargs={"pk": project.pk})}{hash_part}')