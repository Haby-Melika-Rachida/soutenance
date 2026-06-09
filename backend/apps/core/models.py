"""
Modèles Django — Module de Rapprochement MB/CBS/PI
14 classes persistantes issues du MLD validé.

CT-06 : AnnotationEcart et AuditLog sont immuables après création.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


# ═══════════════════════════════════════════════════════════════
# CLASSES DE CHOIX (Enums)
# ═══════════════════════════════════════════════════════════════

class ProfilChoices(models.TextChoices):
    RESPONSABLE_MB  = 'RESPONSABLE_MB',  'Responsable Mobile Banking'
    AGENT_BACKOFFICE = 'AGENT_BACKOFFICE', 'Agent Back-Office'
    ADMINISTRATEUR  = 'ADMINISTRATEUR',  'Administrateur'


class StatutSessionChoices(models.TextChoices):
    EN_COURS             = 'EN_COURS',             'En cours'
    TERMINEE             = 'TERMINEE',             'Terminée'
    TERMINEE_SANS_RAPPORT = 'TERMINEE_SANS_RAPPORT', 'Terminée sans rapport'
    ERREUR               = 'ERREUR',               'Erreur'


class TypeFluxChoices(models.TextChoices):
    CBS_SIMPLE   = 'CBS_SIMPLE',   'Transfert simple CBS'
    PI_EMISSION  = 'PI_EMISSION',  'Paiement Instantané Émission'
    PI_RECEPTION = 'PI_RECEPTION', 'Paiement Instantané Réception'


class TypeEcartChoices(models.TextChoices):
    EC_01 = 'EC-01', 'Transaction MB lettrée absente du CBS'
    EC_02 = 'EC-02', 'Transaction CBS sans correspondance MB'
    EC_03 = 'EC-03', 'Doublon côté CBS'
    EC_04 = 'EC-04', 'Doublon côté MB'
    EC_05 = 'EC-05', 'Irrévocable non débité'
    EC_06 = 'EC-06', 'Irrévocable non crédité'


class CriticiteChoices(models.TextChoices):
    CRITIQUE = 'CRITIQUE', 'Critique'
    IMPORTANT = 'IMPORTANT', 'Important'


class StatutEcartChoices(models.TextChoices):
    NOUVEAU      = 'NOUVEAU',      'Nouveau'
    EN_COURS     = 'EN_COURS',     'En cours de traitement'
    RESOLU       = 'RESOLU',       'Résolu'
    IGNORE = 'IGNORE', 'Ignoré'


class DeclenchementChoices(models.TextChoices):
    AUTOMATIQUE = 'AUTOMATIQUE', 'Automatique (planifié)'
    MANUEL      = 'MANUEL',      'Manuel'


class PrioriteNotifChoices(models.TextChoices):
    HAUTE    = 'HAUTE',    'Haute (écart critique)'
    IMPORTANT = 'IMPORTANT', 'Important'


class DirectionPIChoices(models.TextChoices):
    EMISSION  = 'EMISSION',  'Émission'
    RECEPTION = 'RECEPTION', 'Réception'


# ═══════════════════════════════════════════════════════════════
# 1. PROFIL
# ═══════════════════════════════════════════════════════════════

class Profil(models.Model):
    """Rôle et permissions d'un utilisateur dans le système."""

    nom = models.CharField(
        max_length=30,
        choices=ProfilChoices.choices,
        unique=True,
        verbose_name='Nom du profil'
    )
    description = models.TextField(blank=True, verbose_name='Description')

    class Meta:
        db_table = 'profil'
        verbose_name = 'Profil'
        verbose_name_plural = 'Profils'

    def __str__(self):
        return self.get_nom_display()


# ═══════════════════════════════════════════════════════════════
# 2. UTILISATEUR (modèle custom — remplace auth.User)
# ═══════════════════════════════════════════════════════════════

class Utilisateur(AbstractUser):
    """
    Utilisateur du module. Étend AbstractUser Django.
    AUTH_USER_MODEL doit pointer vers ce modèle dans settings.
    """

    profil = models.ForeignKey(
        Profil,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='utilisateurs',
        verbose_name='Profil'
    )

    class Meta:
        db_table = 'utilisateur'
        verbose_name = 'Utilisateur'
        verbose_name_plural = 'Utilisateurs'

    def __str__(self):
        return f'{self.username} ({self.profil})'


# ═══════════════════════════════════════════════════════════════
# 3. CONFIGURATION BATCH
# ═══════════════════════════════════════════════════════════════

