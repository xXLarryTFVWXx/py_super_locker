import os, sys, shutil, base64, hashlib, cryptography, zipfile
from zlib import compress

from cryptography import fernet

if not sys.platform == "win32":
    raise SystemExit("This program is only for Windows.")



def lock(source, username, password, locker_mode=0):
    """
        locker_mode may be one of the following
        0: file
        1: directory
    """
    base_password = hashlib.sha256(password.encode()).digest()
    b64_encoded_password = base64.b64encode(base_password)
    fernet_object = cryptography.fernet.Fernet(b64_encoded_password)
    encrypted_password = fernet_object.encrypt(password.encode())
    encrypted_uname = fernet_object.encrypt(username.encode()).decode()
    if locker_mode == 0:
        if not os.path.isfile(source):
            raise SystemExit("Source is not a file.")
        else:
            with open(source, "rb") as f:
                data = f.read()
            encrypted_data = fernet_object.encrypt(data)
            with open("result.txt", "w") as dummy:
                dummy.write("1")
            with open(f"result.txt:{encrypted_uname}", "wb") as f:
                f.write(encrypted_password)
            with open(f"result.txt:{encrypted_uname}_F", "wb") as f:
                f.write(encrypted_data)
            os.remove(source)
    elif locker_mode == 1:
        if not os.path.isdir(source):
            raise SystemExit("Source is not a directory.")
        else:
            with zipfile.ZipFile("result.zip", "w") as z:
                for root, dirs, files in os.walk(source):
                    for file in files:
                        z.write(os.path.join(root, file))
            with open("result.zip", "rb") as f:
                data = f.read()
            with open("result.txt", "w") as dummy:
                dummy.write("1")
            with open(f"result.txt:{encrypted_uname}", "wb") as f:
                f.write(encrypted_password)
            with open(f"result.txt:{encrypted_uname}_D", "wb") as f:
                f.write(encrypted_data)
            shutil.rmtree(source)
            os.remove("result.zip")

def unlock(username, password, locker_mode=0): # 0 = file, 1 = directory
    base_password = hashlib.sha256(password.encode()).digest()
    b64_encoded_password = base64.b64encode(base_password)
    fernet_object = cryptography.fernet.Fernet(b64_encoded_password)
    encrypted_password = fernet_object.encrypt(password.encode())
    encrypted_uname = fernet_object.encrypt(username.encode()).decode()
    try:
        with open(f"result.txt:{encrypted_uname}", "rb") as f:
            test_data = f.read()
            fernet_object.decrypt(test_data)
            print(test_data)
    except FileNotFoundError as err:
        print(f"{err.args=}")
    except cryptography.fernet.InvalidToken as err:
        raise SystemExit(f"{err.args=}")
    if not os.path.isfile("result.txt"):
        raise SystemExit("Unable to open File/Folder.")
    testing_file = f"result.txt:{encrypted_uname}"
    with open("result.txt", "rb") as f:
        if f.read() == "1":
            with open(f"{testing_file}:$DATA", "rb") as f:
                encrypted_password = f.read()
    if fernet_object.decrypt(encrypted_password) == password.encode():
        with open(f"{testing_file}_F:$DATA", "rb") as f:
            encrypted_data = f.read()
            #decrypt data
            decrypted_data = fernet_object.decrypt(encrypted_data)
            #get the file name from the decrypted data
            decrypted_zipfile = zipfile.ZipFile(decrypted_data)
            decrypted_zipfile.extractall(decrypted_zipfile.namelist()[0])
            decrypted_zipfile.close()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        if sys.argv[1] == "lock":
            source = input("Enter the source file/folder: ")
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            if os.path.isfile(source):
                locker_mode = 0
            elif os.path.isdir(source):
                locker_mode = 1
            else:
                raise SystemExit("Source is not a file or directory.")
            lock(source, username, password, locker_mode)
        elif sys.argv[1] == "unlock":
            username = input("Enter the username: ")
            password = input("Enter the password: ")
            unlock(username, password)
        else:
            raise SystemExit("Invalid command.")
    else:
        raise SystemExit("Invalid number of arguments.")
