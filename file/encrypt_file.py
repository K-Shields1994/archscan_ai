from cryptography.fernet import Fernet


# Generate a key and save it into a file (do this only once and store it securely)
def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


# Load the encryption key from a file
def load_key():
    return open("secret.key", "rb").read()


# Encrypt the contents of the file
def encrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)

    with open(file_path, "rb") as file:
        original = file.read()

    # Encrypt the file data
    encrypted = fernet.encrypt(original)

    # Write the encrypted file
    with open(file_path, "wb") as encrypted_file:
        encrypted_file.write(encrypted)


if __name__ == "__main__":
    generate_key()  # Only run this once to generate the key
    encrypt_file("/Volumes/SSD/python_projects/archscan_ai/azure_credentials.txt")