class ConfigurationBatch(models.Model):
    """
    Paramètres d'exécution du batch : retries, timeouts, tolérance de date.
    Modifiable depuis l'interface admin sans redéploiement (CT-07).
    """

    nom = models.CharField(
        max_length=100,
        default='Configuration par défaut',
        verbose_name='Nom'
    )
    max_retries = models.PositiveIntegerField(
        default=3,
        verbose_name='Nombre max de tentatives'
    )
    retry_wait_seconds = models.PositiveIntegerField(
        default=2,
        verbose_name='Délai entre tentatives (s)'
    )
    timeout_seconds = models.PositiveIntegerField(
        default=30,
        verbose_name='Timeout API (s)'
    )
    date_tolerance_days = models.PositiveIntegerField(
        default=0,
        verbose_name='Tolérance date matching (jours)'
    )
    active = models.BooleanField(
        default=True,
        verbose_name='Configuration active'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'configuration_batch'
        verbose_name = 'Configuration Batch'

    def __str__(self):
        return self.nom


# ═══════════════════════════════════════════════════════════════
# 4. CONFIGURATION PLANIFICATION
# ═══════════════════════════════════════════════════════════════

class ConfigurationPlanification(models.Model):
    """
    Paramètres de planification du batch nocturne (heure de déclenchement).
    Modifiable depuis l'interface admin (CT-07).
    L'Utilisateur qui modifie est tracé (date_modif).
    """

    heure = models.PositiveSmallIntegerField(
        default=2,
        verbose_name='Heure de déclenchement (0-23)'
    )
    minute = models.PositiveSmallIntegerField(
        default=0,
        verbose_name='Minute de déclenchement (0-59)'
    )
    active = models.BooleanField(
        default=True,
        verbose_name='Planification active'
    )
    modifie_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='configurations_planification',
        verbose_name='Modifié par'
    )
    date_modification = models.DateTimeField(
        auto_now=True,
        verbose_name='Date de dernière modification'
    )

    class Meta:
        db_table = 'configuration_planification'
        verbose_name = 'Configuration Planification'

    def __str__(self):
        return f'Batch planifié à {self.heure:02d}:{self.minute:02d}'


# ═══════════════════════════════════════════════════════════════
# 5. RECONCILIATION SESSION (pivot central du MLD)
# ═══════════════════════════════════════════════════════════════

class ReconciliationSession(models.Model):
    """
    Représente une exécution du batch de rapprochement.
    Pivot central : toutes les données collectées et les écarts
    lui sont rattachés.
    """

    date_traitement = models.DateField(
        verbose_name='Date des transactions traitées'
    )
    statut = models.CharField(
        max_length=30,
        choices=StatutSessionChoices.choices,
        default=StatutSessionChoices.EN_COURS,
        verbose_name='Statut'
    )
    declenchement = models.CharField(
        max_length=15,
        choices=DeclenchementChoices.choices,
        default=DeclenchementChoices.AUTOMATIQUE,
        verbose_name='Mode de déclenchement'
    )
    declenchee_par = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='sessions_declenchees',
        verbose_name='Déclenchée par (si manuel)'
    )
    configuration = models.ForeignKey(
        ConfigurationBatch,
        on_delete=models.PROTECT,
        related_name='sessions',
        verbose_name='Configuration utilisée'
    )
    heure_debut = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Heure de début'
    )
    heure_fin = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Heure de fin'
    )
    message_erreur = models.TextField(
        blank=True,
        verbose_name='Message d\'erreur (si statut ERREUR)'
    )

    class Meta:
        db_table = 'reconciliation_session'
        verbose_name = 'Session de Rapprochement'
        verbose_name_plural = 'Sessions de Rapprochement'
        ordering = ['-heure_debut']

    def __str__(self):
        return f'Session {self.date_traitement} — {self.statut}'


# ═══════════════════════════════════════════════════════════════
# 6. TRANSACTION MB
# ═══════════════════════════════════════════════════════════════

