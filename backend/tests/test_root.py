from main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_read_root():
    """
    Test the root endpoint (/) for expected response.
    """
    # Send GET request to the root endpoint
    response = client.get("/")
    
    # Validate HTTP status code
    assert response.status_code == 200, "Expected status code 200 for root endpoint"
    
    # Validate JSON response structure
    expected_response = {"message": "Backend is working"}
    assert response.json() == expected_response, "Unexpected response from root endpoint"

    # Validate response content type
    assert response.headers["content-type"] == "application/json", "Expected JSON content type"

def test_root_invalid_method():
    """
    Test the root endpoint with an unsupported HTTP method (e.g., POST).
    """
    response = client.post("/")
    # Validate that unsupported methods return proper status
    assert response.status_code == 405, "Expected status code 405 for unsupported method"
