from django.shortcuts import render, redirect, get_object_or_404
from .models import Elevage
from .forms import NouvelElevageForm

def index(request):
    return render(request, "app/index.html", {})

def nouvel_elevage(request):
    if request.method == "POST":
        form = NouvelElevageForm(request.POST)
        if form.is_valid():
            nombreLapins = form.cleaned_data['nombreLapins']
            elevage = form.save()
            for i in range(nombreLapins):
                pass
            return redirect("voir_elevage", elevage.id)
    else:
        form = NouvelElevageForm({
                          "nom": "Mon elevage",
                          "nouritureGrammes": "1000",
                          "cages": 1,
                          "argentCents": 10 ,
                          "nombreLapins": 2
                          })
        
    
    
    return render(request, "app/nouvel_elevage.html", { "form": form})

def voir_elevage(request, pk):
    elevage = get_object_or_404(Elevage, pk=pk)
    return render(request, "app/voir_elevage.html", { "elevage": elevage})