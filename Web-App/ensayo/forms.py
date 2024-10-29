from django import forms
from .models import Ensayo
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
import re
class EnsayoForm(forms.ModelForm):
    class Meta:
        model=Ensayo
        fields=['codigo_ensayo', 'nombre_ensayo', 'fecha_ensayo'
                ,'estado_ensayo']

