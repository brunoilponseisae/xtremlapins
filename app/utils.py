from .models import Elevage, Individu
from .names import NOM_LAPINS
import random

def creer_individu(elevage: Elevage, moisNaissance:int=None, sexe=None):
    if sexe is None:
        sexe = "F"
        if bool(random.getrandbits(1)):
            sexe = "M"
    
    if moisNaissance == None:
        moisNaissance=elevage.ageMois
    
    indexNom = random.randrange(len(NOM_LAPINS))

    Individu(elevage=elevage, 
                    nom=NOM_LAPINS[indexNom],
                    sexe=sexe,
                    moisNaissance=moisNaissance,
                    moisGravide=None
                    ).save()
