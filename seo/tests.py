"""
Property-based tests for SEO template tags
Feature: website-seo-optimization
"""

from django.test import TestCase, RequestFactory, Client
from django.template import Context, Template
from django.conf import settings
from seo.templatetags.seo_tags import seo_title, seo_description, seo_keywords, clean_text
from seo.models import SEOConfig, PageSEO, SEORedirect
import string

class SEOTemplateTagsUnitTests(TestCase):
    """Unit tests for specific SEO template tag behaviors"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_seo_title_with_empty_inputs(self):
        """Test SEO title generation with empty inputs"""
        result = seo_title("", "")
        self.assertEqual(result, "Ritham Tours & Travels")
    
    def test_seo_description_with_html_content(self):
        """Test SEO description with HTML content"""
        html_desc = "<p>This is a <strong>test</strong> description with <a href='#'>links</a></p>"
        result = seo_description(html_desc)
        self.assertNotIn('<', result)
        self.assertNotIn('>', result)
    
    def test_absolute_url_generation(self):
        """Test absolute URL generation"""
        from seo.templatetags.seo_tags import absolute_url
        
        request = self.factory.get('/')
        context = {'request': request}
        
        result = absolute_url(context, '/test-page/')
        self.assertTrue(result.startswith('http'))
        self.assertIn('/test-page/', result)
    
    def test_og_image_url_fallback(self):
        """Test Open Graph image URL with fallback"""
        from seo.templatetags.seo_tags import og_image_url
        
        request = self.factory.get('/')
        context = {'request': request}
        
        # Test with no image (should use default logo)
        result = og_image_url(context, None)
        self.assertIn('logo_ritham.png', result)
        
        # Test with custom image
        result_custom = og_image_url(context, '/custom/image.jpg')
        self.assertIn('/custom/image.jpg', result_custom)
    
    def test_page_type_to_og_type_mapping(self):
        """Test page type to Open Graph type conversion"""
        from seo.templatetags.seo_tags import page_type_to_og_type
        
        self.assertEqual(page_type_to_og_type('home'), 'website')
        self.assertEqual(page_type_to_og_type('article'), 'article')
        self.assertEqual(page_type_to_og_type('blog'), 'article')
        self.assertEqual(page_type_to_og_type('product'), 'product')
        self.assertEqual(page_type_to_og_type('tour'), 'product')
        self.assertEqual(page_type_to_og_type('unknown'), 'website')
    
    def test_clean_text_functionality(self):
        """Test text cleaning functionality"""
        # Test HTML removal
        html_text = "<script>alert('test')</script><p>Clean this <b>text</b></p>"
        result = clean_text(html_text)
        self.assertNotIn('<script>', result)
        self.assertNotIn('<p>', result)
        self.assertNotIn('<b>', result)
        self.assertIn('Clean this text', result)
        
        # Test whitespace normalization
        spaced_text = "Too    many     spaces"
        result = clean_text(spaced_text)
        self.assertEqual(result, "Too many spaces")
    
    def test_seo_keywords_list_input(self):
        """Test SEO keywords with list input"""
        keywords_list = ['travel', 'tours', 'booking']
        result = seo_keywords(keywords_list)
        self.assertIn('travel', result)
        self.assertIn('tours', result)
        self.assertIn('booking', result)
    
    def test_seo_title_truncation(self):
        """Test SEO title truncation for long titles"""
        long_title = "This is a very long page title that should be truncated to fit within SEO limits"
        result = seo_title(long_title, "Ritham Tours")
        self.assertLessEqual(len(result), 60)
        self.assertIn("...", result)
    
    def test_seo_description_truncation(self):
        """Test SEO description truncation for long descriptions"""
        long_desc = "This is a very long description that should be truncated to fit within the 160 character limit for SEO meta descriptions. It contains multiple sentences and should be cut at a word boundary."
        result = seo_description(long_desc)
        self.assertLessEqual(len(result), 160)
        self.assertIn("...", result)
    
    def test_seo_title_length_validation(self):
        """Test SEO title length validation with various inputs"""
        # Test normal title
        result = seo_title("Home Page", "Ritham Tours")
        self.assertLessEqual(len(result), 60)
        self.assertGreater(len(result), 0)
        
        # Test empty title
        result = seo_title("", "Ritham Tours")
        self.assertEqual(result, "Ritham Tours")
        
        # Test very long title
        long_title = "This is an extremely long page title that definitely exceeds the recommended SEO limit"
        result = seo_title(long_title, "Ritham Tours")
        self.assertLessEqual(len(result), 60)
    
    def test_seo_description_length_validation(self):
        """Test SEO description length validation"""
        # Test normal description
        desc = "This is a normal description"
        result = seo_description(desc)
        self.assertLessEqual(len(result), 160)
        self.assertGreater(len(result), 0)
        
        # Test empty description (should use default)
        result = seo_description("")
        self.assertGreater(len(result), 0)
        self.assertIn("Ritham Tours", result)
    
    def test_seo_fallback_behavior(self):
        """Test SEO fallback behavior for missing values"""
        # Test title fallback
        result = seo_title("", None)
        self.assertEqual(result, "Ritham Tours & Travels")
        
        # Test description fallback
        result = seo_description(None)
        self.assertIn("Ritham Tours & Travels", result)
        
        # Test keywords fallback
        result = seo_keywords(None)
        self.assertIn("tours", result.lower())
        self.assertIn("travel", result.lower())
    """Unit tests for specific SEO template tag behaviors"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_seo_title_with_empty_inputs(self):
        """Test SEO title generation with empty inputs"""
        result = seo_title("", "")
        self.assertEqual(result, "Ritham Tours & Travels")
    
    def test_seo_description_with_html_content(self):
        """Test SEO description with HTML content"""
        html_desc = "<p>This is a <strong>test</strong> description with <a href='#'>links</a></p>"
        result = seo_description(html_desc)
        self.assertNotIn('<', result)
        self.assertNotIn('>', result)
    
    def test_absolute_url_generation(self):
        """Test absolute URL generation"""
        from seo.templatetags.seo_tags import absolute_url
        
        request = self.factory.get('/')
        context = {'request': request}
        
        result = absolute_url(context, '/test-page/')
        self.assertTrue(result.startswith('http'))
        self.assertIn('/test-page/', result)
    
    def test_og_image_url_fallback(self):
        """Test Open Graph image URL with fallback"""
        from seo.templatetags.seo_tags import og_image_url
        
        request = self.factory.get('/')
        context = {'request': request}
        
        # Test with no image (should use default logo)
        result = og_image_url(context, None)
        self.assertIn('logo_ritham.png', result)
        
        # Test with custom image
        result_custom = og_image_url(context, '/custom/image.jpg')
        self.assertIn('/custom/image.jpg', result_custom)
    
    def test_page_type_to_og_type_mapping(self):
        """Test page type to Open Graph type conversion"""
        from seo.templatetags.seo_tags import page_type_to_og_type
        
        self.assertEqual(page_type_to_og_type('home'), 'website')
        self.assertEqual(page_type_to_og_type('article'), 'article')
        self.assertEqual(page_type_to_og_type('blog'), 'article')
        self.assertEqual(page_type_to_og_type('product'), 'product')
        self.assertEqual(page_type_to_og_type('tour'), 'product')
        self.assertEqual(page_type_to_og_type('unknown'), 'website')
    
    def test_clean_text_functionality(self):
        """Test text cleaning functionality"""
        # Test HTML removal
        html_text = "<script>alert('test')</script><p>Clean this <b>text</b></p>"
        result = clean_text(html_text)
        self.assertNotIn('<script>', result)
        self.assertNotIn('<p>', result)
        self.assertNotIn('<b>', result)
        self.assertIn('Clean this text', result)
        
        # Test whitespace normalization
        spaced_text = "Too    many     spaces"
        result = clean_text(spaced_text)
        self.assertEqual(result, "Too many spaces")
    
    def test_seo_keywords_list_input(self):
        """Test SEO keywords with list input"""
        keywords_list = ['travel', 'tours', 'booking']
        result = seo_keywords(keywords_list)
        self.assertIn('travel', result)
        self.assertIn('tours', result)
        self.assertIn('booking', result)
    
    def test_seo_title_truncation(self):
        """Test SEO title truncation for long titles"""
        long_title = "This is a very long page title that should be truncated to fit within SEO limits"
        result = seo_title(long_title, "Ritham Tours")
        self.assertLessEqual(len(result), 60)
        self.assertIn("...", result)
    
    def test_seo_description_truncation(self):
        """Test SEO description truncation for long descriptions"""
        long_desc = "This is a very long description that should be truncated to fit within the 160 character limit for SEO meta descriptions. It contains multiple sentences and should be cut at a word boundary."
        result = seo_description(long_desc)
        self.assertLessEqual(len(result), 160)
        self.assertIn("...", result)


