"""
Monkey patches to fix Python 3.14 compatibility issues with Django 4.2.7
"""
import sys

# Only apply patches on Python 3.14+
if sys.version_info >= (3, 14):
    import django.template.context
    import django.template.base
    
    # Patch Context.__copy__ to avoid 'super' object dicts error
    if hasattr(django.template.context.Context, '__copy__'):
        _original_context_copy = django.template.context.Context.__copy__
        
        def _patched_context_copy(self):
            """Patched Context copy method for Python 3.14"""
            new_context = type(self)()
            # Safely copy dicts attribute
            if hasattr(self, 'dicts'):
                if isinstance(self.dicts, list):
                    new_context.dicts = self.dicts[:]
                else:
                    try:
                        new_context.dicts = list(self.dicts) if hasattr(self.dicts, '__iter__') else [dict(self.dicts)]
                    except:
                        new_context.dicts = [{}]
            else:
                new_context.dicts = [{}]
            
            # Copy other attributes
            for key, value in self.__dict__.items():
                if key != 'dicts':
                    try:
                        setattr(new_context, key, value)
                    except (AttributeError, TypeError):
                        pass
            return new_context
        
        django.template.context.Context.__copy__ = _patched_context_copy
    
    # Patch RequestContext - actually, don't patch it as it should work fine
    # The issue might be elsewhere, so we'll let it use the original implementation
    pass

