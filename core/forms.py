from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # Honeypot field: real visitors never fill this in (hidden via CSS).
    website = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "company", "phone", "service_interest", "message"]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@company.com"}),
            "company": forms.TextInput(attrs={"placeholder": "Company (optional)"}),
            "phone": forms.TextInput(attrs={"placeholder": "Phone (optional)"}),
            "message": forms.Textarea(
                attrs={"placeholder": "Tell us about your project...", "rows": 6}
            ),
        }

    def clean_website(self):
        value = self.cleaned_data.get("website")
        if value:
            raise forms.ValidationError("Spam detected.")
        return value
