import json
import hashlib

from cryptography.hazmat.primitives.asymmetric import ed25519, rsa

from ..__polyfill.datetime import utcnow
from ..utils.multibase import multibase_encode

class OIPSigner:
    def __init__(self, private_key: ed25519.Ed25519PrivateKey | rsa.RSAPrivateKey):
        self.private_key: ed25519.Ed25519PrivateKey | rsa.RSAPrivateKey = private_key

    def canonicalize(self, data: dict) -> bytes:
        return json.dumps(data, sort_keys=True).encode('utf-8')

    def hash_data(self, canonical_data) -> bytes:
        return hashlib.sha256(canonical_data).digest()

    def sign_hash(self, data_hash: bytes) -> bytes:
        return self.private_key.sign(data_hash)

    def sign(self, json_object: dict, publickey_url: str):
        canonical_data = self.canonicalize(json_object)
        data_hash: bytes = self.hash_data(canonical_data)
        signature: bytes = self.sign_hash(data_hash)
        proof = {
            "@context": [
                "https://www.w3.org/ns/activitystreams",
                "https://w3id.org/security/data-integrity/v1"
            ],
            "type": "DataIntegrityProof",
            "cryptosuite": "eddsa-jcs-2022",
            "verificationMethod": publickey_url,
            "proofPurpose": "assertionMethod",
            "proofValue": multibase_encode(signature, "base58btc"),
            "created": utcnow().isoformat() + "Z"
        }

        json_object['proof'] = proof
        return json_object
