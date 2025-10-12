from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Opcion

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("username", "role", "password1", "password2")

class PreguntaForm(forms.Form):
    def __init__(self, *args, **kwargs):
        pregunta = kwargs.pop('pregunta')
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        opciones = Opcion.objects.filter(pregunta=pregunta)
        self.fields['opcion'] = forms.ModelChoiceField(
            queryset=opciones,
            widget=forms.RadioSelect,
            empty_label=None,
            label=pregunta.texto
        )

        if usuario:
            from .models import RespuestaUsuario
            respuesta = RespuestaUsuario.objects.filter(usuario=usuario, pregunta=pregunta).first()
            if respuesta:
                self.fields['opcion'].initial = respuesta.opcion.id