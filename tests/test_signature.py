#!/usr/bin/env python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'lib'))

import json
import unittest

import payswarm
import pyld

class TestSignVerify(unittest.TestCase):

    def setUp(self):
        self.data = {
            '@context': [
                'https://w3id.org/payswarm/v1',
                {
                    'ex': 'http://example.com/',
                    'id': 'http://example.com/id/',
                },
            ],
            '@id': 'id:1',
            'ex:foo': 'bar'
        }
        self.assertTrue(
                os.path.exists('payswarm.cfg'), "payswarm.cfg not found")
        self.config = json.load(open('payswarm.cfg'))

    def test_hash(self):
        h = payswarm.util.hash(self.data)
        self.assertEqual(h, 'urn:sha256:0ae78459e1309a368f22265e047d94407907dd16234fa5629f415c6eb12ef0b3')

    def test_verify_signed(self):
        # no signature yet
        self.assertFalse('signature' in self.data)

        # sign
        signed = payswarm.signature.sign(self.data,
                self.config['publicKey']['id'],
                self.config['publicKey']['privateKeyPem'])

        # signature not added to original
        self.assertFalse('signature' in self.data)
        # signature added to result
        self.assertTrue('signature' in signed)

        # no source signature
        with self.assertRaises(Exception):
            payswarm.signature.verify(self.data)

        # valid signature
        self.assertTrue(payswarm.signature.verify(signed))

        # signature still present
        self.assertTrue('signature' in signed)

if __name__ == '__main__':
    unittest.main()