class TransactionMB(models.Model):
    """
    Transaction collectée depuis l'API-MOBILE.
    Collectée en lecture seule (CT-04).
    """

    session = models.ForeignKey(
        ReconciliationSession,
        on_delete=models.CASCADE,
        related_name='transactions_mb',
        verbose_name='Session'
    )
    message_id = models.CharField(
        max_length=255,
        verbose_name='Identifiant message (message_id)'
    )
    end_to_end_id = models.CharField(
        max_length=255,
        verbose_name='Référence end-to-end'
    )
    montant = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='Montant'
    )
    compte_debiteur = models.CharField(
        max_length=100,
        verbose_name='Compte débiteur'
    )
    compte_crediteur = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Compte créditeur'
    )
    statut = models.CharField(
        max_length=50,
        verbose_name='Statut dans le MB'
    )
    type_flux = models.CharField(
        max_length=15,
        choices=TypeFluxChoices.choices,
        verbose_name='Type de flux'
    )
    date_operation = models.DateField(verbose_name='Date d\'opération')
    collected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de collecte'
    )

    class Meta:
        db_table = 'transaction_mb'
        verbose_name = 'Transaction MB'
        verbose_name_plural = 'Transactions MB'
        indexes = [
            models.Index(fields=['end_to_end_id']),
            models.Index(fields=['session', 'type_flux']),
        ]

    def __str__(self):
        return f'MB {self.end_to_end_id} — {self.montant}'


# ═══════════════════════════════════════════════════════════════
# 7. TRANSACTION CBS
# ═══════════════════════════════════════════════════════════════

class TransactionCBS(models.Model):
    """
    Transaction collectée depuis l'API-CORE (logs d'audit CBS).
    Collectée en lecture seule (CT-04).
    """

    session = models.ForeignKey(
        ReconciliationSession,
        on_delete=models.CASCADE,
        related_name='transactions_cbs',
        verbose_name='Session'
    )
    msg_id = models.CharField(
        max_length=255,
        verbose_name='Identifiant message CBS'
    )
    end_to_end_id = models.CharField(
        max_length=255,
        verbose_name='Référence end-to-end'
    )
    montant = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='Montant'
    )
    debtor_account = models.CharField(
        max_length=100,
        verbose_name='Compte débiteur'
    )
    creditor_account = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Compte créditeur'
    )
    transaction_status = models.CharField(
        max_length=50,
        verbose_name='Statut dans le CBS'
    )
    is_pi_transfer = models.BooleanField(
        default=False,
        verbose_name='Est un transfert PI'
    )
    timestamp = models.DateTimeField(verbose_name='Horodatage CBS')
    collected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de collecte'
    )

    class Meta:
        db_table = 'transaction_cbs'
        verbose_name = 'Transaction CBS'
        verbose_name_plural = 'Transactions CBS'
        indexes = [
            models.Index(fields=['end_to_end_id']),
            models.Index(fields=['session', 'is_pi_transfer']),
        ]

    def __str__(self):
        return f'CBS {self.end_to_end_id} — {self.montant}'


# ═══════════════════════════════════════════════════════════════
# 8. CYCLE PI
# ═══════════════════════════════════════════════════════════════

class CyclePI(models.Model):
    """
    Cycle de Paiement Instantané collecté depuis l'API-PI.
    Contient les booléens de validation du cycle (funds_reserved, etc.).
    Collecté en lecture seule (CT-04).
    """

    session = models.ForeignKey(
        ReconciliationSession,
        on_delete=models.CASCADE,
        related_name='cycles_pi',
        verbose_name='Session'
    )
    message_id = models.CharField(
        max_length=255,
        verbose_name='Identifiant message PI'
    )
    end_to_end_id = models.CharField(
        max_length=255,
        verbose_name='Référence end-to-end'
    )
    direction = models.CharField(
        max_length=10,
        choices=DirectionPIChoices.choices,
        verbose_name='Direction'
    )
    montant = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        verbose_name='Montant'
    )
    # Booléens du cycle PI (champ specific_data de l'API-PI)
    funds_reserved = models.BooleanField(
        default=False,
        verbose_name='Fonds réservés'
    )
    funds_debited = models.BooleanField(
        default=False,
        verbose_name='Fonds débités'
    )
    funds_credited = models.BooleanField(
        default=False,
        verbose_name='Fonds crédités'
    )
    statut = models.CharField(
        max_length=50,
        verbose_name='Statut PI'
    )
    date_operation = models.DateField(verbose_name='Date d\'opération')
    collected_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de collecte'
    )

    class Meta:
        db_table = 'cycle_pi'
        verbose_name = 'Cycle PI'
        verbose_name_plural = 'Cycles PI'
        indexes = [
            models.Index(fields=['end_to_end_id']),
            models.Index(fields=['session', 'direction']),
        ]

    def __str__(self):
        return f'PI {self.direction} {self.end_to_end_id}'


# ═══════════════════════════════════════════════════════════════
# 9. ECART DETECTE
# ═══════════════════════════════════════════════════════════════

