from django.shortcuts import render
from .models import *
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from functools import wraps


# user forms
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import CVtable
from .forms import (
    CVForm, PersonalDetailsForm, EducationForm, ExperienceForm,
    SkillForm, LanguageForm, CertificateForm, ProjectForm, InterestForm, ReferenceForm,AdminForm,TemplateForm
)
from .forms import InterestFormSet,EducationFormSet



from django.http import HttpResponse, Http404
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from .models import (
    CVtable, Personal_Details, Skill, Language, Interest,
    Experience, Education, Project, Certificate, Reference,Admin
)
import asyncio
import tempfile
from django.http import FileResponse, Http404
from django.template.loader import render_to_string
from django.conf import settings
from playwright.async_api import async_playwright
from .models import (
    Personal_Details, Skill, Language, Interest,
    Experience, Education, Project, Certificate, Reference
)

async def generate_pdf(full_html, output_path):
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Add full HTML content
        await page.set_content(full_html, wait_until="networkidle")

        # Generate PDF in A4 with proper margins
        await page.pdf(
    path=output_path,
    format="A4",
    print_background=True,
    scale=0.75,   # 👈 add this
    margin={
        "top": "5mm",
        "bottom": "5mm",
        "left": "5mm",
        "right": "5mm"
    }
)

        await browser.close()


def download_cv(request, cv_id, template_id):
    try:
        personal = Personal_Details.objects.filter(CV_id=cv_id).last()
    except Personal_Details.DoesNotExist:
        raise Http404("CV not found")

    context = {
        "personal": personal,
        "skills": Skill.objects.filter(CV_id=cv_id),
        "languages": Language.objects.filter(CV_id=cv_id),
        "interests": Interest.objects.filter(CV_id=cv_id),
        "experience": Experience.objects.filter(CV_id=cv_id),
        "education": Education.objects.filter(CV_id=cv_id),
        "projects": Project.objects.filter(CV_id=cv_id),
        "certificates": Certificate.objects.filter(CV_id=cv_id),
        "references": Reference.objects.filter(CV_id=cv_id),
    }

    template_path = f"cvtheme/theme{template_id}.html"
    html_string = render_to_string(template_path, context, request=request)

    base_url = request.build_absolute_uri("/")
    full_html = f"""
    <!DOCTYPE html>
    <html>
      <head>
        <base href="{base_url}">
        <style>
          @page {{ size: A4; margin: 20mm; }}
          body {{
            width: 210mm;
            min-height: 297mm;
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            box-sizing: border-box;
          }}
          .cv-container {{
            width: 100%;
            min-height: 500mm;
            padding: 10mm;
          }}
        </style>
      </head>
      <body>
        <div class="cv-container">
            {html_string}
        </div>
      </body>
    </html>
    """

    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    asyncio.run(generate_pdf(full_html, tmp.name))

    return FileResponse(
        open(tmp.name, "rb"),
        as_attachment=True,
        filename=f"{personal.First_Name}_{personal.Last_Name}_CV.pdf",
        content_type="application/pdf"
    )



