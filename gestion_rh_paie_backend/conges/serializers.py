from rest_framework import serializers
from conges.models import Conge

class CongeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conge
        fields = ["id", "employe_id", "date_debut", "date_fin", "statut", "date_demande"]
        read_only_fields = ["id"]

    def get_extra_kwargs(self):
        extra = super().get_extra_kwargs()
        
        if self.instance is None:
            extra.update({"employe_id": {"read_only": True}, "date_debut": {"read_only": True},
                "date_fin": {"read_only": True}, "statut": {"read_only": True}, "date_demande": {"read_only": True}})
        return extra
    

class CongeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Conge
        fields = ["date_debut", "date_fin", "statut", "date_demande"]
        extra_kwargs = {"date_debut": {"required": False}, "date_fin": {"required": False},
                        "statut": {"required": False}, "date_demande": {"required": False}}