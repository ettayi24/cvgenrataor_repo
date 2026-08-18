from django.db import models
from django.utils import timezone

# Create your models here.
class Admin(models.Model):
    Admin_id=models.AutoField(primary_key=True)
    Name=models.CharField(max_length=100,null=False)
    Email=models.CharField(max_length=100,null=False)
    Password=models.CharField(max_length=100,null=False)

    def __str__(self):
        return f"{self.Admin_id}-{self.Name}"

class User(models.Model):
    User_id = models.AutoField(primary_key=True)
    Full_Name = models.CharField(max_length=100, null=False)
    Email = models.CharField(max_length=100, null=False)
    Password = models.CharField(max_length=100, null=False)
    created_at = models.DateTimeField(default=timezone.now, editable=False)  # ✅ new field

    def __str__(self):
        return f"{self.User_id} - {self.Full_Name}"


class Template(models.Model):
    Template_id=models.AutoField(primary_key=True)
    Template_Name=models.CharField(max_length=100,null=False)
    Preview_image=models.ImageField(upload_to='preview_images/',null=False)
    Created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.Template_id}.{self.Template_Name}"

class CVtable(models.Model):
    CV_id=models.AutoField(primary_key=True)
    User_id=models.ForeignKey(User,on_delete=models.CASCADE)#foreign key setup
    CV_Name=models.CharField(max_length=100,null=False)
    Template_id=models.ForeignKey(Template,on_delete=models.CASCADE)
    Created_at=models.DateTimeField(auto_now_add=True)
    Updated_at = models.DateTimeField(auto_now=True)   # ✅ updates every time you save()

    def __str__(self):
        return f"{self.CV_id}:{self.User_id} - {self.CV_Name}"

class Personal_Details(models.Model):
    Info_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    First_Name = models.CharField(max_length=100, null=False)
    Last_Name = models.CharField(max_length=100, null=False)
    Email = models.EmailField(max_length=100, null=False)   # ✅ Better validation
    Contact = models.CharField(max_length=15)               # ✅ IntegerField not good for phone numbers
    Address = models.CharField(max_length=500)
    linked_in = models.URLField(max_length=200, blank=True, null=True)  # ✅ Better validation
    github = models.URLField(max_length=200, blank=True, null=True)
    Profile_Image = models.ImageField(upload_to="profile_images/", null=True, blank=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.First_Name}{self.Last_Name}"


class Education(models.Model):
    Education_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    Degree = models.CharField(max_length=100)
    University = models.CharField(max_length=100)
    Start_year = models.IntegerField()
    End_year = models.IntegerField(null=True, blank=True)   # ✅ For ongoing studies
    Description = models.TextField(blank=True)              # ✅ TextField allows more space


class Experience(models.Model):
    Experience_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    Company_Name = models.CharField(max_length=100)
    Start_date = models.DateField()   # ✅ You want manual entry, not auto_now_add
    End_date = models.DateField(null=True, blank=True)   # ✅ Handle current job
    Description = models.TextField(blank=True)

    def __str__(self):
        return self.Company_Name


class Skill(models.Model):
    Skill_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    Skill_Name = models.CharField(max_length=100)
    Proficiency_level = models.CharField(
        max_length=50,
        choices=[
            ("Beginner", "Beginner"),
            ("Intermediate", "Intermediate"),
            ("Advanced", "Advanced"),
            ("Expert", "Expert")
        ]
    )   # ✅ Choices help keep consistency

    def __str__(self):
        return self.Skill_Name


class Language(models.Model):
    Language_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    Language_Name = models.CharField(max_length=100)
    Proficiency = models.CharField(
        max_length=50,
        choices=[
            ("Basic", "Basic"),
            ("Conversational", "Conversational"),
            ("Fluent", "Fluent"),
            ("Native", "Native"),
        ]
    )
    def __str__(self):
        return self.Language_Name



class Certificate(models.Model):
    Certificate_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    Certificate_Name = models.CharField(max_length=100)
    Organization = models.CharField(max_length=100)
    Year = models.IntegerField()

    def __str__(self):
        return self.Certificate_Name


class Project(models.Model):
    Project_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    Project_Name = models.CharField(max_length=100)
    Description = models.TextField(blank=True)   # ✅ Bigger description
    Link = models.URLField(max_length=200, blank=True, null=True)  # ✅ Better for links


class Interest(models.Model):
    Interest_id=models.AutoField(primary_key=True)
    CV_id=models.ForeignKey(CVtable,on_delete=models.CASCADE)
    Interest_Name=models.CharField(max_length=100)

    def __str__(self):
        return self.Interest_Name

class Reference(models.Model):
    Reference_id = models.AutoField(primary_key=True)
    CV_id = models.ForeignKey(CVtable, on_delete=models.CASCADE)
    Reference_Name = models.CharField(max_length=100)
    Designation = models.CharField(max_length=100)
    Company = models.CharField(max_length=100)   # ✅ Typo fixed ("Comapany")
    Contact = models.CharField(max_length=20)    # ✅ Phone as string
    Email = models.EmailField(max_length=100)    # ✅ Validation

    def __str__(self):
        return self.Reference_Name



