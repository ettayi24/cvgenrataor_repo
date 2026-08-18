
from django.contrib import admin
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [

    path('', views.index, name='home'),
    path('templates/', views.templateView, name='templates'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('signin/',views.signin,name='signin'),
    path('signout/',views.signout,name='signout'),
    # ✅ Preview CV Theme (no user data, just design preview)
    path("cv/preview/<int:template_id>/", views.preview_cv, name="preview_cv"),
    # Preview logged-in user's CV (uses session)
    # path("cv/preview/<int:template_id>/", views.render_cv, name="cv"),

    # Preview a specific CV by ID
    path("cv/preview/<int:template_id>/<int:cv_id>/", views.render_cv, name="render_cv_by_id"),
    #form paths---
    path("create_cv/",views.create_cv,name="create_cv"),
    path("personal/<int:cv_id>/", views.add_personal_details, name="add_personal_details"),
    path("education/<int:cv_id>", views.add_education, name="add_education"),
    path("experience/<int:cv_id>", views.add_experience, name="add_experience"),
    path("skills/<int:cv_id>", views.add_skill, name="add_skill"),
    path("languages/<int:cv_id>", views.add_language, name="add_language"),
    path("certificates/<int:cv_id>", views.add_certificate, name="add_certificate"),
    path("projects/<int:cv_id>", views.add_project, name="add_project"),
    path("interests/<int:cv_id>", views.add_interest, name="add_interest"),
    path("references/<int:cv_id>", views.add_reference, name="add_reference"),
    path("summary/<int:cv_id>/", views.cv_summary, name="summary"),

    #admin/user
    path("user/dashboard/", views.user_dashboard, name="user_dashboard"),
    path("cv/delete/<int:cv_id>/", views.delete_cv, name="delete_cv"),

    # path('adminpage',views.adminPage,name='adminpage'),
    path('adminsignup',views.admin_signup,name='adminsignup'),
    path("adminlogin", views.admin_login, name="adminlogin"),
    path('admindashboard',views.adminPage,name='admindashboard'),
    path("adminlogout/", views.admin_logout, name="adminlogout"),
    path("add-template", views.admin_add_template, name="admin_add_template"),
    path("admindashboard/view-cvs/", views.admin_view_cvs, name="admin_view_cvs"),
    path('custom_admin/manage-users/', views.manage_users, name='admin_manage_users'),
    path('custom_admin/user/<int:user_id>/view/', views.view_user, name='view_user'),
    path('custom_admin/user/<int:user_id>/delete/', views.delete_user, name='delete_user'),

     # 🟢 Admin preview CV
    path("myadmin/preview-cv/<int:cv_id>/<int:template_id>/", views.admin_preview_cv, name="admin_preview_cv"),
    path("admindashboard/view-cvs/delete/<int:cv_id>/", views.admin_delete_cv, name="admin_delete_cv"),



    #downloadpdf
    # Before
path("cv/<int:cv_id>/download/", views.download_cv, name="download_cv"),

# After
path("cv/<int:cv_id>/download/<int:template_id>/", views.download_cv, name="download_cv"),


]