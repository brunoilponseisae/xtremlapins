from django import forms
from .models import Elevage
from .config import Config


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
    nouritureAcheteeGrammes = forms.IntegerField(label=f"Achat de nouriture ({Config.PRIX_GRAMME_NOURITURE_CENTS} cents par gramme)", initial=0)
    lapinsVendus = forms.IntegerField(label=f"Vente de lapins ({Config.PRIX_VENTE_LAPIN_CENTS} cents par lapin)", initial=0)
    cagesAchetees = forms.IntegerField(label=f"Achat de cages ({Config.PRIX_CAGE_CENTS} cents par cage)", initial=0)
