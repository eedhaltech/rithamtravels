from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class BlogPost(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    excerpt = models.TextField(max_length=500, blank=True)
    image = models.ImageField(upload_to='blog/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_published = models.BooleanField(default=False)
    views = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blog_posts'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

