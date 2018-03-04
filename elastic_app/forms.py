from django import forms


class TagsField(forms.MultipleChoiceField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('choices', ())
        super(TagsField, self).__init__(*args, **kwargs)

    def valid_value(self, value):
        return True


class XmlForm(forms.Form):
    docfile = forms.FileField(label='Select a file')


class SearchForm(forms.Form):
    search = forms.CharField(label='Title')
    # keywords = TagsField(required=False)
