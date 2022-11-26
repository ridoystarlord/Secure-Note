from django.contrib.auth.hashers import make_password, check_password
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from ServiceApp.models import Note
from ServiceApp.serializers import NoteSerializer, CreateResponseSerializer, ResponseSerializer
from cryptography.fernet import Fernet
import shortuuid
from datetime import datetime


class CreateNewNote(APIView):
    def post(self, request, format=None):
        data = request.data
        if data['password']:
            if data['password'] == data['confirmPassword']:
                data['password'] = make_password(data['password'])
            else:
                return Response({"message": "Password and Confirm Password didn't match"},
                                status=status.HTTP_400_BAD_REQUEST)
        ferne_key = Fernet.generate_key()
        keyString = str(ferne_key, "utf-8")
        fernet_obj = Fernet(ferne_key)

        encryptMessage = fernet_obj.encrypt(data['message'].encode())
        encryptStringMessage = str(encryptMessage, 'utf-8')

        encryptFrontendKey = fernet_obj.encrypt(data['frontendSecretKey'].encode())
        encryptFrontendKeyString = str(encryptFrontendKey, 'utf-8')

        data['message'] = encryptStringMessage
        data['frontendSecretKey'] = encryptFrontendKeyString
        data['backendSecretKey'] = keyString
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
        try:
            return Note.objects.get(url=pk)
        except Note.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        note = self.get_object(pk)
        serializer = NoteSerializer(note)
        data = serializer.data

        ferne_key = bytes(data['backendSecretKey'], 'utf-8')
        byteskey = bytes(data['frontendSecretKey'], 'utf-8')
        bytesMessage = bytes(data['message'], 'utf-8')
        fernet_obj = Fernet(ferne_key)
        decryptMessage = fernet_obj.decrypt(bytesMessage).decode()
        decryptFrontendKey = fernet_obj.decrypt(byteskey).decode()

        if data['isDestroyed']:
            note.delete()
            return Response({'message': "This Note is Already Destroyed.", "isDestroyed": True},
                            status=status.HTTP_404_NOT_FOUND)
        else:
            if data['password']:
                return Response({
                    "message": "You will be asked for the password to read the note. If you don't have it, ask the person who sent you the note for it, before proceeding.",
                    "hasPassword": True})
            elif data['destroyTime'] is not None and datetime.utcnow().isoformat() > data['destroyTime']:
                note.delete()
                return Response({'message': "This Note is Already Destroyed.", "isDestroyed": True},
                                status=status.HTTP_404_NOT_FOUND)
            elif data['destroyTime'] is None:
                data['isDestroyed'] = True
                updateSerializer = NoteSerializer(note, data=data)
                if updateSerializer.is_valid():
                    updateSerializer.save()
                    responseSerializer = ResponseSerializer(updateSerializer.data)
                    updateData = responseSerializer.data
                    updateData["isDestroyed"] = False
                    updateData["message"] = decryptMessage
                    updateData["frontendSecretKey"] = decryptFrontendKey
                    return Response(updateData, status=status.HTTP_200_OK)
                return Response(updateSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                responseSerializer = ResponseSerializer(note)
                updateData = responseSerializer.data
                updateData["isDestroyed"] = False
                updateData["message"] = decryptMessage
                updateData["frontendSecretKey"] = decryptFrontendKey
                return Response(updateData, status=status.HTTP_200_OK)

    def delete(self, request, pk, format=None):
        note = self.get_object(pk)
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetPasswordProtectedNoteDetails(APIView):
    def get_object(self, pk):
        try:
            return Note.objects.get(url=pk)
        except Note.DoesNotExist:
            raise Http404

    def post(self, request, pk, format=None):
        note = self.get_object(pk)
        serializer = NoteSerializer(note)
        data = serializer.data
        print(data)
        ferne_key = bytes(data['backendSecretKey'], 'utf-8')
        byteskey = bytes(data['frontendSecretKey'], 'utf-8')
        bytesMessage = bytes(data['message'], 'utf-8')
        fernet_obj = Fernet(ferne_key)

        decryptMessage = fernet_obj.decrypt(bytesMessage).decode()
        decryptFrontendKey = fernet_obj.decrypt(byteskey).decode()

        requestBody = request.data

        if requestBody['password'] == requestBody['confirmPassword']:
            if check_password(requestBody['password'], data['password']):
                if data['isDestroyed']:
                    note.delete()
                    return Response({'message': "This Note is Already Destroyed.", "isDestroyed": True},
                                    status=status.HTTP_404_NOT_FOUND)
                if data['destroyTime'] is None:
                    data['isDestroyed'] = True
                    updateSerializer = NoteSerializer(note, data=data)
                    if updateSerializer.is_valid():
                        updateSerializer.save()
                        responseSerializer = ResponseSerializer(updateSerializer.data)
                        updateData = responseSerializer.data
                        updateData["isDestroyed"] = False
                        updateData["message"] = decryptMessage
                        updateData["frontendSecretKey"] = decryptFrontendKey
                        return Response(updateData, status=status.HTTP_200_OK)
                    return Response(updateSerializer.errors, status=status.HTTP_400_BAD_REQUEST)
                if data['destroyTime'] is not None and datetime.utcnow().isoformat() > data['destroyTime']:
                    note.delete()
                    return Response({'message': "This Note is Already Destroyed.", "isDestroyed": True},
                                    status=status.HTTP_404_NOT_FOUND)
                data["message"] = decryptMessage
                data["frontendSecretKey"] = decryptFrontendKey
                responseData = ResponseSerializer(data)
                return Response(responseData.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Password and Confirm Password didn't match"},
                                status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Password and Confirm Password didn't match"},
                        status=status.HTTP_400_BAD_REQUEST)