class SEOModelsTests(TestCase):
    """Tests for SEO models"""
    
    def test_seo_config_creation(self):
        """Test SEO configuration model creation"""
        config = SEOConfig.objects.create(
            site_name="Test Site",
            site_description="Test description",
            is_active=True
        )
        
        self.assertEqual(config.site_name, "Test Site")
        self.assertTrue(config.is_active)
        self.assertEqual(str(config), "SEO Config - Test Site")
    
    def test_seo_config_active_singleton(self):
        """Test that only one SEO config can be active"""
        config1 = SEOConfig.objects.create(
            site_name="Config 1",
            is_active=True
        )
        
        config2 = SEOConfig.objects.create(
            site_name="Config 2",
            is_active=True
        )
        
        # Refresh from database
        config1.refresh_from_db()
        
        # Only config2 should be active
        self.assertFalse(config1.is_active)
        self.assertTrue(config2.is_active)
    
    def test_page_seo_creation(self):
        """Test PageSEO model creation"""
        page_seo = PageSEO.objects.create(
            page_path="/test/",
            page_name="Test Page",
            title="Test Title",
            description="Test description"
        )
        
        self.assertEqual(page_seo.page_path, "/test/")
        self.assertEqual(page_seo.get_effective_title(), "Test Title")
        self.assertEqual(page_seo.get_effective_description(), "Test description")
    
    def test_page_seo_effective_methods(self):
        """Test PageSEO effective value methods"""
        page_seo = PageSEO.objects.create(
            page_path="/tour/",
            page_name="Goa Tour",
            page_type="tour"
        )
        
        # Test effective title (should use page_name when title is empty)
        self.assertEqual(page_seo.get_effective_title(), "Goa Tour")
        
        # Test effective description (should generate default for tour)
        description = page_seo.get_effective_description()
        self.assertIn("Goa Tour", description)
        self.assertIn("Ritham Tours", description)
        
        # Test effective keywords (should generate default for tour)
        keywords = page_seo.get_effective_keywords()
        self.assertIn("tour package", keywords)
        self.assertIn("goa tour", keywords)
    
    def test_seo_redirect_creation(self):
        """Test SEO redirect model creation"""
        redirect = SEORedirect.objects.create(
            old_path="/old-page/",
            new_path="/new-page/",
            redirect_type="301"
        )
        
        self.assertEqual(redirect.old_path, "/old-page/")
        self.assertEqual(redirect.new_path, "/new-page/")
        self.assertEqual(redirect.redirect_type, "301")
        self.assertTrue(redirect.is_active)


