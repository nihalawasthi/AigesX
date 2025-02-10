import requests
import sys
import os
import webbrowser

def upload_report(report_path):
    url = "http://127.0.0.1:8000/api/upload-report/"
    email = input("Enter your registered email: ")

    try:
        with open(report_path, 'rb') as f:
            files = {'file': (os.path.basename(report_path), f, 'application/json')}
            data = {'email': email}  # Include email in form data
            
            response = requests.post(url, files=files, data=data)
        
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
    report_path = 'C:/My/Projects/_Python/AigesX/20250203_104013_report.json'
    upload_report(report_path)