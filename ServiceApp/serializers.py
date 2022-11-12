from rest_framework import serializers

from ServiceApp.models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id', 'createdAt', 'updatedAt', 'destroyTime', 'url', 'isDestroyed',
            'hasPassword', 'askForConfirmation', 'message', 'frontendSecretKey', 'backendSecretKey', 'password',
            'confirmPassword', 'name', 'email'
        ]
