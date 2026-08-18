from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register([Admin,User,Template,CVtable,Personal_Details,Education,Experience,Skill,Language,Certificate,Project,Interest,Reference,])