# ✅ Custom session-based login_required decorator
def session_login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get("user_id"):
            messages.warning(request, "⚠️ Please log in to continue")
            return redirect(f"/signin/?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_login_required(view_func):
    """
    Custom decorator to ensure admin is logged in.
    Checks session for 'admin_id'. If not present → redirect to admin login.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get("admin_id"):  # session key set at login
            return redirect("adminlogin")       # redirect to your login page
        return view_func(request, *args, **kwargs)
    return wrapper

# Create your views here.
def index(request):
    return render(request,"index.html")


def contact(request):
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")

#admin/user


#admin register
def adminRegister(request):
    pass

@admin_login_required
def adminPage(request):
    return render(request,'custom_admin/admindashboard.html')


def admin_logout(request):
    """
    Logs out the admin by clearing session data.
    """
    # Clear all session data
    request.session.flush()

    # Optional: Add a message
    messages.success(request, "You have been successfully logged out ✅")

    # Redirect to admin login page
    return redirect("home")


def admin_signup(request):
    if request.method == "POST":
        form = AdminForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)

            # ⚡ Optional: hash the password if your Admin model doesn’t handle it
            # If you are not using Django's built-in User, you should hash manually
            # from django.contrib.auth.hashers import make_password
            # admin.Password = make_password(form.cleaned_data['Password'])

            admin.save()
            messages.success(request, "Admin account created successfully! Please log in.")
            return redirect("home")  # change to your login URL name
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AdminForm()

    return render(request, "custom_admin/adminsignup.html", {"form": form})



def admin_login(request):
    print("🟢 admin_login view called")  # debug

    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")

        print(f"👉 Submitted Username: {email}")  # debug
        print(f"👉 Submitted Password: {password}")  # debug

        # check admin
        admin = Admin.objects.filter(Email=email, Password=password).first()

        if admin:
            print(f"✅ Admin found: ID={admin.pk}, Name={admin.Name}")  # debug

            # store session
            request.session["admin_id"] = admin.pk
            request.session["admin_name"] = admin.Name

            print("📌 Session stored:", request.session.get("admin_id"), request.session.get("admin_name"))  # debug

            messages.success(request, f"Welcome back, {admin.Name} 👋")
            return redirect("admindashboard")  # redirect to dashboard/home
        else:
            print("❌ No matching admin found")  # debug
            messages.error(request, "Invalid email or password ❌")

    else:
        print("ℹ️ GET request → showing login page")  # debug

    return render(request, "custom_admin/adminlogin.html")


@admin_login_required
def admin_add_template(request):
    if request.method == "POST":
        form = TemplateForm(request.POST, request.FILES)
        if form.is_valid():
            template = form.save()
            messages.success(request, f"✅ Template '{template.Template_Name}' added successfully!")
            return redirect("admindashboard")
        else:
            messages.error(request, "❌ Please fix the errors below")
    else:
        form = TemplateForm()

    return render(request, "custom_admin/add_template.html", {"form": form})

from django.db.models import Q

@admin_login_required
def admin_view_cvs(request):
    # Get filters from query params
    order = request.GET.get("order", "newest")
    search = request.GET.get("search", "").strip()
    template_filter = request.GET.get("template", "")

    # Base queryset
    cvs = CVtable.objects.select_related("User_id", "Template_id")

    # Apply search (by CV name or user name)
    if search:
        cvs = cvs.filter(
            Q(CV_Name__icontains=search) |
            Q(User_id__Full_Name__icontains=search) |
            Q(User_id__Email__icontains=search)
        )

    # Apply template filter
    if template_filter:
        cvs = cvs.filter(Template_id__Template_Name__icontains=template_filter)

    # Ordering
    if order == "oldest":
        cvs = cvs.order_by("Created_at")
    else:  # newest first
        cvs = cvs.order_by("-Created_at")

    return render(request, "custom_admin/view_cvs.html", {
        "cvs": cvs,
        "order": order,
        "search": search,
        "template_filter": template_filter,
    })


#for admin preview
@admin_login_required
def admin_preview_cv(request, cv_id, template_id=1):
    cv = CVtable.objects.filter(CV_id=cv_id).last()
    if not cv:
        messages.error(request, "CV not found")
        return redirect("admin_view_cvs")

    personal = Personal_Details.objects.filter(CV_id=cv).last()
    education = Education.objects.filter(CV_id=cv)
    experience = Experience.objects.filter(CV_id=cv)
    skills = Skill.objects.filter(CV_id=cv)
    languages = Language.objects.filter(CV_id=cv)
    certificates = Certificate.objects.filter(CV_id=cv)
    projects = Project.objects.filter(CV_id=cv)
    interests = Interest.objects.filter(CV_id=cv)
    references = Reference.objects.filter(CV_id=cv)

    return render(request, "cvtheme/cv.html", {
        "cv": cv,
        "personal": personal,
        "education": education,
        "experience": experience,
        "skills": skills,
        "languages": languages,
        "certificates": certificates,
        "projects": projects,
        "interests": interests,
        "references": references,
        "selected_template": str(template_id),
    })



@admin_login_required
def admin_delete_cv(request, cv_id):
    cv = get_object_or_404(CVtable, pk=cv_id)
    cv.delete()
    messages.success(request, f"CV '{cv.CV_Name}' deleted successfully ✅")
    return redirect("admin_view_cvs")

@admin_login_required
def manage_users(request):
    users = User.objects.all().order_by('-User_id')  # latest first
    return render(request, "custom_admin/manage_users.html", {"users": users})

# ----------------------------
# View a single user
# ----------------------------
@admin_login_required
def view_user(request, user_id):
    user = get_object_or_404(User, User_id=user_id)
    return render(request, 'custom_admin/view_user.html', {
        'user': user
    })

# Delete a user
# ----------------------------
@admin_login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, User_id=user_id)
    if request.method == "POST":
        user.delete()
        messages.success(request, f"User '{user.Full_Name}' has been deleted successfully.")
        return redirect('admin_manage_users')  # replace with your manage users page URL name
    return render(request, 'custom_admin/confirm_delete.html', {
        'user': user
    })

# -----------User-------------------------------------------------

@session_login_required
def user_dashboard(request):
    user_id = request.session.get("user_id")
    cvs = CVtable.objects.filter(User_id=user_id).select_related("Template_id").order_by("Created_at")

    return render(request, "userdashboard.html", {"cvs": cvs})

@session_login_required
def delete_cv(request, cv_id):
    # fetch CV, make sure it belongs to the logged-in user
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))

    # delete it
    cv.delete()

    messages.success(request, "✅ CV deleted successfully.")
    return redirect("user_dashboard")



def signup(request):
    if request.method == "POST":
        name = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(Email=email).exists():
           return render(request, "sign-up.html", {
                "error": "An account with this email already exists."
            })

        # if email does not exist, save new user
        data = User(Full_Name=name, Email=email, Password=password)
        data.save()
        return render(request, "signup_success.html")

    # if GET request
    return render(request, "sign-up.html")



def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        # ✅ Check POST first, fallback to GET
        next_url = request.POST.get("next") or request.GET.get("next")

        user = User.objects.filter(Email=email, Password=password).first()

        if user:
            request.session["user_id"] = user.User_id
            request.session["user_name"] = user.Full_Name

            messages.success(request, f"Welcome back, {user.Full_Name}! 🎉")

            if next_url:
                return redirect(next_url)
            return redirect("home")
        else:
            messages.error(request, "Invalid email or password")
            return redirect("home")

    # ✅ Pass next forward to the template so it doesn’t get lost
    return render(request, "index.html", {"next": request.GET.get("next")})





def signout(request):
    # Clear all session data
    request.session.flush()
    messages.success(request, " You have been logged out successfully.")  # ✅ 
    # Redirect back to login page
    return redirect("home")

def templateView(request):
    templates = Template.objects.all()  # fetch all templates from DB
    return render(request, 'preview.html', {'templates': templates})

@session_login_required
def render_cv(request, template_id, cv_id=None):
    print("reached cv render")
    if cv_id:
        # Restrict: must belong to logged-in user
        cv = CVtable.objects.filter(
            CV_id=cv_id, 
            User_id=request.session["user_id"]
        ).last()
    else:
        session_cv_id = request.session.get("cv_id")
        if session_cv_id:
            cv = CVtable.objects.filter(
                CV_id=session_cv_id, 
                User_id=request.session["user_id"]
            ).last()
        else:
            cv = None

    if not cv:
        return HttpResponse("You do not have permission to view this CV.", status=403)
    print(cv)
    # Related objects
    personal = Personal_Details.objects.filter(CV_id=cv).last()
    education = Education.objects.filter(CV_id=cv)
    experience = Experience.objects.filter(CV_id=cv)
    skills = Skill.objects.filter(CV_id=cv)
    languages = Language.objects.filter(CV_id=cv)
    certificates = Certificate.objects.filter(CV_id=cv)
    projects = Project.objects.filter(CV_id=cv)
    interests = Interest.objects.filter(CV_id=cv)
    references = Reference.objects.filter(CV_id=cv)

    return render(request, "cvtheme/cv.html", {
        "cv": cv,
        "personal": personal,
        "education": education,
        "experience": experience,
        "skills": skills,
        "languages": languages,
        "certificates": certificates,
        "projects": projects,
        "interests": interests,
        "references": references,
        "selected_template": str(template_id),
    })


#preview theme anyone
def preview_cv(request, template_id):
    return render(request, "cvtheme/cv.html", {
        "cv": None,
        "personal": None,
        "education": [],
        "experience": [],
        "skills": [],
        "languages": [],
        "certificates": [],
        "projects": [],
        "interests": [],
        "references": [],
        "selected_template": str(template_id),
    })







def handle_cancel(request, cv):
    if cv.User_id.pk != request.session.get("user_id"):
        return redirect("user_dashboard")  # Prevent deleting someone else's CV
    
    cv.delete()
    request.session.pop("cv_id", None)
    print("data deleted",cv.pk)
    return redirect("user_dashboard")




@session_login_required
def create_cv(request):
    if request.method == "POST":

        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            request.session.pop("cv_id", None)
            return redirect("user_dashboard")

        form = CVForm(request.POST)
        if form.is_valid():
            cv = form.save(commit=False)
            cv.User_id = get_object_or_404(User, pk=request.session["user_id"])
            cv.save()

            request.session["cv_id"] = cv.CV_id

            return redirect("add_personal_details", cv_id=cv.CV_id)

    else:
        form = CVForm()

    return render(request, "forms/create_cv.html", {
        "form": form,
        "title": "Create CV",
        "step": 1,
        "progress": 10,
    })




# 2️⃣ Personal Details
@session_login_required
def add_personal_details(request, cv_id):
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))
    if request.method == "POST":
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        form = PersonalDetailsForm(request.POST,request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.CV_id = cv
            obj.save()
            return redirect("add_education", cv_id=cv.CV_id)
    else:
        form = PersonalDetailsForm()
    return render(request, "forms/personal_details.html", {
        "form": form,
        "cv": cv,
        "title": "Personal Details",
        "button_text": "Next",
        "step": 2,
        "progress": 20,
    })


# 3️⃣ Education (Formset)
@session_login_required
def add_education(request, cv_id):
    cv = get_object_or_404(CVtable, CV_id=cv_id)
    if request.method == 'POST':
         # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = EducationFormSet(request.POST, queryset=Education.objects.filter(CV_id=cv_id))
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.CV_id = cv
                instance.save()
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('add_experience', cv_id=cv.CV_id)
    else:
        formset = EducationFormSet(queryset=Education.objects.filter(CV_id=cv_id))
    return render(request, 'forms/education.html', 
        {
        'formset': formset, 
        'cv': cv,
        "title": "Educations",
        "step": 3,
        "progress": 30,
        })

# 4️⃣ experience
@session_login_required
def add_experience(request, cv_id):
    """
    Handles the Experience section of the CV creation form using a formset.
    """
    # Assuming CVtable and user authentication are set up.
    # The get_object_or_404 handles the case where the CV doesn't exist.
    cv = get_object_or_404(CVtable, CV_id=cv_id)

    ExperienceFormSet = modelformset_factory(Experience, form=ExperienceForm, extra=1, can_delete=True)

    if request.method == "POST":
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = ExperienceFormSet(request.POST, queryset=Experience.objects.filter(CV_id=cv))
        
        if formset.is_valid():
            instances = formset.save(commit=False)
            
            for instance in instances:
                instance.CV_id = cv
                instance.save()

            # Delete objects marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect("add_skill", cv_id=cv.CV_id)
        else:
            # If the formset is invalid, re-render the page with errors
            return render(request, "forms/experience.html", {
                "formset": formset,
                "cv": cv,
                "title": "Experience",
                "button_text": "Next",
                "step": 4,
                "progress": 40,
            })
    else:
        # For a GET request, initialize the formset with existing data
        formset = ExperienceFormSet(queryset=Experience.objects.filter(CV_id=cv))

    return render(request, "forms/experience.html", {
        "formset": formset,
        "cv": cv,
        "title": "Experience",
        "button_text": "Next",
        "step": 4,
        "progress": 40,
    })

# 5️⃣ skill
@session_login_required
def add_skill(request, cv_id):
    cv = get_object_or_404(CVtable, CV_id=cv_id)

    SkillFormSet = modelformset_factory(Skill, form=SkillForm, extra=1, can_delete=True)

    if request.method == "POST":
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = SkillFormSet(request.POST, queryset=Skill.objects.filter(CV_id=cv))

        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                if instance.Skill_Name:  # ✅ Only save non-empty rows
                    instance.CV_id = cv
                    instance.save()

            # Delete marked rows
            for obj in formset.deleted_objects:
                obj.delete()

            return redirect("add_language", cv_id=cv.CV_id)
        else:
            print("❌ Errors:", formset.errors)

    else:
        formset = SkillFormSet(queryset=Skill.objects.filter(CV_id=cv))

    return render(request, "forms/skill.html", {
        "formset": formset,
        "cv": cv,
        "title": "Skills",
        "button_text": "Next",
        "step": 5,
        "progress": 50,
    })




# 6️⃣ Language
from django.forms import modelformset_factory

@session_login_required
def add_language(request, cv_id):
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))

    LanguageFormSet = modelformset_factory(Language, form=LanguageForm, extra=1, can_delete=True)

    if request.method == "POST":
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = LanguageFormSet(request.POST, queryset=Language.objects.filter(CV_id=cv))

        if formset.is_valid():
            instances = formset.save(commit=False)
            
            for instance in instances:
                instance.CV_id = cv
                instance.save()

            # ✅ Delete objects marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()
            
            return redirect("add_certificate", cv_id=cv.CV_id)
        else:
            return render(request, "forms/language.html", {
                "formset": formset,
                "cv": cv,
                "title": "Languages",
                "button_text": "Next",
                "step": 6,
                "progress": 60,
            })
    else:
        formset = LanguageFormSet(queryset=Language.objects.filter(CV_id=cv))

    return render(request, "forms/language.html", {
        "formset": formset,
        "cv": cv,
        "title": "Languages",
        "button_text": "Next",
        "step": 6,
        "progress": 60,
    })


# 7️⃣ Certificate (Formset)
@session_login_required
def add_certificate(request, cv_id):
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))

    CertificateFormSet = modelformset_factory(Certificate, form=CertificateForm, extra=1, can_delete=True)

    if request.method == "POST":
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = CertificateFormSet(request.POST, queryset=Certificate.objects.filter(CV_id=cv))

        if formset.is_valid():
            instances = formset.save(commit=False)
            
            for instance in instances:
                instance.CV_id = cv
                instance.save()
            
            for obj in formset.deleted_objects:
                obj.delete()
            
            return redirect("add_project", cv_id=cv.CV_id)

        else:
            return render(request, "forms/certificate.html", {
                "formset": formset,
                "cv": cv,
                "title": "Certificates",
                "button_text": "Next",
                "step": 7,
                "progress": 70,
            })
    else:
        formset = CertificateFormSet(queryset=Certificate.objects.filter(CV_id=cv))

    return render(request, "forms/certificate.html", {
        "formset": formset,
        "cv": cv,
        "title": "Certificates",
        "button_text": "Next",
        "step": 7,
        "progress": 70,
    })


# 8️⃣ Project
def add_project(request, cv_id):
    """
    Handles the creation, editing, and deletion of projects associated with a CV.
    """
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))
    ProjectFormSet = modelformset_factory(Project, form=ProjectForm, extra=1, can_delete=True)
    
    if request.method == 'POST':
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = ProjectFormSet(request.POST, queryset=cv.project_set.all())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.CV_id = cv
                instance.save()
            
            # Handle forms marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()
            
            return redirect('add_interest', cv_id=cv.CV_id)
        
        else:
            context = {
                'formset': formset,
                'cv': cv,
                'title': "Projects",
                'button_text': "Next",
                'step': 8,
                'progress': 80,
            }
            return render(request, 'forms/project.html', context)
    
    else:
        formset = ProjectFormSet(queryset=cv.project_set.all())

    context = {
        'formset': formset,
        'cv': cv,
        'title': "Projects",
        'button_text': "Next",
        'step': 8,
        'progress': 80,
    }
    return render(request, 'forms/project.html', context)


from django.forms import modelformset_factory

# 9️ Interest
from django.forms import modelformset_factory

@session_login_required
def add_interest(request, cv_id):
    """
    Handles the creation, editing, and deletion of interests associated with a CV.
    """
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))
    InterestFormSet = modelformset_factory(Interest, form=InterestForm, extra=1, can_delete=True)

    if request.method == 'POST':
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = InterestFormSet(request.POST, queryset=cv.interest_set.all())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.CV_id = cv
                instance.save()
            
            # Handle forms marked for deletion
            for obj in formset.deleted_objects:
                obj.delete()
            
            # Assuming the next step is 'add_certificate'
            return redirect('add_reference', cv_id=cv.CV_id)
        
        else:
            context = {
                'formset': formset,
                'cv': cv,
                'title': "Interests",
                'button_text': "Next",
                'step': 9,
                'progress': 90,
            }
            return render(request, 'forms/interest.html', context)
    
    else:
        formset = InterestFormSet(queryset=cv.interest_set.all())

    context = {
        'formset': formset,
        'cv': cv,
        'title': "Interests",
        'button_text': "Next",
        'step': 9,
        'progress': 90,
    }
    return render(request, 'forms/interest.html', context)




# 🔟 Reference (Formset)
@session_login_required
def add_reference(request, cv_id):
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))
    ReferenceFormSet = modelformset_factory(Reference, form=ReferenceForm, extra=1, can_delete=True)

    if request.method == 'POST':
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        formset = ReferenceFormSet(request.POST, queryset=cv.reference_set.all())
        if formset.is_valid():
            instances = formset.save(commit=False)
            for instance in instances:
                instance.CV_id = cv  # ✅ attach foreign key
                instance.save()
            
            for obj in formset.deleted_objects:
                obj.delete()
            
            return redirect('summary', cv_id=cv.CV_id)
        else:
            print("❌ Errors:", formset.errors)  # ✅ debug why not saving
    else:
        formset = ReferenceFormSet(queryset=cv.reference_set.all())

    return render(request, 'forms/reference.html', {
        'formset': formset,
        'cv': cv,
        'title': "References",
        'button_text': "Next",
        'step': 10,
        'progress': 100,
    })




# ✅ Summary / Final Step
@session_login_required
def cv_summary(request, cv_id):
    cv = get_object_or_404(CVtable, CV_id=cv_id, User_id=request.session.get("user_id"))

    if request.method == "POST":
        # 🔴 Cancel button clicked
        if request.POST.get("action") == "cancel":
            return  handle_cancel(request, cv)
        # when user clicks "Finish" → redirect to preview or dashboard
        return redirect("preview_cv", template_id=cv.Template_id_id) # 👈 Corrected this line)

    return render(
        request,
        "forms/summary.html",
        {
            "form": None,  # no form here, just summary
            "cv": cv,
            "title": "Summary",
            "button_text": "Finish",
            "step": 10,
            "progress": 100,
        },
    )

