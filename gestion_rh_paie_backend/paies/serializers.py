from rest_framework import serializers
from paies.models import Paie

class PaieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paie
        fields = ["id", "employe_id", "salaire_base", "salaire_net", "date_paiement", "its", "cnps"]
        read_only_fields = ["id"]

    def get_extra_kwargs(self):
        extra = super().get_extra_kwargs()
        
        if self.instance is None:
            extra.update({"employe_id": {"read_only": True}, "salaire_base": {"read_only": True},
                "salaire_net": {"read_only": True}, "date_paiement": {"read_only": True}, "its": {"read_only": True}, "cnps": {"read_only": True}})
        return extra


class PaieUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paie
        fields = ["salaire_base", "salaire_net", "date_paiement", "its", "cnps"]
        extra_kwargs = {"salaire_base": {"required": False}, "salaire_net": {"required": False}, "date_paiement": {"required": False},
                        "its": {"required": False}, "cnps": {"required": False}}