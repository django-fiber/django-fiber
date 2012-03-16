from django import forms

POSITION_CHOICES = ['before', 'after', 'inside']

class PageForm(forms.Form):
    
    action = forms.CharField()
    position = forms.ChoiceField(choices=POSITION_CHOICES)
    target_node_id = forms.IntegerField()
