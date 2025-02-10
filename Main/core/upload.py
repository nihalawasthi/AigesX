import requests
import sys
import os
import webbrowser

def upload_report(report_path, auth_token):
    url = "http://127.0.0.1:8000/api/upload-report/"
    email = input("Enter your registered email: ")
    
    headers = {
        'Authorization': f'Bearer {auth_token}'
    }

    try:
        with open(report_path, 'rb') as f:
            files = {'file': (os.path.basename(report_path), f, 'application/json')}
            data = {'email': email}  # Include email in form data
            
            response = requests.post(url, headers=headers, files=files, data=data)
        
        if response.status_code in [200, 201]:
            print(f"{response.text}")
            os.remove(report_path)
            webbrowser.open("http://localhost:5174/")
        else:
            print(f"Failed to upload report. Status code: {response.status_code}\n{response.text}")
    except Exception as e:
        print(f"Error uploading report file: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    report_path = 'C:/Users/draco/OneDrive/Documents/AigesX test/20250203_104013_report.json'
    auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzM5MTg0MTQ2LCJpYXQiOjE3MzkwOTc3NDYsImp0aSI6IjkzZGIxYTQ4ZGQ1NTRlZTZiN2IxZmJiMjNmNGFlZTM3IiwidXNlcl9pZCI6MSwidXNlcm5hbWUiOiJtb3JwaGV1cyJ9.JYMZWgv2RoVhneS6UBXLjTo_QB0iNQdOnwe_8XrV5K8"
    upload_report(report_path, auth_token)