class EcartDetecte(models.Model):
    """
    Anomalie détectée lors du rapprochement.
    La référence vers la transaction source est stockée via
    end_to_end_id + type_flux (pas de FK nullable — choix MLD).
    """

    session = models.ForeignKey(
        ReconciliationSession,
        on_delete=models.CASCADE,
        related_name='ecarts',
        verbose_name='Session'
    )
    type_ecart = models.CharField(
        max_length=10,
        choices=TypeEcartChoices.choices,
        verbose_name='Type d\'écart'
    )
    criticite = models.CharField(
        max_length=10,
        choices=CriticiteChoices.choices,
        verbose_name='Criticité'
    )
    type_flux = models.CharField(
        max_length=15,
        choices=TypeFluxChoices.choices,
        verbose_name='Type de flux concerné'
    )
    # Référence vers la transaction source (pas de FK — CT-04 + MLD)
    reference = models.CharField(
        max_length=255,
        verbose_name='Référence transaction (end_to_end_id ou message_id)'
    )
    montant = models.DecimalField(
        max_digits=18,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Montant concerné'
    )
    compte = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Compte concerné'
    )
    description = models.TextField(verbose_name='Description de l\'écart')
    statut = models.CharField(
        max_length=15,
        choices=StatutEcartChoices.choices,
        default=StatutEcartChoices.NOUVEAU,
        verbose_name='Statut de traitement'
    )
    date_detection = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de détection'
    )

    class Meta:
        db_table = 'ecart_detecte'
        verbose_name = 'Écart Détecté'
        verbose_name_plural = 'Écarts Détectés'
        ordering = ['-date_detection']
        indexes = [
            models.Index(fields=['session', 'type_ecart']),
            models.Index(fields=['session', 'criticite']),
            models.Index(fields=['statut']),
            models.Index(fields=['reference']),
        ]

    def mark_in_progress(self):
        self.statut = StatutEcartChoices.EN_COURS
        self.save(update_fields=['statut'])

    def mark_resolved(self):
        self.statut = StatutEcartChoices.RESOLU
        self.save(update_fields=['statut'])

    def __str__(self):
        return f'{self.type_ecart} — {self.reference} ({self.criticite})'


# ═══════════════════════════════════════════════════════════════
# 10. ANNOTATION ECART (immuable — CT-06, 0..1 par écart)
# ═══════════════════════════════════════════════════════════════

class AnnotationEcart(models.Model):
    """
    Annotation d'un écart par un agent back-office.
    IMMUABLE après création (CT-06).
    Relation OneToOne : 0..1 annotation par écart (choix MLD).
    """

    ecart = models.OneToOneField(
        EcartDetecte,
        on_delete=models.CASCADE,
        related_name='annotation',
        verbose_name='Écart annoté'
    )
    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.PROTECT,
        related_name='annotations',
        verbose_name='Annotée par'
    )
    commentaire = models.TextField(verbose_name='Commentaire')
    nouveau_statut = models.CharField(
        max_length=15,
        choices=StatutEcartChoices.choices,
        verbose_name='Nouveau statut appliqué'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date d\'annotation'
    )

    class Meta:
        db_table = 'annotation_ecart'
        verbose_name = 'Annotation d\'Écart'

    def save(self, *args, **kwargs):
        """Immuabilité CT-06 : interdit toute mise à jour."""
        if self.pk:
            raise ValueError(
                'AnnotationEcart est immuable. '
                'Créez une nouvelle annotation plutôt que de modifier celle-ci.'
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError('AnnotationEcart est immuable et ne peut pas être supprimée.')

    def __str__(self):
        return f'Annotation #{self.ecart_id} par {self.utilisateur}'


# ═══════════════════════════════════════════════════════════════
# 11. RAPPORT RECONCILIATION (0..1 par session)
# ═══════════════════════════════════════════════════════════════

class RapportReconciliation(models.Model):
    """
    Rapport journalier généré après chaque session.
    Un seul rapport par session (RM-05).
    """

    session = models.OneToOneField(
        ReconciliationSession,
        on_delete=models.CASCADE,
        related_name='rapport',
        verbose_name='Session'
    )
    fichier_pdf = models.FileField(
        upload_to='rapports/pdf/',
        null=True,
        blank=True,
        verbose_name='Fichier PDF'
    )
    fichier_excel = models.FileField(
        upload_to='rapports/excel/',
        null=True,
        blank=True,
        verbose_name='Fichier Excel'
    )
    nb_transactions_mb = models.PositiveIntegerField(
        default=0,
        verbose_name='Nb transactions MB'
    )
    nb_transactions_cbs = models.PositiveIntegerField(
        default=0,
        verbose_name='Nb transactions CBS'
    )
    nb_ecarts_total = models.PositiveIntegerField(
        default=0,
        verbose_name='Nb écarts total'
    )
    nb_ecarts_critiques = models.PositiveIntegerField(
        default=0,
        verbose_name='Nb écarts critiques'
    )
    taux_rapprochement = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Taux de rapprochement (%)'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date de génération'
    )

    class Meta:
        db_table = 'rapport_reconciliation'
        verbose_name = 'Rapport de Rapprochement'

    def __str__(self):
        return f'Rapport session {self.session.date_traitement}'


