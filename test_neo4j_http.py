import requests

def test_http_connection():
    try:
        # Try to connect to Neo4j Browser HTTP endpoint
        response = requests.get('http://localhost:7474')
        print(f"HTTP Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        
    except Exception as e:
        print(f"Failed to connect via HTTP: {str(e)}")

if __name__ == "__main__":
    test_http_connection()
