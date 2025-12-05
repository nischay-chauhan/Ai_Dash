import requests
import random
import string
import os

BASE_URL = "http://127.0.0.1:8000"

def get_random_string(length=10):
    return ''.join(random.choice(string.ascii_lowercase) for i in range(length))

def verify_backend():
    print("Starting backend verification...")
    
    # 1. Signup
    email = f"test_{get_random_string()}@example.com"
    password = "password123"
    print(f"Creating user: {email}")
    
    response = requests.post(f"{BASE_URL}/auth/signup", json={
        "email": email,
        "password": password,
        "role": "user"
    })
    
    if response.status_code != 200:
        print(f"Signup failed: {response.text}")
        return
    
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("Signup successful, token received.")
    
    # 2. Upload File
    filename = f"test_{get_random_string()}.csv"
    content = "col1,col2\nval1,val2"
    
    # Create dummy file
    with open(filename, "w") as f:
        f.write(content)
        
    print(f"Uploading file: {filename}")
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "text/csv")}
        response = requests.post(f"{BASE_URL}/upload/", files=files, headers=headers)
        
    if response.status_code != 202:
        print(f"Upload failed: {response.text}")
        os.remove(filename)
        return
        
    print("Upload successful.")
    
    # 3. List Uploads
    print("Listing uploads...")
    response = requests.get(f"{BASE_URL}/upload/", headers=headers)
    
    if response.status_code != 200:
        print(f"List uploads failed: {response.text}")
        os.remove(filename)
        return
        
    uploads = response.json()
    print(f"Found {len(uploads)} uploads.")
    
    found = False
    for upload in uploads:
        if upload["filename"] == filename:
            found = True
            print(f"Verified upload: {upload['filename']}, Status: {upload['status']}")
            break
            
    if found:
        print("Verification PASSED!")
    else:
        print("Verification FAILED: Uploaded file not found in list.")
        
    # Cleanup
    os.remove(filename)

if __name__ == "__main__":
    try:
        verify_backend()
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Make sure the backend is running on http://127.0.0.1:8000")
