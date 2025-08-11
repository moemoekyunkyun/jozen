from django.urls import path
from . import views

urlpatterns = [
    path('', views.CharacterListView.as_view(), name='character_list'),
    path('character/new/', views.CharacterCreateView.as_view(), name='character_create'),
    path('character/<slug:slug>/edit/', views.CharacterUpdateView.as_view(), name='character_edit'),
    path('character/<slug:slug>/', views.CharacterDetailView.as_view(), name='character_detail'),
    path('gallery/', views.ImageGalleryView.as_view(), name='image_gallery'),
    path('image/<int:pk>/', views.ImageDetailView.as_view(), name='image_detail'),
    path('image/<int:pk>/edit/', views.ImageUpdateView.as_view(), name='image_edit'),
    path('image/<int:pk>/delete/', views.ImageDeleteView.as_view(), name='image_delete'),
    path('upload/', views.ImageUploadView.as_view(), name='image_upload'),
    path('tag/<slug:slug>/', views.TagExploreView.as_view(), name='tag_explore'),
    path('group/<slug:slug>/', views.GroupExploreView.as_view(), name='group_explore'),
    path('series/<slug:slug>/', views.SeriesExploreView.as_view(), name='series_explore'),
    # Auth
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('me/', views.UserDashboardView.as_view(), name='user_dashboard'),
    
    # User Account Management
    path('me/profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('me/profile/update/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),
    path('me/password/', views.UserPasswordChangeView.as_view(), name='user_password_change'),
    path('me/delete/', views.UserAccountDeleteView.as_view(), name='user_account_delete'),
    
    # Admin Panel
    path('admin-panel/', views.AdminPanelView.as_view(), name='admin_panel'),
    path('admin-panel/users/', views.AdminUsersView.as_view(), name='admin_users'),
    path('admin-panel/users/<int:pk>/edit/', views.AdminUserEditView.as_view(), name='admin_user_edit'),
    path('admin-panel/users/<int:pk>/delete/', views.AdminDeleteUserView.as_view(), name='admin_user_delete'),
    path('admin-panel/pending-uploads/', views.AdminPendingUploadsView.as_view(), name='admin_pending_uploads'),
    path('admin-panel/image/<int:pk>/approve/', views.AdminApproveImageView.as_view(), name='admin_approve_image'),
    path('admin-panel/settings/', views.AdminSiteSettingsView.as_view(), name='admin_settings'),
    path('admin-panel/content/', views.AdminContentManagementView.as_view(), name='admin_content_management'),
    path('admin-panel/content/create/', views.AdminCreateContentView.as_view(), name='admin_create_content'),
]
