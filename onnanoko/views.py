from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import Series, Group, Tag, Character, Image, SiteSetting
from .serializers import SeriesSerializer, GroupSerializer, TagSerializer, CharacterSerializer, ImageSerializer
from django.db.models import Prefetch, Q, Count
from django.views.generic import ListView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
import json
from django.utils.decorators import method_decorator
from django import forms
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .forms import UserProfileForm, CustomPasswordChangeForm, AccountDeleteForm
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from PIL import Image as PILImage
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .models import Tag, Character, Series, Group, Image, SiteSetting
from django.shortcuts import get_object_or_404
from django.views import View
from django.core.paginator import Paginator
from django.http import JsonResponse
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile

# Create your views here.

class IsAuthenticatedOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    pass

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff

class SeriesViewSet(viewsets.ModelViewSet):
    queryset = Series.objects.all()
    serializer_class = SeriesSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class TagViewSet(viewsets.ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']

class CharacterViewSet(viewsets.ModelViewSet):
    queryset = Character.objects.select_related('series').prefetch_related('groups', 'tags', 'images')
    serializer_class = CharacterSerializer
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_2d', 'series', 'groups', 'tags']
    search_fields = ['name', 'description']

class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.select_related('uploader').prefetch_related('characters', 'tags')
    serializer_class = ImageSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['is_approved', 'tags', 'characters']
    search_fields = ['description', 'uploader__username']

    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)

class CharacterListView(ListView):
    model = Character
    template_name = 'onnanoko/character_list.html'
    context_object_name = 'characters'
    paginate_by = 20

    def get_queryset(self):
        qs = Character.objects.select_related('series').prefetch_related('groups', 'tags', 'images').all()
        search = self.request.GET.get('search')
        type_filter = self.request.GET.get('type')

        if search:
            qs = qs.filter(
                Q(name__icontains=search)
                | Q(description__icontains=search)
                | Q(tags__name__icontains=search)
                | Q(series__name__icontains=search)
                | Q(groups__name__icontains=search)
            )
        if type_filter == '2d':
            qs = qs.filter(is_2d=True)
        elif type_filter == '3d':
            qs = qs.filter(is_2d=False)
        # If type_filter is 'all' or empty, show all types
        
        return qs.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected'] = {
            'search': self.request.GET.get('search', ''),
            'type': self.request.GET.get('type', 'all'),
        }
        return context

