from django import forms
from .models import Elevage


class NouvelElevageForm(forms.ModelForm):
    nombreLapins = forms.IntegerField(label="Nombre de lapins")

    class Meta:
        model = Elevage
        fields = ["nom", "nouritureGrammes", "cages", "argentCents", 'nombreLapins']
        labels = {
                "nom": "Nom de l'élevage",
                "nouritureGrammes": "Réserve de nouriture (grammes)",
                "cages": "Nombre de cages",
                "argentCents": "Banque (cents)"
                }


class ActionElevageForm(forms.Form):
    nouritureAcheteeGrammes = forms.IntegerField(label="Achat de nouriture (grammes)", initial=0)
    lapinsVendus = forms.IntegerField(label="Vente de lapins", initial=0)
    cagesAchetees = forms.IntegerField(label="Achat de cages", initial=0)
