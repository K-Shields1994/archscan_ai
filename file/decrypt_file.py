from cryptography.fernet import Fernet


# Load the encryption key
def load_key():
    return open("secret.key", "rb").read()


# Decrypt the contents of the file
def decrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)

    with open(file_path, "rb") as encrypted_file:
        encrypted_data = encrypted_file.read()

    # Decrypt the file data
    decrypted = fernet.decrypt(encrypted_data)

    # Write the decrypted file
    with open(file_path, "wb") as decrypted_file:
        decrypted_file.write(decrypted)


if __name__ == "__main__":
    decrypt_file("/Volumes/SSD/python_projects/archscan_ai/azure_credentials.txt")
