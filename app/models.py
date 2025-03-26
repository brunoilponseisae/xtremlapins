from django.db import models


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


class Individu(models.Model):
    elevage = models.ForeignKey(Elevage, on_delete=models.CASCADE, related_name='lapins')
    nom = models.CharField(max_length=200)
    sexe = models.CharField(max_length=1)
    moisNaissance = models.IntegerField()
    moisGravide = models.IntegerField(null=True)

    @property
    def ageMois(self):
        return self.elevage.ageMois - self.moisNaissance

    @property
    def gravideDepuisMois(self):
        if self.moisGravide is not None:
            return self.elevage.ageMois - self.moisGravide
    