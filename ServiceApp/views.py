from django.contrib.auth.hashers import make_password, check_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ServiceApp.models import Note
from ServiceApp.serializers import NoteSerializer, CreateResponseSerializer, ResponseSerializer
import shortuuid
from datetime import datetime

from ServiceApp.utils import note_destroyed, password_not_match, encrypt_message, decrypt_message


class CreateNewNote(APIView):
    def post(self, request, format=None):
        data = request.data
        if data['password']:
            if data['password'] == data['confirmPassword']:
                data['password'] = make_password(data['password'])
            else:
                return password_not_match()

        encryptData = encrypt_message(data['message'], data['frontendSecretKey'])

        data['message'] = encryptData[0]
        data['frontendSecretKey'] = encryptData[1]
        data['backendSecretKey'] = encryptData[2]
        data['url'] = shortuuid.uuid()

        serializer = NoteSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            createResponseSerializer = CreateResponseSerializer(serializer.data)
            updateData = createResponseSerializer.data
            updateData['message'] = "Note Created Successful"
            updateData['isDestroyed'] = False
            return Response(updateData, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetNoteDetails(APIView):
    def get_object(self, pk):
        return Note.objects.get(url=pk)

    def get(self, request, pk, format=None):
        try:
            note = self.get_object(pk)
            serializer = NoteSerializer(note)
            data = serializer.data

            decryptData = decrypt_message(data['message'], data['frontendSecretKey'], data['backendSecretKey'])

            if data['isDestroyed']:
                note.delete()
                return note_destroyed()
            else:
                if data['password']:
                    return Response({
                        "message": "You will be asked for the password to read the note. If you don't have it, ask the person who sent you the note for it, before proceeding.",
                        "hasPassword": True})
                elif data['destroyTime'] is not None and datetime.utcnow().isoformat() > data['destroyTime']:
                    note.delete()
                    return note_destroyed()
                elif data['destroyTime'] is None:
                    data['isDestroyed'] = True
                    updateSerializer = NoteSerializer(note, data=data)
                    if updateSerializer.is_valid():
                        updateSerializer.save()
                        responseSerializer = ResponseSerializer(updateSerializer.data)
                        updateData = responseSerializer.data
                        updateData["isDestroyed"] = False
                        updateData["message"] = decryptData[0]
                        updateData["frontendSecretKey"] = decryptData[1]
                        return Response(updateData, status=status.HTTP_200_OK)
                    return Response(updateSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
                else:
                    responseSerializer = ResponseSerializer(note)
                    updateData = responseSerializer.data
                    updateData["isDestroyed"] = False
                    updateData["message"] = decryptData[0]
                    updateData["frontendSecretKey"] = decryptData[1]
                    return Response(updateData, status=status.HTTP_200_OK)

        except Note.DoesNotExist:
            return note_destroyed()

    def delete(self, request, pk, format=None):
        note = self.get_object(pk)
        note.delete()
        return Response({'message': "Note Deleted Successfully"},
                        status=status.HTTP_204_NO_CONTENT)


class GetPasswordProtectedNoteDetails(APIView):
    def get_object(self, pk):
        return Note.objects.get(url=pk)

    def post(self, request, pk, format=None):
        try:
            note = self.get_object(pk)
            serializer = NoteSerializer(note)
            data = serializer.data

            decryptData = decrypt_message(data['message'], data['frontendSecretKey'], data['backendSecretKey'])

            requestBody = request.data

            if requestBody['password'] == requestBody['confirmPassword']:
                if check_password(requestBody['password'], data['password']):
                    if data['isDestroyed']:
                        note.delete()
                        return note_destroyed()
                    if data['destroyTime'] is None:
                        data['isDestroyed'] = True
                        updateSerializer = NoteSerializer(note, data=data)
                        if updateSerializer.is_valid():
                            updateSerializer.save()
                            responseSerializer = ResponseSerializer(updateSerializer.data)
                            updateData = responseSerializer.data
                            updateData["isDestroyed"] = False
                            updateData["message"] = decryptData[0]
                            updateData["frontendSecretKey"] = decryptData[1]
                            return Response(updateData, status=status.HTTP_200_OK)
                        return Response(updateSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
                    if data['destroyTime'] is not None and datetime.utcnow().isoformat() > data['destroyTime']:
                        note.delete()
                        return note_destroyed()
                    data["message"] = decryptData[0]
                    data["frontendSecretKey"] = decryptData[1]
                    responseData = ResponseSerializer(data)
                    return Response(responseData.data, status=status.HTTP_200_OK)
                else:
                    return password_not_match()
            return password_not_match()
        except Note.DoesNotExist:
            return note_destroyed()
