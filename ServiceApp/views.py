from django.contrib.auth.hashers import make_password
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ServiceApp.models import Note
from ServiceApp.serializers import NoteSerializer
from cryptography.fernet import Fernet
import shortuuid


class CreateNewNote(APIView):
    def post(self, request, format=None):
        data = request.data
        if data['password']:
            if data['password'] == data['confirmPassword']:
                data['password'] = make_password(data['password'])
                data['confirmPassword'] = make_password(data['confirmPassword'])
                data['hasPassword'] = True
            else:
                return Response({"message": "Password and Confirm Password didn't match"},
                                status=status.HTTP_400_BAD_REQUEST)
        ferne_key = Fernet.generate_key()
        fernet_obj = Fernet(ferne_key)
        encryptMessage = fernet_obj.encrypt(data['message'].encode())
        encryptStringMessage = str(encryptMessage, 'utf-8')
        encryptFrontendKey = fernet_obj.encrypt(data['frontendSecretKey'].encode())
        encryptFrontendKeyString = str(encryptFrontendKey, 'utf-8')
        keyString = str(ferne_key, "utf-8")
        # t = bytes(a, 'utf-8')
        data['message'] = encryptStringMessage
        data['frontendSecretKey'] = encryptFrontendKeyString
        data['backendSecretKey'] = keyString
        data['url'] = shortuuid.uuid()

        serializer = NoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetNoteDetails(APIView):
    def get_object(self, pk):
        try:
            return Note.objects.get(url=pk)
        except Note.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = NoteSerializer(snippet)
        return Response(serializer.data)

    def put(self, request, pk, format=None):
        snippet = self.get_object(pk)
        serializer = NoteSerializer(snippet, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        snippet = self.get_object(pk)
        snippet.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
