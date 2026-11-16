from django import forms


class BookingForm(forms.Form):
    name = forms.CharField(max_length=100, strip=True)
    contact = forms.CharField(max_length=150, strip=True)
    topic = forms.CharField(max_length=1000, required=False, strip=True)
    # приманка для ботів: людина це поле не бачить і не заповнює
    website = forms.CharField(required=False)

    def clean_website(self):
        if self.cleaned_data['website']:
            raise forms.ValidationError('spam')
        return ''
