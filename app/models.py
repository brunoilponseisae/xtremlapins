from django.db import models


class Elevage(models.Model):
    nom = models.CharField(max_length=200)
    nouritureGrammes = models.IntegerField()
    cages = models.IntegerField()
    argentCents = models.IntegerField()


class Individu(models.Model):
	sexe = models.CharField(max_length=1)
	moisNaissance = models.IntegerField()
	moisGravide = models.IntegerField(null=True)
