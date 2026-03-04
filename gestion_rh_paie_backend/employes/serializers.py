from rest_framework import serializers
from employes.models import Employe

class EmployeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ["id", "nom", "prenom", "email", "poste", "departement", "salaire",
                "solde_conge", "mot_de_passe", "administrateur", "disponibilite", "statut"]
        read_only_fields = ["id"]  

    def get_extra_kwargs(self):
        extra = super().get_extra_kwargs()
        
        if self.instance is None:  # serializer is creating a new object
            extra.update({"solde_conge": {"read_only": True}, "mot_de_passe": {"read_only": True},
                "disponibilite": {"read_only": True}, "statut": {"read_only": True}, "administrateur": {"read_only": True}})
        return extra
    

class EmployeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employe
        fields = ["poste", "departement", "salaire", "disponibilite", "email", "statut"]
        extra_kwargs = {
            "poste": {"required": False},
            "departement": {"required": False},
            "salaire": {"required": False},
            "disponibilite": {"required": False},
            "email": {"required": False},
            "statut": {"required": False},
        }