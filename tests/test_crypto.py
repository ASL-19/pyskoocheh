# -*- coding: utf-8 -*-
""" Unit tests for Crypto utility Module

"""

import unittest
import pgpy
    
from pyskoocheh import crypto

class BasicTests(unittest.TestCase):
    private_key_file  = 'tests/test_files/asl19_gpg_test_key.asc'
    private_key_password = 'olaghekadkhoda'
    test_message='this order should be signed'

    def test_signing(self):
        test_signer = crypto.SignatureManager(self.private_key_file, self.private_key_password)

        signature = test_signer.sign_string(self.test_message)
        self.assertTrue(bool(test_signer.signing_key.verify(self.test_message, pgpy.PGPSignature.from_blob(signature))))

if __name__ == "__main__":
    unittest.main()