class SEOMixinsTests(TestCase):
    """Tests for SEO mixins"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_seo_mixin_basic_functionality(self):
        """Test basic SEO mixin functionality"""
        from seo.mixins import SEOMixin
        
        class TestView(SEOMixin):
            seo_title = "Test Title"
            seo_description = "Test description"
        
        view = TestView()
        view.request = self.factory.get('/')
        seo_context = view.get_seo_context()
        
        self.assertEqual(seo_context['title'], "Test Title")
        self.assertEqual(seo_context['description'], "Test description")
        self.assertEqual(seo_context['page_type'], "website")
    
    def test_home_seo_mixin(self):
        """Test HomeSEOMixin specific functionality"""
        from seo.mixins import HomeSEOMixin
        
        class TestHomeView(HomeSEOMixin):
            pass
        
        view = TestHomeView()
        view.request = self.factory.get('/')
        seo_context = view.get_seo_context()
        
        self.assertIn("Ritham Tours", seo_context['title'])
        self.assertIn("travel", seo_context['description'].lower())
        self.assertEqual(seo_context['canonical_url'], "/")
    
    def test_blog_seo_mixin(self):
        """Test BlogSEOMixin specific functionality"""
        from seo.mixins import BlogSEOMixin
        
        class TestBlogView(BlogSEOMixin):
            pass
        
        view = TestBlogView()
        view.request = self.factory.get('/blog/test/')
        seo_context = view.get_seo_context()
        
        self.assertEqual(seo_context['page_type'], "article")
        self.assertIn("travel blog", seo_context['keywords'])
    
    def test_contact_seo_mixin(self):
        """Test ContactSEOMixin specific functionality"""
        from seo.mixins import ContactSEOMixin
        
        class TestContactView(ContactSEOMixin):
            pass
        
        view = TestContactView()
        view.request = self.factory.get('/contact/')
        seo_context = view.get_seo_context()
        
        self.assertIn("Contact", seo_context['title'])
        self.assertEqual(seo_context['page_type'], "contact")
        self.assertEqual(seo_context['canonical_url'], "/contact/")


class SEOContextProcessorTests(TestCase):
    """Tests for SEO context processor"""
    
    def setUp(self):
        self.factory = RequestFactory()
    
    def test_seo_context_processor(self):
        """Test SEO context processor functionality"""
        from seo.context_processors import seo_context
        
        request = self.factory.get('/')
        context = seo_context(request)
        
        self.assertIn('site_seo', context)
        site_seo = context['site_seo']
        
        self.assertIn('site_name', site_seo)
        self.assertIn('company_name', site_seo)
        self.assertIn('default_og_image', site_seo)
        self.assertEqual(site_seo['site_name'], 'Ritham Tours & Travels')


class SEOIntegrationTests(TestCase):
    """Integration tests for complete SEO functionality"""
    
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
    
    def test_seo_template_tags_functionality(self):
        """Test that SEO template tags work correctly"""
        from seo.templatetags.seo_tags import seo_title, seo_description, absolute_url, og_image_url
        
        # Test template tags directly
        title = seo_title("Test Page", "Test Site")
        self.assertEqual(title, "Test Page | Test Site")
        
        description = seo_description("Test description")
        self.assertEqual(description, "Test description")
        
        # Test absolute URL generation
        request = self.factory.get('/')
        context = {'request': request}
        abs_url = absolute_url(context, '/test/')
        self.assertTrue(abs_url.startswith('http'))
        self.assertIn('/test/', abs_url)
        
        # Test OG image URL
        og_img = og_image_url(context, None)
        self.assertIn('logo_ritham.png', og_img)