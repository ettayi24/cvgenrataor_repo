from django import forms
from .models import (
    CVtable, Personal_Details, Education, Experience,
    Skill, Language, Certificate, Project,
    Interest, Reference,Admin,Template
)
from django.forms import modelformset_factory

#admin
class AdminForm(forms.ModelForm):
    class Meta:
        model = Admin
        fields = ['Name', 'Email', 'Password']
        widgets = {
            'Name': forms.TextInput(attrs={
                'placeholder': 'Enter full name',
                'class': 'form-control form-control-lg rounded-3 shadow-sm border-0'
            }),
            'Email': forms.EmailInput(attrs={
                'placeholder': 'Enter email address',
                'class': 'form-control form-control-lg rounded-3 shadow-sm border-0'
            }),
            'Password': forms.PasswordInput(attrs={
                'placeholder': 'Create a secure password',
                'class': 'form-control form-control-lg rounded-3 shadow-sm border-0'
            }),
        }


class TemplateForm(forms.ModelForm):
    class Meta:
        model = Template
        fields = ["Template_Name", "Preview_image"]
        widgets = {
            "Template_Name": forms.TextInput(attrs={
                "class": "form-control form-control-lg rounded-3 shadow-sm border-0",
                "placeholder": "Enter template name"
            }),
            "Preview_image": forms.ClearableFileInput(attrs={
                "class": "form-control form-control-lg rounded-3 shadow-sm border-0"
            }),
        }



class CVForm(forms.ModelForm):
    class Meta:
        model = CVtable
        fields = ['CV_Name', 'Template_id']
        widgets = {
            "CV_Name": forms.TextInput(attrs={"placeholder": "Enter CV Name"}),
        }


class PersonalDetailsForm(forms.ModelForm):
    class Meta:
        model = Personal_Details
        exclude = ['CV_id']
        widgets = {
            "First_Name": forms.TextInput(attrs={"placeholder": "First Name"}),
            "Last_Name": forms.TextInput(attrs={"placeholder": "Last Name"}),
            "Email": forms.EmailInput(attrs={"placeholder": "Email Address"}),
            "Contact": forms.TextInput(attrs={"placeholder": "Phone Number"}),
            "Address": forms.Textarea(attrs={"placeholder": "Full Address", "rows": 3}),
            "linked_in": forms.URLInput(attrs={"placeholder": "LinkedIn Profile URL"}),
            "github": forms.URLInput(attrs={"placeholder": "GitHub Profile URL"}),
            "Profile_Image": forms.ClearableFileInput(),  # ✅ File upload handled
        }


class EducationForm(forms.ModelForm):
    class Meta:
        model = Education
        exclude = ['CV_id']
        widgets = {
            "Degree": forms.TextInput(attrs={"placeholder": "Degree / Course"}),
            "University": forms.TextInput(attrs={"placeholder": "University / Institute"}),
            "Start_year": forms.NumberInput(attrs={"placeholder": "Start Year"}),
            "End_year": forms.NumberInput(attrs={"placeholder": "End Year"}),
            "Description": forms.Textarea(attrs={"placeholder": "Description", "rows": 2}),
        }


class ExperienceForm(forms.ModelForm):
    class Meta:
        model = Experience
        exclude = ['CV_id', 'Experience_id']   # ✅ Exclude the AutoField
        widgets = {
            "Company_Name": forms.TextInput(attrs={
                "placeholder": "Company Name",
                "class": "form-control"
            }),
            "Start_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d"
            ),
            "End_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d"
            ),
            "Description": forms.Textarea(attrs={
                "placeholder": "Role / Responsibilities",
                "rows": 3,
                "class": "form-control"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ Allow blank End_date without failing validation
        self.fields['End_date'].required = False



class SkillForm(forms.ModelForm):
    class Meta:
        model = Skill
        exclude = ['CV_id','Skill_id']
        widgets = {
            "Skill_Name": forms.TextInput(attrs={
                "placeholder": "Skill Name",
                "class": "form-control"
            }),
            "Proficiency_level": forms.Select(
                choices=Skill._meta.get_field("Proficiency_level").choices,
                attrs={"class": "form-control"}
            ),
        }



class LanguageForm(forms.ModelForm):
    class Meta:
        model = Language
        exclude = ['CV_id']
        widgets = {
            "Language_Name": forms.TextInput(
                attrs={"placeholder": "Language Name", "class": "form-control"}
            ),
            "Proficiency": forms.Select(
                attrs={"class": "form-control"},
                choices=[
                    ("", "Select"),   # ✅ This will show instead of ---------
                    ("Basic", "Basic"),
                    ("Conversational", "Conversational"),
                    ("Fluent", "Fluent"),
                    ("Native", "Native"),
                ]
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # ✅ force "Select" to show instead of Django's default '---------'
        self.fields["Proficiency"].empty_label = None




class CertificateForm(forms.ModelForm):
    class Meta:
        model = Certificate
        exclude = ['CV_id']
        widgets = {
            "Certificate_Name": forms.TextInput(attrs={"placeholder": "Certificate Name"}),
            "Organization": forms.TextInput(attrs={"placeholder": "Issuing Organization"}),
            "Year": forms.NumberInput(attrs={"placeholder": "Year of Completion"}),
        }


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        exclude = ['CV_id']
        widgets = {
            "Project_Name": forms.TextInput(attrs={"placeholder": "Project Title"}),
            "Description": forms.Textarea(attrs={"placeholder": "Project Description", "rows": 3}),
            "Link": forms.URLInput(attrs={"placeholder": "Project Link (if any)"}),
        }


# 9️⃣ Interest
from django import forms
from django.forms import modelformset_factory
from .models import Interest

# Single form for Interest
class InterestForm(forms.ModelForm):
    class Meta:
        model = Interest
        exclude = ['CV_id']
        widgets = {
            "Interest_Name": forms.TextInput(
                attrs={"placeholder": "Interest / Hobby", "class": "form-control"}
            ),
        }

# Formset for multiple Interests
InterestFormSet = modelformset_factory(
    Interest,
    form=InterestForm,
    extra=0,
    can_delete=True
)


class ReferenceForm(forms.ModelForm):
    class Meta:
        model = Reference
        exclude = ['CV_id']
        widgets = {
            "Reference_Name": forms.TextInput(attrs={"placeholder": "Reference Full Name"}),
            "Designation": forms.TextInput(attrs={"placeholder": "Job Title / Position"}),
            "Company": forms.TextInput(attrs={"placeholder": "Company Name"}),
            "Contact": forms.TextInput(attrs={"placeholder": "Phone Number"}),
            "Email": forms.EmailInput(attrs={"placeholder": "Reference Email"}),
        }





# Define Formsets for multiple entries
EducationFormSet = modelformset_factory(Education, form=EducationForm, extra=1, can_delete=True)





