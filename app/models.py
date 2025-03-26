from django.db import models


class Elevage(models.Model):
    nom = models.CharField(max_length=200)
    nouritureGrammes = models.IntegerField()
    cages = models.IntegerField()
    argentCents = models.IntegerField()
    ageMois = models.IntegerField(default=0)

    def nombreLapins(self):
        return Individu.objects.filter(elevage=self).count()


class Individu(models.Model):
    elevage = models.ForeignKey(Elevage, on_delete=models.CASCADE)
    sexe = models.CharField(max_length=1)
    moisNaissance = models.IntegerField()
    moisGravide = models.IntegerField(null=True)
