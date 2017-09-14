# -*- coding: utf-8 -*-
""" Crypto utility Module

    It provides functions necessary for cryptograhpic operation of the server
"""
import pgpy
import hashlib

class SignatureManager:
    """ decrypt the sigining private key and sign the files on demand
    """
    def __init__(self, signing_key_filename, signing_key_password):
        """ decrypt and store the sigining private key for later use.

        Args:
            signing_key_filename the file which contain the private signing key blob.
            signing_key_password the password to unlock the key
        """
        # load the key from file
        self.signing_key, _ = pgpy.PGPKey.from_file(signing_key_filename)
        self.signing_key_password = signing_key_password
        
    def calc_signature(self, file_to_be_signed):
        """
        Computes the pgp armored signature of the content of the file and return
        it as an string
        
        Args:
            file_to_be_signed:  FileField object which contain the submission to be signed

        Returns:
            Armored pgp signature of the file content
        """
        with self.signing_key.unlock(self.signing_key_password):
            file_to_be_signed.seek(0)
            message_to_be_signed = pgpy.PGPMessage.new(file_to_be_signed.read())
            return str(self.signing_key.sign(message_to_be_signed))

    def sign_string(self, string_to_be_signed):
        """
        Computes the pgp armored signature of the string message

        Args:
             string_to_be_signed the string who signature is seeked

        Return:
             Armored pgp signature of the file content of string_to_be_signed
        """
        with self.signing_key.unlock(self.signing_key_password):
            return str(self.signing_key.sign(string_to_be_signed))

    def calc_compute_checksum(self, file_to_be_summed):
        """
        Computes the sha256 hash of the file content and returns it as a hex 
        string

        Args:
            file_to_be_summed:  FileField object which contain the submission whose checksum is seeked

        Return:
            the sha256 hash value of the binary content of the file in hexadecimal representation.
        
        """
        file_to_be_summed.seek(0)
        return hashlib.sha256(file_to_be_summed.read()).hexdigest()
