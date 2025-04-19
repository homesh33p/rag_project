import pytest
from httpx import AsyncClient
from fastapi import status

# Example test for document creation endpoint
@pytest.mark.asyncio
async def test_create_document(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/documents",
        json={
            "title": "Test Document",
            "content": "This is a test document for testing purposes."
        }
    )
    
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["title"] == "Test Document"
    assert data["content"] == "This is a test document for testing purposes."
    assert "id" in data
    
# Example test for getting a document by ID
@pytest.mark.asyncio
async def test_get_document(async_client: AsyncClient):
    # First create a document
    create_response = await async_client.post(
        "/api/v1/documents",
        json={
            "title": "Get Test Document",
            "content": "This is a test document that we will try to retrieve."
        }
    )
    
    # Get the document ID from the response
    document_id = create_response.json()["id"]
    
    # Now get the document by ID
    response = await async_client.get(f"/api/v1/documents/{document_id}")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["id"] == document_id
    assert data["title"] == "Get Test Document"
