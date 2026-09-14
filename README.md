# apsig
![PyPI](https://img.shields.io/pypi/v/apsig) [![CodeQL](https://github.com/AmaseCocoa/apsig/actions/workflows/github-code-scanning/codeql/badge.svg?branch=main)](https://github.com/AmaseCocoa/apsig/actions/workflows/github-code-scanning/codeql)

> [!WARNING]
> **Minimal Maintenance Only**
> This library is stable and completed, but is now in minimal maintenance mode (critical bug fixes only). For more context on the fedi-libs ecosystem, please read our discussion: [**Project Status**](https://github.com/orgs/fedi-libs/discussions/2).

apsig is collection of signature implemention used in ActivityPub.

This library implements the creation/verification of signatures for HTTP Signatures ([draft-cavage-http-signatures-12](https://datatracker.ietf.org/doc/html/draft-cavage-http-signatures-12)), [Linked Data Signatures 1.0](https://docs.joinmastodon.org/spec/security/#ld), and Object Integrity Proofs ([FEP-8b32](https://codeberg.org/fediverse/fep/src/branch/main/fep/8b32/fep-8b32.md)).

[RFC9421](https://datatracker.ietf.org/doc/html/rfc9421) implementation is progress.

## Installation

```bash
# pip
pip install apsig

# uv
uv add apsig

# pdm
pdm add apsig
```

## Example

First, prepare the keys for signing and verification. `apsig` uses the `cryptography` library.

```python
from cryptography.hazmat.primitives.asymmetric import rsa, ed25519
from cryptography.hazmat.primitives import serialization

# For HTTP Signatures (RSA)
private_key_rsa = rsa.generate_private_key(public_exponent=65537, key_size=3092)
public_key_rsa_pem = private_key_rsa.public_key().public_bytes(
    encoding=serialization.Encoding.PEM,
    format=serialization.PublicFormat.SubjectPublicKeyInfo,
)

# For Object Integrity Proofs (Ed25519)
private_key_ed = ed25519.Ed25519PrivateKey.generate()
public_key_ed = private_key_ed.public_key()
```

### HTTP Signature (draft)

This is used for signing HTTP requests.

```python
import email.utils
from apsig.draft import Signer, Verifier

# === Signing ===
method = "POST"
url = "https://example.com/api/resource"
headers = {
    "Content-Type": "application/json",
    "Date": email.utils.formatdate(usegmt=True),
}
body = '{"key": "value"}'
key_id = "https://example.com/users/johndoe#main-key"

signer = Signer(
    headers=headers,
    private_key=private_key_rsa,
    method=method,
    url=url,
    key_id=key_id,
    body=body.encode("utf-8"),
)
signed_headers = signer.sign()

print(signed_headers)

# === Verifying ===
verifier = Verifier(
    public_pem=public_key_rsa_pem.decode("utf-8"),
    method=method,
    url=url,
    headers=signed_headers,
    body=body.encode("utf-8"),
)
verified_key_id = verifier.verify(raise_on_fail=True)

print(f"Verified with key: {verified_key_id}")
```

### Object Integrity Proofs (proof)

This is used for signing JSON objects (like ActivityStreams objects).

```python
from apsig import ProofSigner, ProofVerifier

# === Signing ===
json_object = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/data-integrity/v1",
    ],
    "id": "https://server.example/objects/1",
    "type": "Note",
    "content": "Hello world",
}
proof_options = {
    "type": "DataIntegrityProof",
    "cryptosuite": "eddsa-jcs-2022",
    "verificationMethod": "https://example.com/keys/1",
    "created": "2024-01-01T09:00:00Z",
}

signer = ProofSigner(private_key_ed)
signed_object = signer.sign(json_object, proof_options)

print(signed_object)

# === Verifying ===
verifier = ProofVerifier(public_key_ed)
verified_key_id = verifier.verify(signed_object, raise_on_fail=True)

print(f"Verified with key: {verified_key_id}")
```

### Linked Data Signature (LD-Signature)

This is another method for signing JSON-LD objects, often used in older ActivityPub implementations.

```python
from apsig import LDSignature

# === Signing ===
ld_signer = LDSignature()
json_ld_object = {
    "@context": [
        "https://www.w3.org/ns/activitystreams",
        "https://w3id.org/security/v1",
    ],
    "type": "Note",
    "content": "Hello, Linked Data!",
}
creator = "https://example.com/users/johndoe#main-key"

signed_ld_object = ld_signer.sign(
    doc=json_ld_object,
    creator=creator,
    private_key=private_key_rsa
)

print(signed_ld_object)

# === Verifying ===
# The public key can be passed directly.
public_key_rsa = private_key_rsa.public_key()
verified_creator = ld_signer.verify(
    doc=signed_ld_object,
    public_key=public_key_rsa,
    raise_on_fail=True
)

print(f"Verified with creator: {verified_creator}")
```

## Documents
The document can be viewed [here](https://fedi-libs.github.io/apsig/).

## Thanks
- [Hong Minhee](https://github.com/dahlia) ([Fedify](https://fedify.dev/) Author)
- [Takahē](https://github.com/jointakahe/takahe) Authors (apsig.LDSignature was ported from Takahē)
- And All Contributor/Users

## License
MIT License
