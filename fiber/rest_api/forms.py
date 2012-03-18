from django import forms

POSITION_CHOICES = sorted((item, item) for item in ['before', 'after', 'inside'])

class MovePageForm(forms.Form):
    
    position = forms.ChoiceField(choices=POSITION_CHOICES)
    target_node_id = forms.IntegerField()
