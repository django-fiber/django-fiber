from django import forms
from django.utils.translation import ugettext_lazy as _

from mptt.forms import TreeNodeChoiceField

from app_settings import TEMPLATE_CHOICES
from models import Page, ContentItem
from utils.urls import is_quoted_url


if len(TEMPLATE_CHOICES) == 0:
    template_choices = [('', _('Default template'))]
else:
    template_choices = TEMPLATE_CHOICES


class ContentItemAdminForm(forms.ModelForm):

    class Meta:
        model = ContentItem


class PageForm(forms.ModelForm):

    parent = TreeNodeChoiceField(queryset=Page.tree.all(), level_indicator=3*unichr(160), empty_label='---------', required=False)
    template_name = forms.ChoiceField(choices=template_choices, required=False, label=_('Template'))
    redirect_page = TreeNodeChoiceField(label=_('Redirect page'), queryset=Page.objects.filter(redirect_page__isnull=True), level_indicator=3*unichr(160), empty_label='---------', required=False)

    class Meta:
        model = Page

    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        if len(TEMPLATE_CHOICES) > 0:
            self.fields['template_name'] = forms.ChoiceField(choices=TEMPLATE_CHOICES, required=False, label=_('Template'))

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
