from django.shortcuts import render, redirect, get_object_or_404
from .models import Elevage
from .forms import NouvelElevageForm, ActionElevageForm
from .config import Config


def index(request):
    return render(request, "app/index.html", {})


def nouvel_elevage(request):
    if request.method == "POST":
        form = NouvelElevageForm(request.POST)
        if form.is_valid():
            nombreLapins = form.cleaned_data['nombreLapins']
            elevage = Elevage.objects.creer(form.instance, nombreLapins)
            return redirect("voir_elevage", elevage.id)
    else:
        form = NouvelElevageForm({
                          "nom": "Mon elevage",
                          "nouritureGrammes": 10000,
                          "cages": 1,
                          "argentCents": 1000,
                          "nombreLapins": 2
                          })
    return render(request, "app/nouvel_elevage.html", {"form": form})


def voir_elevage(request, pk):
    elevage = get_object_or_404(Elevage, pk=pk)
    error = None
    if request.method == "POST":
        form = ActionElevageForm(request.POST)
        if form.is_valid():
            nouritureAcheteeGrammes = form.cleaned_data['nouritureAcheteeGrammes']
            lapinsVendus = form.cleaned_data['lapinsVendus']
            cagesAchetees = form.cleaned_data['cagesAchetees']

            (elevage, error) = Elevage.objects.passerMois(elevage.id, nouritureAcheteeGrammes, lapinsVendus, cagesAchetees)

    form = ActionElevageForm()
    return render(request, "app/voir_elevage.html", {"elevage": elevage,
                                                     "form": form,
                                                     "error": error,
                                                     "Config": Config
                                                     })


def liste_elevages(request):
    elevages = Elevage.objects.all()
    return render(request, "app/liste_elevages.html", {"elevages": elevages})
