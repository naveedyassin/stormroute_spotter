from rest_framework import serializers


class TripSerializer(serializers.Serializer):
    origin = serializers.CharField(max_length=255)
    destination = serializers.CharField(max_length=255)

    departure_date = serializers.DateField()
    departure_time = serializers.TimeField()

    load_weight = serializers.IntegerField(min_value=1)

    checkpoint_interval = serializers.ChoiceField(
        choices=[10, 25, 50]
    )

    def validate(self, data):
        origin = data["origin"].strip()
        destination = data["destination"].strip()

        if not origin:
            raise serializers.ValidationError({
                "origin": "Origin cannot be empty."
            })

        if not destination:
            raise serializers.ValidationError({
                "destination": "Destination cannot be empty."
            })

        if origin.casefold() == destination.casefold():
            raise serializers.ValidationError(
                "Origin and destination must be different."
            )

        data["origin"] = origin
        data["destination"] = destination

        return data