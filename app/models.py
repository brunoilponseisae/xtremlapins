from django.db import models
from functools import cmp_to_key
from .config import Config
import random


class ElevageManager(models.Manager):
    def creer(self, elevage, nombreLapins):
        elevage.save()
        Individu.objects.creer(elevage, -3, "M")
        Individu.objects.creer(elevage, -3, "F")

        for i in range(nombreLapins-2):
            Individu.objects.creer(elevage, 0)

        return elevage

    def passerMois(self, pk, nouritureAcheteeGrammes, lapinsVendus, cagesAchetees):
        elevage = self.get(pk=pk)

        depenses = Config.PRIX_CAGE_CENTS * cagesAchetees + Config.PRIX_GRAMME_NOURITURE_CENTS * nouritureAcheteeGrammes
        recettes = lapinsVendus * Config.PRIX_VENTE_LAPIN_CENTS
        balanceArgent = elevage.argentCents + recettes - depenses

        error = None

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
                        lapin.creer_evenement(f"Décès de {lapin.nom} - Mort de faim")
                        continue

                    # Mort à cause de la surpopulation
                    if nbLapinsDansCages > maxLapins:
                        lapin.statut = "D"
                        lapin.save()
                        lapin.creer_evenement(f"Décès de {lapin.nom} - Surpopulation")
                        continue

                    # Reproduction
                    if lapin.sexe == "F":
                        # Deviennent gravide
                        if (lapin.moisGravide is None
                                and lapin.ageMois < Config.MAX_AGE_MOIS_GRAVIDE
                                and lapin.ageMois > Config.MIN_AGE_MOIS_GRAVIDE):
                            lapin.moisGravide = elevage.ageMois
                            lapin.creer_evenement(f"{lapin.nom} devient gravide.")
                            lapin.save()
                        # Mettent bas
                        elif lapin.gravideDepuisMois is not None and lapin.gravideDepuisMois >= Config.DUREE_GRAVIDITE_MOIS:
                            for i in range(random.randrange(Config.MAX_LAPEREAUX_PAR_PORTEE) + 1):
                                Individu.objects.creer(elevage)
                            lapin.moisGravide = None
                            lapin.save()
                            lapin.creer_evenement(f"{lapin.nom} met bas")

            if balanceNouriture < 0:
                balanceNouriture = 0

            elevage.nouritureGrammes = balanceNouriture
            elevage.cages = elevage.cages + cagesAchetees
            elevage.argentCents = balanceArgent
            elevage.ageMois = elevage.ageMois + 1
            elevage.save()

            if cagesAchetees > 0:
                elevage.creer_evenement(f"Achat de {cagesAchetees} cages")
            if nouritureAcheteeGrammes > 0:
                elevage.creer_evenement(f"Achat de {nouritureAcheteeGrammes}g de nourriture")
            if lapinsVendus > 0:
                elevage.creer_evenement(f"Vente de {lapinsVendus} lapins")

        return (elevage, error)


class Elevage(models.Model):
    nom = models.CharField(max_length=200)
    nouritureGrammes = models.IntegerField()
    cages = models.IntegerField()
    argentCents = models.IntegerField()
    ageMois = models.IntegerField(default=0)

    objects = ElevageManager()

    def creer_evenement(self, texte):
        return Evenement(elevage=self,
                         individu=None,
                         ageMois=self.ageMois,
                         texte=texte).save()

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
    def lapinsMorts(self):
        return Individu.objects.filter(elevage=self, statut="D")

    @property
    def lapinsVendus(self):
        return Individu.objects.filter(elevage=self, statut="V")

    @property
    def lapinsTries(self):
        res = sorted(self.lapins.all(), key=cmp_to_key(sort_lapins))
        return res

    @property
    def sortedEvenements(self):
        res = sorted(self.evenements.all(), key=lambda x: x.ageMois, reverse=True)
        return res


class IndividuManager(models.Manager):
    def creer(self, elevage: Elevage, moisNaissance: int = None, sexe=None):
        if sexe is None:
            sexe = "F"
            if bool(random.getrandbits(1)):
                sexe = "M"

        if moisNaissance is None:
            moisNaissance = elevage.ageMois

        indexNom = random.randrange(len(Config.NOM_LAPINS))

        individu = Individu(elevage=elevage,
                            nom=Config.NOM_LAPINS[indexNom],
                            sexe=sexe,
                            moisNaissance=moisNaissance,
                            moisGravide=None,
                            statut="N",
                            )
        individu.save()

        action = "Acquisition"
        if moisNaissance >= 0:
            action = "Naissance"
        individu.creer_evenement(f"{action} de {individu.nom}")

        return individu


class Individu(models.Model):
    elevage = models.ForeignKey(Elevage, on_delete=models.CASCADE, related_name='lapins')
    nom = models.CharField(max_length=200)
    sexe = models.CharField(max_length=1)
    moisNaissance = models.IntegerField()
    moisDécès = models.IntegerField(null=True)
    moisGravide = models.IntegerField(null=True)
    statut = models.CharField(max_length=1)

    objects = IndividuManager()

    def creer_evenement(self, texte):
        return Evenement(elevage=self.elevage,
                         individu=self,
                         ageMois=self.elevage.ageMois,
                         texte=texte).save()

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


class Evenement(models.Model):
    elevage = models.ForeignKey(Elevage, on_delete=models.CASCADE, related_name='evenements')
    individu = models.ForeignKey(Individu, on_delete=models.CASCADE, related_name='evenements', null=True)
    ageMois = models.IntegerField()
    texte = models.CharField(max_length=200)


def sort_lapins(l1: Individu, l2: Individu):
    if l1.ageMois > l2.ageMois:
        return 1
    if l1.ageMois < l2.ageMois:
        return -1
    return 0


def sort_lapins_vente(l1: Individu, l2: Individu):
    if l1.sexe == "M" and l2.sexe == "F":
        return -1
    if l1.sexe == "F" and l2.sexe == "M":
        return 1
    return sort_lapins(l1, l2)


def sort_lapins_nouriture(l1: Individu, l2: Individu):
    return sort_lapins_vente(l2, l1)
