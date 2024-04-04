import random


def gcd(a, b): # Definere største fælles deviser.
    while b:
        a, b = b, a % b
    return a

def mod_inverse(a, m):
    g, x, y = extended_gcd(a, m)
    if g != 1:
        raise Exception("Modulær invers findes ikke")
    return x % m

def extended_gcd(a, b):
    if a == 0:
        return b, 0, 1
    else:
        g, x, y = extended_gcd(b % a, a)
        return g, y - (b // a) * x, x
    
def generate_keypair(p, q):
    n = p * q # Modulus for både offentlig og privat nøgle
    phi = (p - 1) * (q - 1) # Eulers totient-funktion

    e = random.randrange(1, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(1, phi)

    d = mod_inverse(e, phi) # Privat eksponent

    return ((e, n), (d, n)) # Offentlig nøgle og privat nøgle

def encrypt(public_key, plaintext):
    e, n = public_key
    encrypted_msg = [pow(ord(char), e, n) for char in plaintext]
    return encrypted_msg

def decrypt(private_key, encrypted_msg):
    d, n = private_key
    decrypted_msg = [chr(pow(char, d, n)) for char in encrypted_msg]
    return ''.join(decrypted_msg)

p = 61
q = 53
public_key, private_key = generate_keypair(p, q)

message = input("Indtast en besked til at kryptere: ")

encrypted_message = encrypt(public_key, message)
print("Krypteret besked:", encrypted_message)

decrypted_message = decrypt(private_key, encrypted_message)
print("Dekrypteret besked:", decrypted_message)
