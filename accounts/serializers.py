from django.contrib.auth.models import User
from rest_framework import serializers
from elections.models import UserProfile

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    phone = serializers.CharField(write_only=True, required=False, allow_blank=True)
    date_of_birth = serializers.DateField(write_only=True, required=False, allow_null=True)
    role = serializers.ChoiceField(write_only=True, choices=[('voter', 'Voter'), ('admin', 'Admin')], required=False)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'phone', 'date_of_birth', 'role')

    def create(self, validated_data):
        phone = validated_data.pop('phone', '')
        date_of_birth = validated_data.pop('date_of_birth', None)
        role = validated_data.pop('role', 'voter')

        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )

        # Ensure profile exists and set additional fields
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role if role in dict(UserProfile.USER_ROLES) else 'voter'
        profile.phone = phone or ''
        profile.date_of_birth = date_of_birth
        profile.save()

        return user