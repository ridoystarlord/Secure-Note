from rest_framework.response import Response
from rest_framework import status
from cryptography.fernet import Fernet


def note_destroyed():
    return Response({'message': "This Note is Already Destroyed.", "isDestroyed": True},
                    status=status.HTTP_200_OK)


def password_not_match():
    return Response({"message": "Password and Confirm Password didn't match"},
                    status=status.HTTP_400_BAD_REQUEST)


def bytes_to_string(key):
    return str(key, "utf-8")


def string_to_bytes(key):
    return bytes(key, "utf-8")


def encrypt_message(message, secretkey):
    ferne_key = Fernet.generate_key()
    fernet_obj = Fernet(ferne_key)
    encryptmessage = bytes_to_string(fernet_obj.encrypt(message.encode()))
    encryptFrontendKey = bytes_to_string(fernet_obj.encrypt(secretkey.encode()))
    encryptbackendKey = bytes_to_string(ferne_key)
    return [encryptmessage, encryptFrontendKey, encryptbackendKey]


def decrypt_message(message, frontendsecretkey, backendsecretkey):
    fernet_obj = Fernet(string_to_bytes(backendsecretkey))
    decryptessage = fernet_obj.decrypt(string_to_bytes(message)).decode()
    decryptFrontendKey = fernet_obj.decrypt(string_to_bytes(frontendsecretkey)).decode()
    return [decryptessage, decryptFrontendKey]
