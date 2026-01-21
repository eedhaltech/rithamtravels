from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import BlogPost


class BlogListView(ListView):
    model = BlogPost
    template_name = 'blog/blog_list.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        return BlogPost.objects.filter(is_published=True)


class BlogDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blog_detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
    def get_object(self):
        obj = super().get_object()
        # Don't auto-increment views here, let JavaScript handle it
        # after user has spent some time on the page
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get related posts (exclude current post, get 4 most recent)
        context['related_posts'] = BlogPost.objects.filter(
            is_published=True
        ).exclude(
            id=self.object.id
        ).order_by('-created_at')[:4]
        return context


@csrf_exempt
@require_POST
def increment_view_count(request, slug):
    """API endpoint to increment blog post view count"""
    try:
        post = get_object_or_404(BlogPost, slug=slug, is_published=True)
        post.views += 1
        post.save(update_fields=['views'])
        return JsonResponse({'success': True, 'views': post.views})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)