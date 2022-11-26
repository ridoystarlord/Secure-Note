from rest_framework import serializers

from ServiceApp.models import Note


class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'id', 'createdAt', 'updatedAt', 'destroyTime', 'url', 'isDestroyed',
            'askForConfirmation', 'message', 'frontendSecretKey', 'backendSecretKey', 'password',
            'name', 'email'
        ]


class ResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'createdAt', 'destroyTime', 'isDestroyed', 'url', 'askForConfirmation', 'message', 'frontendSecretKey',
            'name', 'email'
        ]


class CreateResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Note
        fields = [
            'createdAt', 'destroyTime', 'url', 'askForConfirmation', 'message', 'name', 'email'
        ]
