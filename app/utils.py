from .models import Elevage, Individu, sort_lapins
from .names import NOM_LAPINS
import random


def creer_individu(elevage: Elevage, moisNaissance: int = None, sexe=None):
    if sexe is None:
        sexe = "F"
        if bool(random.getrandbits(1)):
            sexe = "M"

    if moisNaissance is None:
        moisNaissance = elevage.ageMois

    indexNom = random.randrange(len(NOM_LAPINS))

    Individu(elevage=elevage,
             nom=NOM_LAPINS[indexNom],
             sexe=sexe,
             moisNaissance=moisNaissance,
             moisGravide=None,
             statut="N",
             ).save()


# Tri des lapins
# Dabord les males
# Dabord les plus vieux
def sort_lapins_vente(l1: Individu, l2: Individu):
    if l1.sexe == "M" and l2.sexe == "F":
        return -1
    if l1.sexe == "F" and l2.sexe == "M":
        return 1
    return sort_lapins(l1, l2)


def sort_lapins_nouriture(l1: Individu, l2: Individu):
    return sort_lapins_vente(l2, l1)
