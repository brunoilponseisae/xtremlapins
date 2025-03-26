from django.shortcuts import render, redirect, get_object_or_404
from .models import Elevage, Individu
from .forms import NouvelElevageForm, ActionElevageForm
from .utils import creer_individu

PRIX_GRAMME_NOURITURE_CENTS=0.1
PRIX_VENTE_LAPIN_CENTS=100
PRIX_CAGE_CENTS=100
CONSOMMATION_NOURITURE_GRAMMES_2_MOIS=100
CONSOMMATION_NOURITURE_GRAMMES_3_MOIS=250

def index(request):
    return render(request, "app/index.html", {})

def nouvel_elevage(request):
    if request.method == "POST":
        form = NouvelElevageForm(request.POST)
        if form.is_valid():
            nombreLapins = form.cleaned_data['nombreLapins']
            elevage = form.save()

            creer_individu(elevage, -3, "M")
            creer_individu(elevage, -3, "F")

            for i in range(nombreLapins-2):
                creer_individu(elevage, 0)
                
            return redirect("voir_elevage", elevage.id)
    else:
        form = NouvelElevageForm({
                          "nom": "Mon elevage",
                          "nouritureGrammes": 10000,
                          "cages": 1,
                          "argentCents": 1000 ,
                          "nombreLapins": 2
                          })
        
    
    
    return render(request, "app/nouvel_elevage.html", { "form": form})

def voir_elevage(request, pk):
    elevage = get_object_or_404(Elevage, pk=pk)
    error = None
    if request.method == "POST":
        form = ActionElevageForm(request.POST)
        if form.is_valid():
            nouritureAcheteeGrammes = form.cleaned_data['nouritureAcheteeGrammes']
            lapinsVendus = form.cleaned_data['lapinsVendus']
            cagesAchetees = form.cleaned_data['cagesAchetees']

            depenses = PRIX_CAGE_CENTS * cagesAchetees + PRIX_GRAMME_NOURITURE_CENTS * nouritureAcheteeGrammes
            recettes = lapinsVendus * PRIX_VENTE_LAPIN_CENTS
            balanceArgent = elevage.argentCents + recettes - depenses
            
            if len(elevage.lapins.all()) < lapinsVendus:
                error = "Vous essayez de vendre plus de lapin que vous n'en avez."
                
            if balanceArgent < 0:
                error = f"Vous n'avez pas assez d'argent pour ces achats (manque {-balanceArgent}€). Vendez plus de lapins!"

            if not error:
                nourritureConsommee = 0
                for lapin in elevage.lapins.all():
                    # Consommation de nouriture
                    if lapin.ageMois >= 3:
                        nourritureConsommee += CONSOMMATION_NOURITURE_GRAMMES_3_MOIS
                    elif lapin.ageMois >= 2:
                        nourritureConsommee += CONSOMMATION_NOURITURE_GRAMMES_2_MOIS

                    # Gravidité
                    print(lapin.sexe)
                    print(lapin.moisGravide)
                    if lapin.sexe == "F" and lapin.moisGravide is None:
                        print("qsdsqd")
                        lapin.moisGravide = elevage.ageMois
                        lapin.save()
                
                balanceNouriture = elevage.nouritureGrammes + nouritureAcheteeGrammes - nourritureConsommee
                if balanceNouriture < 0:
                    balanceNouriture = 0
                    # TODO: implementer décès

                elevage.nouritureGrammes = balanceNouriture
                elevage.cages = elevage.cages + cagesAchetees
                elevage.argentCents = balanceArgent
                elevage.ageMois = elevage.ageMois + 1
                elevage.save()

    form = ActionElevageForm()
    return render(request, "app/voir_elevage.html", { "elevage": elevage,
                                                    "form": form,
                                                    "error": error})