# ═══════════════════════════════════════════════════════════════
# 12. METRIQUE BATCH (0..1 par session)
# ═══════════════════════════════════════════════════════════════

class MetriqueBatch(models.Model):
    """
    Métriques de performance d'une session de rapprochement.
    Accessibles depuis l'interface d'administration.
    """

    session = models.OneToOneField(
        ReconciliationSession,
        on_delete=models.CASCADE,
        related_name='metrique',
        verbose_name='Session'
    )
    duree_secondes = models.PositiveIntegerField(
        default=0,
        verbose_name='Durée totale (s)'
    )
    nb_transactions_mb_collectees = models.PositiveIntegerField(
        default=0,
        verbose_name='Transactions MB collectées'
    )
    nb_transactions_cbs_collectees = models.PositiveIntegerField(
        default=0,
        verbose_name='Transactions CBS collectées'
    )
    nb_cycles_pi_collectes = models.PositiveIntegerField(
        default=0,
        verbose_name='Cycles PI collectés'
    )
    nb_ecarts_detectes = models.PositiveIntegerField(
        default=0,
        verbose_name='Écarts détectés'
    )
    nb_erreurs_api = models.PositiveIntegerField(
        default=0,
        verbose_name='Erreurs API rencontrées'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'metrique_batch'
        verbose_name = 'Métrique Batch'

    def __str__(self):
        return f'Métriques session {self.session.date_traitement}'


# ═══════════════════════════════════════════════════════════════
# 13. NOTIFICATION
# ═══════════════════════════════════════════════════════════════

class Notification(models.Model):
    """
    Notification email envoyée suite à la détection d'un écart.
    Priorisée selon la criticité de l'écart (EF-16).
    """

    ecart = models.ForeignKey(
        EcartDetecte,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Écart concerné'
    )
    destinataires = models.JSONField(
        default=list,
        verbose_name='Liste des destinataires'
    )
    sujet = models.CharField(max_length=255, verbose_name='Sujet')
    corps = models.TextField(verbose_name='Corps du message')
    priorite = models.CharField(
        max_length=10,
        choices=PrioriteNotifChoices.choices,
        verbose_name='Priorité'
    )
    envoyee = models.BooleanField(
        default=False,
        verbose_name='Envoyée'
    )
    date_envoi = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Date d\'envoi'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        ordering = ['-created_at']

    def __str__(self):
        return f'Notif {self.priorite} — {self.sujet[:50]}'


# ═══════════════════════════════════════════════════════════════
# 14. AUDIT LOG (immuable — CT-06)
# ═══════════════════════════════════════════════════════════════

class AuditLog(models.Model):
    """
    Journal d'audit de toutes les actions utilisateurs.
    IMMUABLE après création (CT-06).
    Inclut les connexions, annotations, changements de statut.
    """

    utilisateur = models.ForeignKey(
        Utilisateur,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Utilisateur'
    )
    action = models.CharField(
        max_length=100,
        verbose_name='Action effectuée'
    )
    entite = models.CharField(
        max_length=100,
        verbose_name='Entité concernée (nom de table)'
    )
    entite_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='ID de l\'entité concernée'
    )
    details = models.JSONField(
        default=dict,
        verbose_name='Détails de l\'action'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Adresse IP'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Date et heure'
    )

    class Meta:
        db_table = 'audit_log'
        verbose_name = 'Log d\'Audit'
        verbose_name_plural = 'Logs d\'Audit'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        """Immuabilité CT-06 : interdit toute mise à jour."""
        if self.pk:
            raise ValueError(
                'AuditLog est immuable. '
                'Impossible de modifier un log d\'audit existant.'
            )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError('AuditLog est immuable et ne peut pas être supprimé.')

    def __str__(self):
        return f'[{self.created_at}] {self.utilisateur} — {self.action}'