class CharacterDetailView(DetailView):
    model = Character
    template_name = 'onnanoko/character_detail.html'
    context_object_name = 'character'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        return Character.objects.select_related('series').prefetch_related('groups', 'tags', 'images')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        character = self.object
        other_girls = Character.objects.filter(groups__in=character.groups.all()).exclude(id=character.id).distinct()
        context['other_girls'] = other_girls
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {
                'title': 'Home',
                'url': reverse('character_list'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>'
            },
            {
                'title': 'Characters',
                'url': reverse('character_list'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>'
            },
            {
                'title': character.name,
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>'
            }
        ]
        
        return context

class ImageGalleryView(ListView):
    model = Image
    template_name = 'onnanoko/image_gallery.html'
    context_object_name = 'images'
    paginate_by = 24

    def get_queryset(self):
        qs = Image.objects.select_related('uploader').prefetch_related('characters', 'tags').filter(is_approved=True)
        search = self.request.GET.get('search')
        
        if search:
            qs = qs.filter(
                Q(description__icontains=search)
                | Q(illustrator__icontains=search)
                | Q(uploader__username__icontains=search)
                | Q(characters__name__icontains=search)
                | Q(tags__name__icontains=search)
            ).distinct()
        
        return qs.order_by('-uploaded_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['selected'] = {
            'search': self.request.GET.get('search', ''),
        }
        return context

class ImageDetailView(DetailView):
    model = Image
    template_name = 'onnanoko/image_detail.html'
    context_object_name = 'image'

    def get_queryset(self):
        qs = Image.objects.select_related('uploader').prefetch_related('characters', 'tags')
        if not self.request.user.is_staff:
            qs = qs.filter(is_approved=True)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        img = self.object
        # Related images that share any character, excluding current
        related = Image.objects.filter(characters__in=img.characters.all()).exclude(id=img.id).filter(is_approved=True).distinct()[:12]
        context['related_images'] = related
        context['can_delete'] = self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user == img.uploader)
        context['can_edit'] = self.request.user.is_authenticated and (self.request.user.is_staff or self.request.user == img.uploader)
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {
                'title': 'Home',
                'url': reverse('character_list'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>'
            },
            {
                'title': 'Gallery',
                'url': reverse('image_gallery'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>'
            },
            {
                'title': f'Image #{img.id}',
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>'
            }
        ]
        
        return context

class ImageDeleteView(View):
    def post(self, request, pk):
        image = get_object_or_404(Image, pk=pk)
        if not request.user.is_authenticated or not (request.user.is_staff or request.user == image.uploader):
            messages.error(request, 'You do not have permission to delete this image.')
            return redirect('image_detail', pk=pk)
        image.delete()
        messages.success(request, 'Image deleted.')
        return redirect('image_gallery')

class TagExploreView(TemplateView):
    template_name = 'onnanoko/explore.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_slug = kwargs.get('slug')
        tag = Tag.objects.get(slug=tag_slug)
        characters = (Character.objects.select_related('series')
                      .prefetch_related('groups', 'tags', 'images')
                      .filter(tags=tag).distinct())
        images = (Image.objects.select_related('uploader')
                  .prefetch_related('characters', 'tags')
                  .filter(tags=tag, is_approved=True)
                  .order_by('-uploaded_at'))
        context.update({
            'mode': 'tag',
            'tag': tag,
            'title': f'Tag: {tag.name}',
            'characters': characters,
            'images': images,
        })
        return context

class GroupExploreView(TemplateView):
    template_name = 'onnanoko/explore.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        group_slug = kwargs.get('slug')
        group = Group.objects.get(slug=group_slug)
        characters = (Character.objects.select_related('series')
                      .prefetch_related('groups', 'tags', 'images')
                      .filter(groups=group).distinct())
        images = (Image.objects.select_related('uploader')
                  .prefetch_related('characters', 'tags')
                  .filter(characters__groups=group, is_approved=True)
                  .distinct()
                  .order_by('-uploaded_at'))
        context.update({
            'mode': 'group',
            'group': group,
            'title': f'Group: {group.name}',
            'characters': characters,
            'images': images,
        })
        return context

class SeriesExploreView(TemplateView):
    template_name = 'onnanoko/explore.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        series_slug = kwargs.get('slug')
        series = Series.objects.get(slug=series_slug)
        characters = (Character.objects.select_related('series')
                      .prefetch_related('groups', 'tags', 'images')
                      .filter(series=series).distinct())
        images = (Image.objects.select_related('uploader')
                  .prefetch_related('characters', 'tags')
                  .filter(characters__series=series, is_approved=True)
                  .distinct()
                  .order_by('-uploaded_at'))
        context.update({
            'mode': 'series',
            'series': series,
            'title': f'Series: {series.name}',
            'characters': characters,
            'images': images,
        })
        return context

class ImageUploadForm(forms.Form):
    characters = forms.ModelMultipleChoiceField(queryset=Character.objects.all(), required=False, widget=forms.SelectMultiple)
    tags = forms.ModelMultipleChoiceField(queryset=Tag.objects.all(), required=False, widget=forms.SelectMultiple)
    description = forms.CharField(widget=forms.Textarea, required=False)
    illustrator = forms.CharField(max_length=128, required=False, widget=forms.TextInput(attrs={'placeholder': 'Artist/Illustrator name'}))

class CharacterForm(forms.ModelForm):
    class Meta:
        model = Character
        fields = [
            'name','is_2d','series','groups','tags','birth_date','age','height_cm','weight_kg',
            'bust_cm','waist_cm','hips_cm','description','primary_image'
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'groups': forms.SelectMultiple,
            'tags': forms.SelectMultiple,
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Short bio / description'}),
            'age': forms.NumberInput(attrs={'placeholder': 'Age'}),
            'height_cm': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Height (cm)'}),
            'weight_kg': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Weight (kg)'}),
            'bust_cm': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Bust (cm)'}),
            'waist_cm': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Waist (cm)'}),
            'hips_cm': forms.NumberInput(attrs={'step': '0.1', 'placeholder': 'Hips (cm)'}),
        }

class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ['description', 'characters', 'tags', 'is_approved', 'illustrator']
        widgets = {
            'characters': forms.SelectMultiple,
            'tags': forms.SelectMultiple,
            'description': forms.Textarea,
            'illustrator': forms.TextInput(attrs={'placeholder': 'Artist/Illustrator name'}),
        }

@method_decorator(login_required, name='dispatch')
class ImageUploadView(TemplateView):
    template_name = 'onnanoko/image_upload.html'

    def get(self, request, *args, **kwargs):
        form = ImageUploadForm()
        context = {
            'form': form,
            'all_characters': Character.objects.all().order_by('name'),
            'all_tags': Tag.objects.all().order_by('name'),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = ImageUploadForm(request.POST)
        errors = []
        if form.is_valid():
            files = request.FILES.getlist('files')
            characters = form.cleaned_data['characters']
            tags = form.cleaned_data['tags']
            description = form.cleaned_data['description']
            illustrator = form.cleaned_data['illustrator']
            for f in files:
                if f.content_type not in ['image/jpeg', 'image/png', 'image/webp']:
                    errors.append(f'{f.name}: Only JPEG, PNG, and WEBP images are allowed.')
                    continue
                if f.size > 5 * 1024 * 1024:
                    errors.append(f'{f.name}: Each file must be under 5MB.')
                    continue
                try:
                    img = PILImage.open(f)
                    img.verify()
                except Exception:
                    errors.append(f'{f.name}: Invalid image file.')
                    continue
                image = Image.objects.create(
                    file=f,
                    uploader=request.user,
                    description=description,
                    illustrator=illustrator,
                    is_approved=request.user.is_staff,
                )
                image.characters.set(characters)
                image.tags.set(tags)
                image.save()
            if not errors:
                return self.render_to_response({'form': ImageUploadForm(), 'success': True, 'auto_approved': request.user.is_staff})
            else:
                return self.render_to_response({'form': form, 'errors': errors})
        return self.render_to_response({'form': form})

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class CharacterCreateView(TemplateView):
    template_name = 'onnanoko/character_create.html'

    def get(self, request, *args, **kwargs):
        form = CharacterForm()
        context = {
            'form': form,
            'all_tags': Tag.objects.all().order_by('name'),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = CharacterForm(request.POST, request.FILES)
        if form.is_valid():
            character = form.save()
            return redirect('character_detail', slug=character.slug)
        return self.render_to_response({'form': form})

class LoginView(TemplateView):
    template_name = 'auth/login.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('user_dashboard')
        return self.render_to_response({'form': AuthenticationForm()})

    def post(self, request, *args, **kwargs):
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('user_dashboard')
        return self.render_to_response({'form': form})

class LogoutView(TemplateView):
    def post(self, request, *args, **kwargs):
        logout(request)
        return redirect('character_list')

class RegisterView(TemplateView):
    template_name = 'auth/register.html'

    def dispatch(self, request, *args, **kwargs):
        if not SiteSetting.get_solo().allow_self_registration:
            return redirect('login')
        if request.user.is_authenticated:
            return redirect('user_dashboard')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return self.render_to_response({'form': UserCreationForm()})

    def post(self, request, *args, **kwargs):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('user_dashboard')
        return self.render_to_response({'form': form})

@method_decorator(login_required, name='dispatch')
class UserDashboardView(TemplateView):
    template_name = 'auth/dashboard.html'

    def get(self, request, *args, **kwargs):
        user_images = Image.objects.filter(uploader=request.user)
        uploads = user_images.order_by('-uploaded_at')[:24]
        approved_count = user_images.filter(is_approved=True).count()
        pending_count = user_images.filter(is_approved=False).count()
        
        return self.render_to_response({
            'user': request.user, 
            'uploads': uploads,
            'approved_count': approved_count,
            'pending_count': pending_count,
        })

@method_decorator(login_required, name='dispatch')
class UserProfileView(TemplateView):
    template_name = 'auth/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_form'] = UserProfileForm(instance=self.request.user)

        
        # Calculate user stats
        user_images = Image.objects.filter(uploader=self.request.user)
        context['user_stats'] = {
            'total_uploads': user_images.count(),
            'approved_count': user_images.filter(is_approved=True).count(),
            'pending_count': user_images.filter(is_approved=False).count(),
        }
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {
                'title': 'Home',
                'url': reverse('character_list'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>'
            },
            {
                'title': 'Dashboard',
                'url': reverse('user_dashboard'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>'
            },
            {
                'title': 'Account Settings',
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"></path>'
            }
        ]
        return context

@method_decorator(login_required, name='dispatch')
class UserProfileUpdateView(View):
    def post(self, request, *args, **kwargs):
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated successfully!')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.title()}: {error}')
        return redirect('user_profile')

@method_decorator(login_required, name='dispatch')
class UserPasswordChangeView(TemplateView):
    template_name = 'auth/password_change.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CustomPasswordChangeForm(user=self.request.user)
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {
                'title': 'Home',
                'url': reverse('character_list'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>'
            },
            {
                'title': 'Dashboard',
                'url': reverse('user_dashboard'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>'
            },
            {
                'title': 'Change Password',
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m-2-2a2 2 0 00-2 2m2-2h2m-6 9a2 2 0 01-2-2V9a2 2 0 012-2h8a2 2 0 012 2v8a2 2 0 01-2 2h-8z"></path>'
            }
        ]
        return context
    
    def post(self, request, *args, **kwargs):
        form = CustomPasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            # Update session to prevent logout
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(request, form.user)
            messages.success(request, 'Your password has been changed successfully!')
            return redirect('user_dashboard')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

@method_decorator(login_required, name='dispatch')
class UserAccountDeleteView(TemplateView):
    template_name = 'auth/account_delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = AccountDeleteForm(user=self.request.user)
        
        # Calculate user stats
        user_images = Image.objects.filter(uploader=self.request.user)
        context['user_stats'] = {
            'total_uploads': user_images.count(),
            'approved_count': user_images.filter(is_approved=True).count(),
            'pending_count': user_images.filter(is_approved=False).count(),
        }
        
        # Breadcrumbs
        context['breadcrumbs'] = [
            {
                'title': 'Home',
                'url': reverse('character_list'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path>'
            },
            {
                'title': 'Dashboard',
                'url': reverse('user_dashboard'),
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>'
            },
            {
                'title': 'Delete Account',
                'icon': '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path>'
            }
        ]
        return context
    
    def post(self, request, *args, **kwargs):
        form = AccountDeleteForm(user=request.user, data=request.POST)
        if form.is_valid():
            # Delete the user account
            username = request.user.username
            request.user.delete()
            messages.success(request, f'Account "{username}" has been permanently deleted.')
            return redirect('character_list')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{error}')
            context = self.get_context_data()
            context['form'] = form
            return self.render_to_response(context)

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class CharacterUpdateView(TemplateView):
    template_name = 'onnanoko/character_edit.html'

    def get_object(self):
        return Character.objects.get(slug=self.kwargs['slug'])

    def get(self, request, *args, **kwargs):
        character = self.get_object()
        form = CharacterForm(instance=character)
        context = {
            'form': form,
            'character': character,
            'all_tags': Tag.objects.all().order_by('name'),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        character = self.get_object()
        form = CharacterForm(request.POST, request.FILES, instance=character)
        if form.is_valid():
            form.save()
            messages.success(request, 'Character updated.')
            return redirect('character_detail', slug=character.slug)
        return self.render_to_response({'form': form, 'character': character})

class ImageUpdateView(TemplateView):
    template_name = 'onnanoko/image_edit.html'

    def dispatch(self, request, *args, **kwargs):
        self.image = Image.objects.select_related('uploader').get(pk=kwargs['pk'])
        if not request.user.is_authenticated or not (request.user.is_staff or request.user == self.image.uploader):
            messages.error(request, 'You do not have permission to edit this image.')
            return redirect('image_detail', pk=self.image.pk)
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = ImageForm(instance=self.image)
        
        # Serialize characters and tags for JavaScript
        all_characters = [{'id': c.id, 'name': c.name} for c in Character.objects.all().order_by('name')]
        all_tags = [{'id': t.id, 'name': t.name} for t in Tag.objects.all().order_by('name')]
        
        context = {
            'form': form,
            'image': self.image,
            'all_characters': json.dumps(all_characters),
            'all_tags': json.dumps(all_tags),
        }
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = ImageForm(request.POST, instance=self.image)
        if form.is_valid():
            image = form.save()
            # Save illustrator field
            image.illustrator = form.cleaned_data.get('illustrator', '')
            image.save()
            messages.success(request, 'Image updated successfully.')
            return redirect('image_detail', pk=self.image.pk)
        
        # Serialize characters and tags for JavaScript on form error
        all_characters = [{'id': c.id, 'name': c.name} for c in Character.objects.all().order_by('name')]
        all_tags = [{'id': t.id, 'name': t.name} for t in Tag.objects.all().order_by('name')]
        
        context = {
            'form': form, 
            'image': self.image,
            'all_characters': json.dumps(all_characters),
            'all_tags': json.dumps(all_tags),
        }
        return self.render_to_response(context)

# Admin Panel Views
class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = ['allow_self_registration']
        widgets = {
            'allow_self_registration': forms.CheckboxInput(attrs={'class': 'form-checkbox'})
        }

class UserManagementForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        }

class BulkApprovalForm(forms.Form):
    action = forms.ChoiceField(choices=[('approve', 'Approve'), ('reject', 'Delete')], widget=forms.Select)
    image_ids = forms.CharField(widget=forms.HiddenInput)

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminPanelView(TemplateView):
    template_name = 'admin/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Dashboard stats
        context['stats'] = {
            'total_users': User.objects.count(),
            'total_characters': Character.objects.count(),
            'total_images': Image.objects.count(),
            'pending_images': Image.objects.filter(is_approved=False).count(),
            'recent_uploads': Image.objects.order_by('-uploaded_at')[:5],
        }
        
        return context

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminUsersView(ListView):
    model = User
    template_name = 'admin/users.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        qs = User.objects.annotate(
            upload_count=Count('uploaded_images')
        ).order_by('-date_joined')
        
        search = self.request.GET.get('search')
        if search:
            qs = qs.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        
        return qs

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminUserEditView(TemplateView):
    template_name = 'admin/user_edit.html'

    def get_object(self):
        return get_object_or_404(User, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.get_object()
        context['user_obj'] = user
        context['form'] = UserManagementForm(instance=user)
        context['user_uploads'] = Image.objects.filter(uploader=user).order_by('-uploaded_at')[:10]
        return context

    def post(self, request, *args, **kwargs):
        user = self.get_object()
        form = UserManagementForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('admin_users')
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminPendingUploadsView(ListView):
    model = Image
    template_name = 'admin/pending_uploads.html'
    context_object_name = 'images'
    paginate_by = 24

    def get_queryset(self):
        return Image.objects.filter(is_approved=False).select_related('uploader').prefetch_related('characters', 'tags').order_by('-uploaded_at')

    def post(self, request, *args, **kwargs):
        form = BulkApprovalForm(request.POST)
        if form.is_valid():
            action = form.cleaned_data['action']
            image_ids = form.cleaned_data['image_ids'].split(',')
            image_ids = [int(id) for id in image_ids if id.isdigit()]
            
            images = Image.objects.filter(id__in=image_ids, is_approved=False)
            
            if action == 'approve':
                images.update(is_approved=True)
                messages.success(request, f'Approved {images.count()} images.')
            elif action == 'reject':
                count = images.count()
                images.delete()
                messages.success(request, f'Deleted {count} images.')
        
        return redirect('admin_pending_uploads')

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminSiteSettingsView(TemplateView):
    template_name = 'admin/site_settings.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        settings = SiteSetting.get_solo()
        context['form'] = SiteSettingsForm(instance=settings)
        context['settings'] = settings
        return context

    def post(self, request, *args, **kwargs):
        settings = SiteSetting.get_solo()
        form = SiteSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'Site settings updated successfully.')
            return redirect('admin_settings')
        
        context = self.get_context_data()
        context['form'] = form
        return self.render_to_response(context)

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminContentManagementView(TemplateView):
    template_name = 'admin/content_management.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get counts and recent items
        context['content_stats'] = {
            'series_count': Series.objects.count(),
            'groups_count': Group.objects.count(),
            'tags_count': Tag.objects.count(),
            'characters_count': Character.objects.count(),
            'recent_series': Series.objects.order_by('name')[:5],
            'recent_groups': Group.objects.order_by('name')[:5],
            'recent_tags': Tag.objects.order_by('name')[:5],
        }
        
        return context

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminApproveImageView(View):
    def post(self, request, pk):
        image = get_object_or_404(Image, pk=pk)
        action = request.POST.get('action')
        
        if action == 'approve':
            image.is_approved = True
            image.save()
            messages.success(request, 'Image approved.')
        elif action == 'reject':
            image.delete()
            messages.success(request, 'Image deleted.')
        
        # Return to pending uploads or the specific image
        next_url = request.POST.get('next', 'admin_pending_uploads')
        return redirect(next_url)

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminDeleteUserView(View):
    def post(self, request, pk):
        user = get_object_or_404(User, pk=pk)
        if user == request.user:
            messages.error(request, 'You cannot delete yourself.')
        elif user.is_superuser and not request.user.is_superuser:
            messages.error(request, 'You cannot delete a superuser.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'User {username} deleted.')
        
        return redirect('admin_users')

# Quick content creation forms for admin
class QuickSeriesForm(forms.ModelForm):
    class Meta:
        model = Series
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Series name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Description'}),
        }

class QuickGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Group name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Description'}),
        }

class QuickTagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Tag name'}),
        }

@method_decorator(user_passes_test(lambda u: u.is_staff), name='dispatch')
class AdminCreateContentView(View):
    def post(self, request):
        content_type = request.POST.get('content_type')
        
        if content_type == 'series':
            form = QuickSeriesForm(request.POST)
            if form.is_valid():
                series = form.save()
                messages.success(request, f'Series "{series.name}" created.')
        elif content_type == 'group':
            form = QuickGroupForm(request.POST)
            if form.is_valid():
                group = form.save()
                messages.success(request, f'Group "{group.name}" created.')
        elif content_type == 'tag':
            form = QuickTagForm(request.POST)
            if form.is_valid():
                tag = form.save()
                messages.success(request, f'Tag "{tag.name}" created.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f'Tag creation failed: {error}')
        
        return redirect('admin_content_management')
