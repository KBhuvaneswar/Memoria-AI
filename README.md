# AI ENGINE

### Configure Environment Variables:
    -   Add your secret keys to this file (.env)
        ```
        PINECONE_API_KEY="YOUR_PINECONE_KEY"
        PINECONE_INDEX ="YOUR_PINECONE_INDEX"
        GROQ_API_KEY="YOUR_GROQ_KEY"
        ```

### Running the Service

1.  **Start the API Server:**
    ```bash
    uvicorn app.main:app --reload
    ```
    The server will be running at `http://127.0.0.1:8000`.

2.  **Access the Interactive Docs:**
    -   Open your browser and go to `http://127.0.0.1:8000/docs`.
    -   You can use this interface to test the API endpoints directly.


## API Endpoints

The following endpoints are available under the `/api/v1` prefix.


### Ingestion

-   **`POST /api/v1/ingest`**
    -   Receives a PDF file, user_id, and product_id for processing. This request must be sent as multipart/form-data.

    -   **Request Body (Form Fields):**

        "user_id": (string) The ID of the user.
        "product_id": (string) The ID of the product.
        "file": (file) The PDF document.


### Querying

-   **`POST /api/v1/query`**
    -   Receives a user's question and returns a generated answer.
    -   **Request Body:**
        ```json
        {
          "query": "What is the warranty policy?",
          "user_id": "user_abc_123",
          "product_id": "product_abc_123"
        }
        ```
    -   **Response Body:**
        ```json
        {
          "answer": "The product comes with a 2-year limited warranty."
        }
        ```