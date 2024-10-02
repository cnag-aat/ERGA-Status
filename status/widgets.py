from datetime import date
from django import forms

class CustomDatePickerWidget(forms.DateInput):
    DATE_INPUT_WIDGET_REQUIRED_FORMAT = '%Y-%m'

    def __init__(self, attrs={}, format=None):
        attrs.update(
            {
                'class': 'form-control',
                'type': 'date',
            }
        )
        self.format = format or self.DATE_INPUT_WIDGET_REQUIRED_FORMAT
        super().__init__(attrs, format=self.format)
        