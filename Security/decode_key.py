import base64
import string

ciphertexts = [
    "BiA8RSIrPhE4JjFULzA1VC9lP145ZS1eJiorQyQyeVA/ZWoRGwh3EQgqN1cuNzxfKCB5QyQqNBEJaw==",
    "GyQqQjwqK1VrNzxCLjF5XSIrMgtrLS1FOzZjHmQsN0UuNzdQJ2stWSZqK1Q4IC0OPyoyVCV4OFModGsC",
    "GAAaYw4RYxEfDRRKHAAYehQGC2gbERZuDQkYdjZldBEPKnlfJDF5QiMkK1RrMTFYOGUuWD8teUQlJCxFIyorWDEgPRE7ICtCJCs3VCdr"
]

chars = string.ascii_letters + string.digits

for c in chars:
    key = ("KEY" + c).encode()

    print("=" * 60)
    print("Trying key:", key.decode())

    ok = True

    for ct in ciphertexts:
        data = base64.b64decode(ct)
        pt = bytes(data[i] ^ key[i % 4] for i in range(len(data)))

        try:
            text = pt.decode("utf-8")
            print(text)
        except:
            ok = False
            break

    if ok:
        print("Candidate key:", key.decode())
