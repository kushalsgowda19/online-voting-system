import requests

def test_auth():
    # First, get a token
    login_url = 'http://localhost:8000/api/token/'
    login_data = {
        'username': 'admin2',
        'password': 'admin123'
    }
    
    try:
        # Get token
        response = requests.post(login_url, data=login_data)
        response.raise_for_status()
        access_token = response.json().get('access')
        print(f"Got access token: {access_token[:20]}...")
        
        # Test the user endpoint
        user_url = 'http://localhost:8000/api/auth/user/'
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        user_response = requests.get(user_url, headers=headers)
        print(f"Status Code: {user_response.status_code}")
        print(f"Response: {user_response.text}")
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    test_auth()
