import pytz
from django import forms

class TimeZoneForm(forms.Form):
    timezone = forms.ChoiceField(
        choices=[(tz, tz) for tz in pytz.all_timezones],
        label='Выберите ваш часовой пояс'
    )