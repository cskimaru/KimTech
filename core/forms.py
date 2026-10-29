import re

from django import forms

from .models import ContactMessage, Order, Package


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


DOMAIN_RE = re.compile(r"^(?=.{3,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z]{2,24}$")


class OrderForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput())  # honeypot
    services = forms.MultipleChoiceField(
        choices=Order.SERVICE_CHOICES, widget=forms.CheckboxSelectMultiple, label="What do you need?"
    )
    package = forms.ModelChoiceField(
        queryset=Package.objects.filter(is_published=True, category="online"),
        required=False,
        empty_label="Not sure yet: help me choose",
        label="Package",
    )

    class Meta:
        model = Order
        fields = ["package", "services", "domain_name", "name", "email", "phone", "company", "notes"]
        labels = {
            "domain_name": "Domain name you want (or already own)",
            "phone": "Phone / M-Pesa number",
            "notes": "Anything else we should know?",
        }
        widgets = {
            "domain_name": forms.TextInput(attrs={"placeholder": "e.g. mybusiness.co.ke"}),
            "name": forms.TextInput(attrs={"placeholder": "Your name", "autocomplete": "name"}),
            "email": forms.EmailInput(attrs={"placeholder": "you@example.com", "autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"placeholder": "07XX XXX XXX", "autocomplete": "tel"}),
            "company": forms.TextInput(attrs={"placeholder": "Business / organisation (optional)"}),
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "e.g. the website is already built in Python and needs hosting"}),
        }

    def clean_website(self):
        if self.cleaned_data.get("website"):
            raise forms.ValidationError("Spam detected.")
        return ""

    def clean_services(self):
        return ",".join(self.cleaned_data["services"])

    def clean_domain_name(self):
        value = self.cleaned_data.get("domain_name", "").strip().lower()
        value = re.sub(r"^https?://", "", value).removeprefix("www.").rstrip("/")
        if value and not DOMAIN_RE.match(value):
            raise forms.ValidationError("Enter a domain like mybusiness.co.ke, without spaces.")
        return value

    def clean(self):
        data = super().clean()
        if "domain" in (data.get("services") or "").split(",") and not data.get("domain_name"):
            self.add_error("domain_name", "Tell us the domain name you'd like.")
        return data


class PaymentCodeForm(forms.Form):
    mpesa_code = forms.CharField(
        max_length=12,
        label="M-Pesa confirmation code",
        widget=forms.TextInput(attrs={"placeholder": "e.g. SJK4A2B9XY", "autocomplete": "off"}),
    )

    def clean_mpesa_code(self):
        code = self.cleaned_data["mpesa_code"].strip().upper()
        if not re.fullmatch(r"[A-Z0-9]{10}", code):
            raise forms.ValidationError("The code is the 10 letters and numbers at the start of the M-Pesa message.")
        return code
