from django.shortcuts import render, redirect, get_object_or_404
from .models import Elevage
from .forms import NouvelElevageForm, ActionElevageForm
from .utils import creer_individu, sort_lapins_nouriture, sort_lapins_vente
import random
from functools import cmp_to_key
from .config import Config

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
                          "argentCents": 1000,
                          "nombreLapins": 2
                          })
    return render(request, "app/nouvel_elevage.html", {"form": form })


def voir_elevage(request, pk):
    elevage = get_object_or_404(Elevage, pk=pk)
    error = None
    if request.method == "POST":
        form = ActionElevageForm(request.POST)
        if form.is_valid():
            nouritureAcheteeGrammes = form.cleaned_data['nouritureAcheteeGrammes']
            lapinsVendus = form.cleaned_data['lapinsVendus']
            cagesAchetees = form.cleaned_data['cagesAchetees']

            depenses = Config.PRIX_CAGE_CENTS * cagesAchetees + Config.PRIX_GRAMME_NOURITURE_CENTS * nouritureAcheteeGrammes
            recettes = lapinsVendus * Config.PRIX_VENTE_LAPIN_CENTS
            balanceArgent = elevage.argentCents + recettes - depenses

            if elevage.lapinsDisponibles.count() < lapinsVendus:
                error = "Vous essayez de vendre plus de lapin que vous n'en avez."

            if lapinsVendus < 0:
                error = "Vous essayez de vendre un nomre négatif de lapins."

            if balanceArgent < 0:
                error = f"Vous n'avez pas assez d'argent pour ces achats (manque {-balanceArgent}€). Vendez plus de lapins!"

            balanceNouriture = elevage.nouritureGrammes + nouritureAcheteeGrammes
            if not error:
                # Vente de lapins
                lapinVendusDb = 0

                for lapin in sorted(elevage.lapinsDisponibles, key=cmp_to_key(sort_lapins_vente)):
                    if lapinVendusDb >= lapinsVendus:
                        break
                    lapin.statut = "V"
                    lapin.save()
                    lapinVendusDb = lapinVendusDb + 1

                maxLapins = Config.MAX_LAPINS_PAR_CAGES * elevage.cages
                nbLapinsDansCages = 0

                # Gestion des lapins restants
                for lapin in sorted(elevage.lapinsDisponibles, key=cmp_to_key(sort_lapins_nouriture)):
                    if lapin.statut == "N":
                        if lapin.ageMois >= 1:
                            nbLapinsDansCages = nbLapinsDansCages + 1
                        # Consommation de nouriture
                        if lapin.ageMois >= 3:
                            balanceNouriture -= Config.CONSOMMATION_NOURITURE_GRAMMES_3_MOIS
                        elif lapin.ageMois >= 2:
                            balanceNouriture -= Config.CONSOMMATION_NOURITURE_GRAMMES_2_MOIS

                        # Mort de faim
                        if balanceNouriture < 0:
                            lapin.statut = "D"
                            lapin.save()
                            continue
                        
                        # Mort à cause de la surpopulation
                        if nbLapinsDansCages > maxLapins:
                            lapin.statut = "D"
                            lapin.save()
                            continue


                        # Reproduction
                        if lapin.sexe == "F":
                            # Deviennent gravide
                            if lapin.moisGravide is None and lapin.ageMois < Config.MAX_AGE_MOIS_GRAVIDE and lapin.ageMois > Config.MIN_AGE_MOIS_GRAVIDE:
                                lapin.moisGravide = elevage.ageMois
                                lapin.save()
                            # Mettent bas
                            elif lapin.gravideDepuisMois is not None and lapin.gravideDepuisMois >= Config.DUREE_GRAVIDITE_MOIS:
                                for i in range(random.randrange(Config.MAX_LAPEREAUX_PAR_PORTEE) + 1):
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
    return render(request, "app/voir_elevage.html", {"elevage": elevage,
                                                     "form": form,
                                                     "error": error,
                                                     "Config": Config
                                                     })


def liste_elevages(request):
    elevages = Elevage.objects.all()
    return render(request, "app/liste_elevages.html", {"elevages": elevages})
