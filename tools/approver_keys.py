"""Make an Ed25519 key pair for an approver (added 9 Nov 2026).

    python tools/approver_keys.py tdra-duty-officer

Prints the PUBLIC key (register it as public_key in kb/approvers.yaml) and the PRIVATE key (the approver keeps it,
e.g. export HISN_PRIV_TDRA_DUTY_OFFICER=<hex>; never commit it). Verification needs only the public key.
"""
import sys
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives import serialization as S

if len(sys.argv) != 2: sys.exit(__doc__)
k = ed25519.Ed25519PrivateKey.generate()
priv = k.private_bytes(S.Encoding.Raw, S.PrivateFormat.Raw, S.NoEncryption()).hex()
pub = k.public_key().public_bytes(S.Encoding.Raw, S.PublicFormat.Raw).hex()
env = "HISN_PRIV_" + sys.argv[1].upper().replace("-", "_")
print(f"public_key for {sys.argv[1]} (put in kb/approvers.yaml): {pub}")
print(f"private key (keep secret, never commit):  export {env}={priv}")
