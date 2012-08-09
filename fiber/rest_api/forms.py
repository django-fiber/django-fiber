from django import forms


POSITION_CHOICES = sorted((item, item) for item in ['before', 'after', 'inside'])


class MovePageForm(forms.Form):

    position = forms.ChoiceField(choices=POSITION_CHOICES)
    target_node_id = forms.IntegerField()


class MovePageContentItemForm(forms.Form):

    before_page_content_item_id = forms.IntegerField(required=False)
    block_name = forms.CharField()
