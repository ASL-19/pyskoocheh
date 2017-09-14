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
    test_filename = "tests/test_files/authentic_dog.jpg"
    test_checksum = "0ebb42d3073050b283735a6123af78c8130d8f8401de4968b3edbb926c92c672"

    def test_signing(self):
        test_signer = crypto.SignatureManager(self.private_key_file, self.private_key_password)

        signature = test_signer.sign_string(self.test_message)
        self.assertTrue(bool(test_signer.signing_key.verify(self.test_message, pgpy.PGPSignature.from_blob(signature))))
    def test_checksum_calculation(self):
        test_signer = crypto.SignatureManager(self.private_key_file, self.private_key_password)
        with open(self.test_filename, "rb") as test_file:
            computed_checksum = test_signer.calc_compute_checksum(test_file)
            self.assertEqual(self.test_checksum, computed_checksum)
        

    def test_always_read_from_the_beginning(self):
        test_signer = crypto.SignatureManager(self.private_key_file, self.private_key_password)
        with open(self.test_filename, "rb") as test_file:
            test_file.seek(0,2)
            computed_checksum = test_signer.calc_compute_checksum(test_file)
            self.assertEqual(self.test_checksum, computed_checksum)

if __name__ == "__main__":
    unittest.main()
