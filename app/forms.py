from django import forms
from .models import Elevage

class NouvelElevageForm(forms.ModelForm):
    nombreLapins = forms.IntegerField(label="Nombre de lapins")
    class Meta:
        model = Elevage
        fields=["nom", "nouritureGrammes", "cages", "argentCents", 'nombreLapins']
        labels={
                "nom": "Nom de l'élevage",
                "nouritureGrammes": "Réserve de nouriture (grammes)",
                "cages": "Nombre de cages",
                "argentCents" : "Banque (cents)"
                }