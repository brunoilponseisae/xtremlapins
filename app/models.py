from django.db import models
from functools import cmp_to_key




class Elevage(models.Model):
    nom = models.CharField(max_length=200)
    nouritureGrammes = models.IntegerField()
    cages = models.IntegerField()
    argentCents = models.IntegerField()
    ageMois = models.IntegerField(default=0)

    @property
    def nombreLapinsMales(self):
        return Individu.objects.filter(elevage=self, sexe="M").count()

    @property
    def nombreLapinsFemelles(self):
        return Individu.objects.filter(elevage=self, sexe="F").count()
    
    @property
    def argentEuros(self):
        return f"{self.argentCents/100}€"

    @property
    def lapinsDisponibles(self):
        return Individu.objects.filter(elevage=self, statut="N")

    @property
    def lapinsTries(self):
        res = sorted(self.lapins.all(), key=cmp_to_key(sort_lapins))
        return res


class Individu(models.Model):
    elevage = models.ForeignKey(Elevage, on_delete=models.CASCADE, related_name='lapins')
    nom = models.CharField(max_length=200)
    sexe = models.CharField(max_length=1)
    moisNaissance = models.IntegerField()
    moisDécès = models.IntegerField(null=True)
    moisGravide = models.IntegerField(null=True)
    statut = models.CharField(max_length=1)

    @property
    def ageMois(self):
        return self.elevage.ageMois - self.moisNaissance

    @property
    def gravideDepuisMois(self):
        if self.moisGravide is not None:
            return self.elevage.ageMois - self.moisGravide
    
    @property
    def statutText(self):
        if self.statut == "N":
            if self.gravideDepuisMois:
                return f"Gravide depuis {self.gravideDepuisMois} mois"
            else:
                return "Dans l'élevage"
        if self.statut == "D":
            return "Décédé"
        if self.statut == "V":
            return "Vendu"
        

        

def sort_lapins(l1: Individu, l2: Individu):
    if l1.ageMois > l2.ageMois:
        return 1
    if l1.ageMois < l2.ageMois:
        return 1
    return 0
