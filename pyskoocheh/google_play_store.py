# -*- coding: utf-8 -*-
#
# Copyright (C) 2017  ASL19
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

""" Google Play Store Token Dispenser

This program obtains Google Play Store authentication tokens.

These tokens are necessary in order to access the Google Play API, since
having a valid username and password no longer works for the existing
Google Play API python modules.

This module can also be run from shell, to obtain a token directly.

Example:
    $ python google_token_dispense.py <e-mail> <password>
"""

import sys
import struct
import requests
import re
from base64 import b64encode, b64decode
from binascii import hexlify
from hashlib import sha1
from Crypto.PublicKey.RSA import construct
from Crypto.Cipher import PKCS1_OAEP


class GooglePlayStoreTokenDispenser(object):
    """ Obtains Google Play Store authentication tokens.

    This class is responsible for retrieving Google Play Store tokens.

    Attributes:
    @type email: str
        The E-mail to be used for authentication.
    @type password: str
        The password corresponding to the E-mail.
    """

    _URL_LOGIN = 'https://android.clients.google.com/auth'
    _GOOGLE_DEFAULT_PUB_KEY = ('AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveW'
                               'LEwo6prwgi3iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3b'
                               'aEVGcmEgqaLZUNBjm057pKRI16kB0YppeGx5qIQ5QjKzsR'
                               '8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/6rmf5AAAAAwEA'
                               'AQ==')

    _DEFAULT_LOGIN_PARAMS = {
        'sdk_version':          '23',
        'service':              'androidmarket',
    }


    def __init__(self, email=None, password=None):
        self._email = email
        self._password = password


    def set_credentials(self, email, password):
        """ Setter for the required credentials.

        Attributes:
        @type email: str
            The E-mail to be used for authentication.
        @type password: str
            The password corresponding to the E-mail.
        """
        self._email = email
        self._password = password
        return self


    def get_token(self, email=None, password=None):
        """ Main function for retrieving a valid Google Play Store token.

        Attributes:
        @type email: str
            The E-mail to be used for authentication.
        @type password: str
            The password corresponding to the E-mail.
        """

        if ( not self._email and not self._password and
             not email and not password ):
            raise MissingCredentialsException(
                    'The credentials have not been set.')

        email = self._email
        password = self._password

        login_params = self._DEFAULT_LOGIN_PARAMS.copy()
        login_params['Email'] = email,
        login_params['EncryptedPasswd'] = self._encrypt_passwd(email, password)
        response = requests.post(self._URL_LOGIN, data=login_params)

        if response.status_code != 200      or   \
           'Auth' not in response.text      or   \
           'Token' not in response.text:

            raise BadAuthenticationError('Bad Authentication: '
                                         'Are you credentials correct?')

        token = re.search('Auth=([^\n]*)\n', response.text).groups()[0]
        return token


    def _encrypt_passwd(self, email, password):
        """ Encrypts credentials with Google's default public key

        Given an email and password, returns an encrypted and encoded version
        of the credentials using Google's default public key and methods
        that Google can be expected to decrypted.

        Attributes:
        @type email: str
            The email that will be encrypted in the cipher.
        @type password: str
            The password that will be encrypted in the cipher.
        """

        read_int = lambda array_of_byte, start_position:                    \
                        (struct.unpack('i', array_of_byte[start_position:   \
                                                          start_position+4] \
                                                         [::-1])[0])

        # Obtain Cipher
        # 1. Convert Google login public key from base64 to byte[]
        binary_key = bytearray(b64decode(self._GOOGLE_DEFAULT_PUB_KEY))

        # 2. Calculate RSA public key modulus
        i = read_int(binary_key, 0)
        half = binary_key[4: i + 4]
        key_modulus = long(hexlify(half), 16)

        # 3. Calculate RSA public key exponent
        j = read_int(binary_key, i + 4)
        half = binary_key[i + 8: i + 8 + j]
        key_exponent = long(hexlify(half), 16)

        # 4. Construct Public Key using the key modulus and exponent
        public_key = construct((key_modulus, key_exponent))

        # 5. Obtain cipher using public key
        cipher = PKCS1_OAEP.new(public_key)


        # Encrypt Credentials
        # 6. Concatenate credentials with null character separator
        combined = email + '\0' + password

        # 7. Convert to bytes
        combined_bytes = bytearray(combined.encode('utf-8'))

        # 8. Encrypt bytes with public key
        encrypted = cipher.encrypt(str(combined_bytes))


        # Create signature
        # 9. Calculate SHA-1 of the public key
        pub_sha1 = bytearray(sha1(binary_key).digest())

        # 10. Signature
        # signature[0] = 0
        # signature[1:5] = first 4 bytes of sha-1 of public key
        # signature[5:133] = encrypted credentials
        signature = bytearray(1)
        signature[0] = 0
        signature.extend(pub_sha1[:4])
        signature.extend(encrypted)

        # Must contain URL safe characters after b64 encoding
        return b64encode(signature).encode('ascii')     \
                                   .replace('+', '-')   \
                                   .replace('/', '_')

class MissingCredentialsException(Exception):
    """ Custom exception for attempting to obtain a token without credentials.
    """
    pass

class BadAuthenticationError(Exception):
    """ Custom error for bad authentication error returned by Google.
    """
    pass

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('Usage: python google_play_store <email> '
              '<password>')
    else:
        email = sys.argv[1]
        password = sys.argv[2]
        token = GooglePlayStoreTokenDispenser(email, password).get_token()
        print
        print('Google Play Store Authentication Token:')
        print
        print(token)

