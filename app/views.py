from django.shortcuts import render, redirect, get_object_or_404
from .models import Elevage, Individu
from .forms import NouvelElevageForm, ActionElevageForm
from .utils import creer_individu, sort_lapins_nouriture, sort_lapins_vente
import random
from functools import cmp_to_key

PRIX_GRAMME_NOURITURE_CENTS=0.1
PRIX_VENTE_LAPIN_CENTS=100
PRIX_CAGE_CENTS=100
CONSOMMATION_NOURITURE_GRAMMES_2_MOIS=100
CONSOMMATION_NOURITURE_GRAMMES_3_MOIS=250
MAX_LAPEREAUX_PAR_PORTEE=3

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
            
            if elevage.lapinsDisponibles.count() < lapinsVendus:
                error = "Vous essayez de vendre plus de lapin que vous n'en avez."
                
            if balanceArgent < 0:
                error = f"Vous n'avez pas assez d'argent pour ces achats (manque {-balanceArgent}€). Vendez plus de lapins!"

            balanceNouriture = elevage.nouritureGrammes
            if not error:
                # Vente de lapins
                lapinVendusDb = 0
                
                for lapin in sorted(elevage.lapinsDisponibles, key=cmp_to_key(sort_lapins_vente)):
                    if lapinVendusDb >= lapinsVendus:
                        break
                    lapin.statut = "V"
                    lapin.save()
                    lapinVendusDb = lapinVendusDb + 1

                # Gestion des lapins restants
                for lapin in sorted(elevage.lapinsDisponibles, key=cmp_to_key(sort_lapins_nouriture)):
                    if lapin.statut == "N":
                        # Consommation de nouriture
                        if lapin.ageMois >= 3:
                            balanceNouriture -= CONSOMMATION_NOURITURE_GRAMMES_3_MOIS
                        elif lapin.ageMois >= 2:
                            balanceNouriture -= CONSOMMATION_NOURITURE_GRAMMES_2_MOIS
                        
                        # Mort de faim
                        if balanceNouriture < 0:
                            lapin.statut = "D"
                            lapin.save()
                            continue


                        # Reproduction
                        if lapin.sexe == "F":
                            # Deviennent gravide
                            if lapin.moisGravide is None and lapin.ageMois < 4 * 12:
                                lapin.moisGravide = elevage.ageMois
                                lapin.save()
                            # Mettent bas
                            elif lapin.gravideDepuisMois >= 2:
                                for i in range(random.randrange(MAX_LAPEREAUX_PAR_PORTEE) + 1):
                                    creer_individu(elevage)
                                lapin.moisGravide = None
                                lapin.save()
                
                        
                    
                    

                if balanceNouriture < 0:
                    balanceNouriture = 0

                elevage.nouritureGrammes = balanceNouriture
                elevage.cages = elevage.cages + cagesAchetees
                elevage.argentCents = balanceArgent
                elevage.ageMois = elevage.ageMois + 1
                elevage.save()

    form = ActionElevageForm()
    return render(request, "app/voir_elevage.html", { "elevage": elevage,
                                                    "form": form,
                                                    "error": error})