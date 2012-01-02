from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import get_language

from mptt.forms import TreeNodeChoiceField

from app_settings import TEMPLATE_CHOICES
from models import Page, ContentItem
from utils.urls import is_quoted_url


class ContentItemAdminForm(forms.ModelForm):

    class Meta:
        model = ContentItem


class PageForm(forms.ModelForm):

    parent = TreeNodeChoiceField(queryset=Page.tree.all(), level_indicator=3*unichr(160), empty_label='---------', required=False)
    redirect_page = TreeNodeChoiceField(label=_('Redirect page'), queryset=Page.objects.filter(redirect_page__isnull=True), level_indicator=3*unichr(160), empty_label='---------', required=False)

    class Meta:
        model = Page

    def __init__(self, *args, **kw):
        super(PageForm, self).__init__(*args, **kw)

        translation_of_qs = Page.objects.filter(language__exact=settings.LANGUAGE_CODE)
        if 'instance' in kw and kw['instance']:
            translation_of_qs = translation_of_qs.exclude(pk__exact=kw['instance'].pk)


        self.fields['translation_of'].choices = [(p.pk, unicode(p)) for p in translation_of_qs]
        self.fields['translation_of'].choices.insert(0, ('', '--------'))

    def clean_title(self):
        """
        Strips extra whitespace
        """
        return self.cleaned_data.get('title', '').strip()

    def clean_redirect_page(self):
        if self.cleaned_data['redirect_page']:
            try:
                if self.cleaned_data['url'] and is_quoted_url(self.cleaned_data['url']):
                    raise forms.ValidationError(_('A named url can\'t be combined with a redirect page'))
            except KeyError:
                pass
        return self.cleaned_data['redirect_page']


class FiberAdminPageForm(PageForm):
    template_name = forms.ChoiceField(choices=TEMPLATE_CHOICES, required=False, label=_('Template'))
