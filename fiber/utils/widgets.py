from django import forms


class FiberTextarea(forms.Textarea):
    def render(self, name, value, attrs=None):
        attrs['class'] = 'fiber-editor'
        return super(FiberTextarea, self).render(name, value, attrs)
