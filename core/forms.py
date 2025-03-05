# core/forms.py
from django import forms
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Row, Column, Fieldset, HTML, Div, Button
from crispy_forms.bootstrap import TabHolder, Tab, FormActions
from .models import (
    Client, User, Project, ProjectEmail, ProjectBillingEmail, 
    ProjectPhone, PropertyDeed, PropertyMap, ProjectAttachment,
    ProjectComment, FieldCrew, CrewMember, Vehicle, TotalStation, GpsReceiver,
    DataCollector, MobileHotspot, RtkNetwork, GateCode, CalendarEvent, Ordinance
)

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'password1', 'password2', 'first_name', 'last_name')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Register', css_class='btn-primary'))

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = [
            'company_name', 'name', 'contact_person', 
            'email', 'billing_email', 'phone', 
            'address', 'city', 'state', 'zip_code', 
            'notes', 'active'
        ]
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save Client', css_class='btn-primary'))
        
        # Layout with Bootstrap grid
        self.helper.layout = Layout(
            Row(
                Column('company_name', css_class='form-group col-md-6 mb-3'),
                Column('name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('contact_person', css_class='form-group col-md-6 mb-3'),
                Column('phone', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('billing_email', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('address', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('city', css_class='form-group col-md-4 mb-3'),
                Column('state', css_class='form-group col-md-4 mb-3'),
                Column('zip_code', css_class='form-group col-md-4 mb-3'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('active', css_class='form-group col-md-12 mb-3'),
            ),
        )

class ClientSearchForm(forms.Form):
    search = forms.CharField(
        required=False, 
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search clients...', 
            'class': 'form-control bg-medium text-light'
        })
    )
    status = forms.ChoiceField(
        required=False, 
        label='',  # Remove the label text
        choices=[('', 'All'), ('active', 'Active'), ('inactive', 'Inactive')],
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        
        # Modified layout for improved search form appearance
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-8 mb-0'),
                Column(
                    Div(
                        Div('Status', css_class='small text-muted mb-1'),
                        'status',
                        css_class='d-flex flex-column'
                    ),
                    css_class='form-group col-md-3 mb-0'
                ),
                Column(
                    Submit('submit', 'Search', css_class='btn-primary w-100 h-100'), 
                    css_class='form-group col-md-1 mb-0 d-flex align-items-end'
                ),
            )
        )

class ProjectForm(forms.ModelForm):
    # Add these fields explicitly
    latitude = forms.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        required=False,
        help_text="Enter latitude manually if geocoding fails"
    )
    longitude = forms.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        required=False,
        help_text="Enter longitude manually if geocoding fails"
    )
    
    class Meta:
        model = Project
        fields = [
            'project_number', 'title', 'client', 'status',
            'start_date', 'end_date', 'location', 'assigned_to',
            'has_legal_contract', 'contract_document', 'legal_name_for_survey',
            'property_address', 'property_tax_parcel', 'flood_map_number',
            'base_flood_elevation', 'quoted_price', 'quoted_time_frame',
            'notes', 'description', 'latitude', 'longitude',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'property_address': forms.Textarea(attrs={'rows': 2}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'assigned_to': forms.SelectMultiple(attrs={'class': 'form-select'}),
            'quoted_price': forms.NumberInput(attrs={'step': '0.01'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.form_enctype = 'multipart/form-data'
        
        # Make project number readonly if it exists
        if self.instance.pk and self.instance.project_number:
            self.fields['project_number'].widget.attrs['readonly'] = True
        else:
            self.fields['project_number'].help_text = "Optional. Will be auto-generated if left blank."
        
        self.helper.layout = Layout(
            TabHolder(
                Tab('Basic Information',
                    Row(
                        Column('project_number', css_class='form-group col-md-4 mb-3'),
                        Column('title', css_class='form-group col-md-8 mb-3'),
                    ),
                    Row(
                        Column('client', css_class='form-group col-md-6 mb-3'),
                        Column('status', css_class='form-group col-md-6 mb-3'),
                    ),
                    Row(
                        Column('start_date', css_class='form-group col-md-6 mb-3'),
                        Column('end_date', css_class='form-group col-md-6 mb-3'),
                    ),
                    Row(
                        Column('location', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('description', css_class='form-group col-md-12 mb-3'),
                    ),
                ),
                Tab('Property Information',
                    Row(
                        Column('legal_name_for_survey', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('property_address', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('property_tax_parcel', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('flood_map_number', css_class='form-group col-md-6 mb-3'),
                        Column('base_flood_elevation', css_class='form-group col-md-6 mb-3'),
                    ),
                    HTML('<hr><h5>Property Deeds & Maps</h5><p class="text-muted">You can add these after saving the project</p>'),
                ),
                Tab('Contract & Financial',
                    Row(
                        Column('has_legal_contract', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('contract_document', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('quoted_price', css_class='form-group col-md-6 mb-3'),
                        Column('quoted_time_frame', css_class='form-group col-md-6 mb-3'),
                    ),
                ),
                Tab('Team & Notes',
                    Row(
                        Column('assigned_to', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('notes', css_class='form-group col-md-12 mb-3'),
                    ),
                    HTML('<hr><h5>Contact Information</h5><p class="text-muted">You can add additional contact details after saving the project</p>'),
                ),
            ),
            FormActions(
                Submit('submit', 'Save Project', css_class='btn-primary'),
                Button('cancel', 'Cancel', css_class='btn-secondary', onclick="window.history.back()"),
            )
        )

    def clean_project_number(self):
        """Prevent changing an existing project number"""
        project_number = self.cleaned_data.get('project_number')
        if self.instance.pk and self.instance.project_number and project_number != self.instance.project_number:
            return self.instance.project_number
        return project_number


class ProjectEmailForm(forms.ModelForm):
    class Meta:
        model = ProjectEmail
        fields = ['email', 'is_primary']
        

class ProjectBillingEmailForm(forms.ModelForm):
    class Meta:
        model = ProjectBillingEmail
        fields = ['email', 'is_primary']


class ProjectPhoneForm(forms.ModelForm):
    class Meta:
        model = ProjectPhone
        fields = ['phone', 'description', 'is_primary']


class PropertyDeedForm(forms.ModelForm):
    class Meta:
        model = PropertyDeed
        fields = ['book', 'page', 'description']


class PropertyMapForm(forms.ModelForm):
    class Meta:
        model = PropertyMap
        fields = ['name', 'file', 'description']


class ProjectAttachmentForm(forms.ModelForm):
    class Meta:
        model = ProjectAttachment
        fields = ['name', 'file', 'description']


class ProjectCommentForm(forms.ModelForm):
    class Meta:
        model = ProjectComment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }


# Create formsets for related models
ProjectEmailFormSet = inlineformset_factory(
    Project, ProjectEmail, form=ProjectEmailForm, extra=1, can_delete=True
)

ProjectBillingEmailFormSet = inlineformset_factory(
    Project, ProjectBillingEmail, form=ProjectBillingEmailForm, extra=1, can_delete=True
)

ProjectPhoneFormSet = inlineformset_factory(
    Project, ProjectPhone, form=ProjectPhoneForm, extra=1, can_delete=True
)

PropertyDeedFormSet = inlineformset_factory(
    Project, PropertyDeed, form=PropertyDeedForm, extra=1, can_delete=True
)

PropertyMapFormSet = inlineformset_factory(
    Project, PropertyMap, form=PropertyMapForm, extra=1, can_delete=True
)

ProjectAttachmentFormSet = inlineformset_factory(
    Project, ProjectAttachment, form=ProjectAttachmentForm, extra=1, can_delete=True
)


class ProjectSearchForm(forms.Form):
    search = forms.CharField(
        required=False, 
        label='',
        widget=forms.TextInput(attrs={'placeholder': 'Search projects...', 'class': 'form-control bg-medium text-light'})
    )
    status = forms.ChoiceField(
        required=False, 
        label='Status',
        choices=[('', 'All')] + list(Project.STATUS_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    client = forms.ModelChoiceField(
        required=False,
        label='Client',
        queryset=Client.objects.all(),
        empty_label="All Clients",
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    date_range = forms.ChoiceField(
        required=False,
        label='Date Range',
        choices=[
            ('', 'All Time'),
            ('this_week', 'This Week'),
            ('this_month', 'This Month'),
            ('this_year', 'This Year'),
        ],
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        label='Sort By',
        choices=[
            ('project_number', 'Project Number'),
            ('title', 'Project Title'),
            ('client__name', 'Client Name'),
            ('created_at', 'Date Created'),
            ('start_date', 'Start Date'),
            ('end_date', 'Deadline'),
            ('status', 'Status'),
            ('quoted_price', 'Quoted Price'),
        ],
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        
        # Modified layout for improved search form appearance
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-12 mb-3'),
            ),
            Row(
                Column('status', css_class='form-group col-md-3 mb-3'),
                Column('client', css_class='form-group col-md-3 mb-3'),
                Column('date_range', css_class='form-group col-md-3 mb-3'),
                Column('sort_by', css_class='form-group col-md-2 mb-3'),
                Column(Submit('submit', 'Search', css_class='btn-primary w-100'), 
                       css_class='form-group col-md-1 mb-3 d-flex align-items-end'),
            )
        )


# Field Crew Forms
class FieldCrewForm(forms.ModelForm):
    class Meta:
        model = FieldCrew
        fields = ['crew_id', 'contact_phone', 'contact_email', 'contact_address', 'color', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'contact_address': forms.Textarea(attrs={'rows': 2}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color'}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            TabHolder(
                Tab('Crew Information',
                    Row(
                        Column('crew_id', css_class='form-group col-md-12 mb-3'),
                    ),
                    Row(
                        Column('contact_phone', css_class='form-group col-md-6 mb-3'),
                        Column('contact_email', css_class='form-group col-md-6 mb-3'),
                    ),
                    Row(
                        Column('contact_address', css_class='form-group col-md-9 mb-3'),
                        Column('color', css_class='form-group col-md-3 mb-3'),
                    ),
                    Row(
                        Column('notes', css_class='form-group col-md-12 mb-3'),
                    ),
                    HTML('<hr><h5>Crew Members</h5><p class="text-muted">You can add crew members after saving</p>'),
                ),
                Tab('Vehicle Information',
                    HTML('<p class="text-muted">Vehicle information can be added after saving the crew</p>'),
                ),
                Tab('Survey Equipment',
                    HTML('<p class="text-muted">Survey equipment can be added after saving the crew</p>'),
                    HTML('<hr><h5>Total Stations</h5>'),
                    HTML('<hr><h5>GPS Receivers</h5>'),
                    HTML('<hr><h5>Data Collectors</h5>'),
                ),
                Tab('Network & Connectivity',
                    HTML('<h5>Mobile Hotspots</h5><p class="text-muted">Add after saving the crew</p>'),
                    HTML('<hr><h5>RTK Network Credentials</h5><p class="text-muted">Add after saving the crew</p>'),
                ),
            ),
            FormActions(
                Submit('submit', 'Save Field Crew', css_class='btn-primary'),
                Button('cancel', 'Cancel', css_class='btn-secondary', onclick="window.history.back()"),
            )
        )


class CrewMemberForm(forms.ModelForm):
    class Meta:
        model = CrewMember
        fields = ['name', 'position', 'phone', 'email']


class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['make', 'model', 'year', 'license_plate', 'tag_renewal_date', 'last_oil_change', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'tag_renewal_date': forms.DateInput(attrs={'type': 'date'}),
            'last_oil_change': forms.DateInput(attrs={'type': 'date'}),
        }


class TotalStationForm(forms.ModelForm):
    class Meta:
        model = TotalStation
        fields = ['model_number', 'last_calibration']
        widgets = {
            'last_calibration': forms.DateInput(attrs={'type': 'date'}),
        }


class GpsReceiverForm(forms.ModelForm):
    class Meta:
        model = GpsReceiver
        fields = ['model_number', 'receiver_type']


class DataCollectorForm(forms.ModelForm):
    class Meta:
        model = DataCollector
        fields = ['model_number', 'has_ts_module', 'has_gps_module', 'software_version']


class MobileHotspotForm(forms.ModelForm):
    class Meta:
        model = MobileHotspot
        fields = ['make_model', 'phone_number', 'network_name', 'network_password']


class RtkNetworkForm(forms.ModelForm):
    class Meta:
        model = RtkNetwork
        fields = ['network_name', 'username', 'password']


# Create formsets for Field Crew related models
CrewMemberFormSet = inlineformset_factory(
    FieldCrew, CrewMember, form=CrewMemberForm, extra=1, can_delete=True
)

TotalStationFormSet = inlineformset_factory(
    FieldCrew, TotalStation, form=TotalStationForm, extra=1, can_delete=True
)

GpsReceiverFormSet = inlineformset_factory(
    FieldCrew, GpsReceiver, form=GpsReceiverForm, extra=1, can_delete=True
)

DataCollectorFormSet = inlineformset_factory(
    FieldCrew, DataCollector, form=DataCollectorForm, extra=1, can_delete=True
)

MobileHotspotFormSet = inlineformset_factory(
    FieldCrew, MobileHotspot, form=MobileHotspotForm, extra=1, can_delete=True
)

RtkNetworkFormSet = inlineformset_factory(
    FieldCrew, RtkNetwork, form=RtkNetworkForm, extra=1, can_delete=True
)

class FieldCrewSearchForm(forms.Form):
    search = forms.CharField(
        required=False, 
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search field crews...', 
            'class': 'form-control bg-medium text-light'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-11 mb-0'),
                Column(
                    Submit('submit', 'Search', css_class='btn-primary w-100 h-100'), 
                    css_class='form-group col-md-1 mb-0 d-flex align-items-end'
                ),
            )
        )

class GateCodeForm(forms.ModelForm):
    class Meta:
        model = GateCode
        fields = ['community_name', 'gate_code', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        
        self.helper.layout = Layout(
            Row(
                Column('community_name', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('gate_code', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-3'),
            ),
            FormActions(
                Submit('submit', 'Save Gate Code', css_class='btn-primary'),
                Button('cancel', 'Cancel', css_class='btn-secondary', onclick="window.history.back()"),
            )
        )

class GateCodeSearchForm(forms.Form):
    search = forms.CharField(
        required=False, 
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search gate codes...', 
            'class': 'form-control bg-medium text-light'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-11 mb-0'),
                Column(
                    Submit('submit', 'Search', css_class='btn-primary w-100 h-100'), 
                    css_class='form-group col-md-1 mb-0 d-flex align-items-end'
                ),
            )
        )

# Calendar Event Forms
class CalendarEventForm(forms.ModelForm):
    """Form for creating and editing calendar events"""
    
    class Meta:
        model = CalendarEvent
        fields = [
            'title', 'project', 'field_crew', 'start_time', 'end_time',
            'all_day', 'location', 'notes'
        ]
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-md-3'
        self.helper.field_class = 'col-md-9'
        
        # Filter active projects for the dropdown
        self.fields['project'].queryset = Project.objects.filter(
            status__in=['admin', 'field_ready', 'in_progress', 'mapping', 'construction_ongoing']
        ).order_by('project_number')
        
        self.helper.layout = Layout(
            Row(
                Column('title', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('project', css_class='form-group col-md-6 mb-3'),
                Column('field_crew', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('start_time', css_class='form-group col-md-5 mb-3'),
                Column('end_time', css_class='form-group col-md-5 mb-3'),
                Column('all_day', css_class='form-group col-md-2 mb-3 d-flex align-items-center'),
            ),
            Row(
                Column('location', css_class='form-group col-md-12 mb-3'),
            ),
            Row(
                Column('notes', css_class='form-group col-md-12 mb-3'),
            ),
            FormActions(
                Submit('submit', 'Save Event', css_class='btn-primary'),
                Button('cancel', 'Cancel', css_class='btn-secondary', onclick="window.history.back()"),
            )
        )
    
    def clean(self):
        """Validate start and end times"""
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and start_time > end_time:
            self.add_error('end_time', 'End time must be after start time')
        
        return cleaned_data

class CalendarEventSearchForm(forms.Form):
    """Form for filtering calendar events"""
    search = forms.CharField(
        required=False, 
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Search events...', 
            'class': 'form-control bg-medium text-light'
        })
    )
    field_crew = forms.ModelChoiceField(
        required=False,
        label='Field Crew',
        queryset=FieldCrew.objects.all(),
        empty_label="All Crews",
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    project = forms.ModelChoiceField(
        required=False,
        label='Project',
        queryset=Project.objects.all(),
        empty_label="All Projects",
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    date_range = forms.ChoiceField(
        required=False,
        label='Date Range',
        choices=[
            ('', 'Current View'),
            ('today', 'Today'),
            ('this_week', 'This Week'),
            ('this_month', 'This Month'),
            ('next_month', 'Next Month'),
        ],
        widget=forms.Select(attrs={'class': 'form-select bg-medium text-light'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'form-inline'
        
        # Filter active projects for the dropdown
        self.fields['project'].queryset = Project.objects.filter(
            status__in=['admin', 'field_ready', 'in_progress', 'mapping', 'construction_ongoing']
        ).order_by('project_number')
        
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-3 mb-3'),
                Column('field_crew', css_class='form-group col-md-3 mb-3'),
                Column('project', css_class='form-group col-md-3 mb-3'),
                Column('date_range', css_class='form-group col-md-2 mb-3'),
                Column(Submit('submit', 'Filter', css_class='btn-primary w-100'), 
                       css_class='form-group col-md-1 mb-3 d-flex align-items-end'),
            )
        )

class OrdinanceForm(forms.ModelForm):
    class Meta:
        model = Ordinance
        fields = ['name', 'description', 'is_url', 'url', 'document']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-3'
        self.helper.field_class = 'col-lg-9'
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('description', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('is_url', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('url', css_class='form-group col-md-12 mb-0 url-field'),
                css_class='form-row'
            ),
            Row(
                Column('document', css_class='form-group col-md-12 mb-0 document-field'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', 'Save', css_class='btn btn-primary'),
                css_class='text-right'
            )
        )        