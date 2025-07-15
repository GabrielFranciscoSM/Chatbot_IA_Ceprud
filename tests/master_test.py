# test_vllm_endpoints.py

import unittest
import os
import json
import time
import csv
import requests
from vLLM_test import (
    call_completions,
    call_chat_completions,
    call_streaming_completions,
    call_embeddings
)

BASE_URL = "http://localhost:5001"

class TestVllmEndpoints(unittest.TestCase):

    def test_completions_endpoint(self):
        """
        Tests the /completions endpoint for a successful response and valid content.
        """
        print("\n--- Running test for /completions ---")
        response = call_completions("Escribe un slogan para una cafetería.")
        
        # Assert that the request was successful
        self.assertIsNotNone(response, "Request to /completions failed.")
        self.assertEqual(response.status_code, 200, "Response status code is not 200 OK.")
        
        # Parse the JSON and check its structure
        data = response.json()
        self.assertIn("id", data, "Response JSON is missing 'id'.")
        self.assertIn("choices", data, "Response JSON is missing 'choices'.")
        self.assertGreater(len(data["choices"]), 0, "'choices' array should not be empty.")
        self.assertIn("text", data["choices"][0], "Choice object is missing 'text'.")
        print("✓ Test for /completions passed.")

    def test_chat_completions_endpoint(self):
        """
        Tests the /chat/completions endpoint for a successful response and valid content.
        """
        print("\n--- Running test for /chat/completions ---")
        response = call_chat_completions("¿Cuál es la fórmula química del agua?")
        
        # Assert that the request was successful
        self.assertIsNotNone(response, "Request to /chat/completions failed.")
        self.assertEqual(response.status_code, 200, "Response status code is not 200 OK.")
        
        # Parse the JSON and check its structure
        data = response.json()
        self.assertIn("id", data, "Response JSON is missing 'id'.")
        self.assertIn("choices", data, "Response JSON is missing 'choices'.")
        self.assertGreater(len(data["choices"]), 0, "'choices' array should not be empty.")
        self.assertIn("message", data["choices"][0], "Choice object is missing 'message'.")
        self.assertIn("role", data["choices"][0]["message"], "Message object is missing 'role'.")
        self.assertEqual(data["choices"][0]["message"]["role"], "assistant")
        print("✓ Test for /chat/completions passed.")

    def test_streaming_completions_endpoint(self):
        """
        Tests the /completions endpoint with streaming for a successful response and valid content chunks.
        """
        print("\n--- Running test for streaming /completions ---")
        response = call_streaming_completions("Cuéntame un chiste sobre programadores.")
        
        # Assert that the initial HTTP request was successful
        self.assertIsNotNone(response, "Request to streaming /completions failed.")
        self.assertEqual(response.status_code, 200, "Response status code is not 200 OK.")
        
        received_chunk = False
        # Iterate over the streaming response
        for chunk in response.iter_lines():
            if chunk:
                received_chunk = True
                # Slices off the 'data: ' prefix
                decoded_chunk = chunk.decode('utf-8')
                self.assertTrue(decoded_chunk.startswith('data: '), f"Chunk does not start with 'data: ': {decoded_chunk}")
                
                json_data_str = decoded_chunk[6:]
                
                # The stream ends with a '[DONE]' message
                if json_data_str.strip() == '[DONE]':
                    break
                    
                # Assert that the chunk is valid JSON
                try:
                    chunk_json = json.loads(json_data_str)
                    self.assertIn("id", chunk_json)
                    self.assertIn("choices", chunk_json)
                    self.assertIsInstance(chunk_json["choices"], list)
                except json.JSONDecodeError:
                    self.fail(f"Failed to decode JSON from stream chunk: {json_data_str}")

        # Ensure that we actually received at least one data chunk
        self.assertTrue(received_chunk, "Did not receive any data chunks from the streaming endpoint.")
        print("✓ Test for streaming /completions passed.")

    def test_embeddings_endpoint(self):
        """
        Tests the /embeddings endpoint for a successful response and valid content.
        """
        print("\n--- Running test for /embeddings ---")
        response = call_embeddings("Hola Mundo")
        
        # Assert that the request was successful
        self.assertIsNotNone(response, "Request to /embeddings failed.")
        self.assertEqual(response.status_code, 200, "Response status code is not 200 OK.")
        
        # Parse the JSON and check its structure
        data = response.json()
        self.assertIn("object", data, "Response JSON is missing 'object'.")
        self.assertEqual(data["object"], "list", "'object' should be 'list'.")
        self.assertIn("data", data, "Response JSON is missing 'data'.")
        self.assertGreater(len(data["data"]), 0, "'data' array should not be empty.")
        
        embedding_data = data["data"][0]
        self.assertIn("object", embedding_data, "Embedding data is missing 'object'.")
        self.assertEqual(embedding_data["object"], "embedding", "'object' in data should be 'embedding'.")
        self.assertIn("embedding", embedding_data, "Embedding data is missing 'embedding' vector.")
        self.assertIsInstance(embedding_data["embedding"], list, "Embedding should be a list.")
        self.assertGreater(len(embedding_data["embedding"]), 0, "Embedding vector should not be empty.")
        print("✓ Test for /embeddings passed.")
    

    #API TESTS

    @classmethod
    def setUpClass(cls):
        """
        Set up the environment for the tests.
        This method is called once before any tests in the class run.
        """
        print("--- Setting up test environment ---")
        # Create mock directories and files ON THE HOST, which will be mounted into the container.
        os.makedirs("../app/RAG/chroma/test_subject", exist_ok=True)
        os.makedirs("../graphs", exist_ok=True)
        os.makedirs("../logs", exist_ok=True)
        
        # Create a dummy graph file for the graph endpoint test
        with open("../graphs/test_graph.png", "w") as f:
            f.write("dummy graph content")

    @classmethod
    def tearDownClass(cls):
        """
        Clean up created files after all tests are complete.
        """
        print("\n--- Tearing down test environment ---")
        if os.path.exists("../graphs/test_graph.png"):
            os.remove("../graphs/test_graph.png")
        if os.path.exists("../logs/chat_logs.csv"):
            os.remove("../logs/chat_logs.csv")

    def test_01_service_is_alive(self):
        """
        Test if the service is reachable. This is a basic health check.
        """
        print("\n--- Running test: Service health check ---")
        try:
            # We test an endpoint that doesn't exist to confirm the server is running
            response = requests.get(f"{BASE_URL}/")
            # A 404 is expected and means the server is up and routing requests
            self.assertEqual(response.status_code, 404)
            print("✓ Service is running.")
        except requests.ConnectionError as e:
            self.fail(f"Service is not running. Could not connect to {BASE_URL}. Error: {e}")

    def test_02_chat_endpoint_base_mode(self):
        """
        Test a successful interaction with the /chat endpoint in 'base' mode.
        This will make a real call to the vLLM container.
        """
        print("\n--- Running test: /chat endpoint (base mode) ---")
        response = requests.post(
            f"{BASE_URL}/chat",
            data={
                "message": "What is 2+2?",
                "email": "test@example.com",
                "mode": "base"
            }
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("response", data)
        print("✓ Test for /chat endpoint (base mode) passed.")
    
    def test_03_chat_with_invalid_mode(self):
        """
        Test the /chat endpoint with an unsupported mode.
        """
        print("\n--- Running test: Invalid mode ---")
        response = requests.post(
            f"{BASE_URL}/chat",
            data={"message": "Hello", "mode": "invalid_mode"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Modo no válido", response.json()["response"])
        print("✓ Test for invalid mode passed.")

    def test_04_chat_with_empty_message(self):
        """
        Test the /chat endpoint with an empty message.
        """
        print("\n--- Running test: Empty message ---")
        response = requests.post(
            f"{BASE_URL}/chat",
            data={"message": " ", "mode": "rag"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Por favor, escribe una pregunta", response.json()["response"])
        print("✓ Test for empty message passed.")

    def test_05_chat_rag_mode_with_nonexistent_subject(self):
        """
        Test the /chat endpoint in 'rag' mode with a subject that has no data.
        """
        print("\n--- Running test: RAG with nonexistent subject ---")
        response = requests.post(
            f"{BASE_URL}/chat",
            data={
                "message": "Inquiry",
                "subject": "nonexistent_subject",
                "mode": "rag"
            }
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("No hay datos disponibles", response.json()["response"])
        print("✓ Test for RAG with nonexistent subject passed.")
        
    def test_06_logging_is_created(self):
        """
        Test that user messages are correctly logged by checking the log file.
        """
        print("\n--- Running test: Message logging ---")
        log_file = "../logs/chat_logs.csv"
        
        # Ensure log file is clean before this test
        if os.path.exists(log_file):
            os.remove(log_file)

        # Make a request that should be logged
        requests.post(
            f"{BASE_URL}/chat",
            data={
                "message": "Log this message",
                "subject": "logging_test",
                "email": "log@test.com",
                "mode": "base"
            }
        )
        
        # Check that the log file was created and has the correct content
        self.assertTrue(os.path.exists(log_file), "Log file was not created.")
        
        with open(log_file, mode='r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, ["user", "message", "time", "date", "subject", "sources"])
            log_entry = next(reader)
            self.assertEqual(log_entry[0], "log@test.com")
            self.assertEqual(log_entry[1], "Log this message")
            self.assertEqual(log_entry[4], "logging_test")

        print("✓ Test for message logging passed.")

    def test_07_serve_graph_success(self):
        """
        Test successfully serving a graph file.
        """
        print("\n--- Running test: Serving graphs (success) ---")
        response = requests.get(f"{BASE_URL}/graphs/test_graph.png")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "dummy graph content")
        print("✓ Test for serving graphs (success) passed.")

    def test_08_serve_graph_not_found(self):
        """
        Test serving a graph file that does not exist.
        """
        print("\n--- Running test: Serving graphs (not found) ---")
        response = requests.get(f"{BASE_URL}/graphs/nonexistent.png")
        self.assertEqual(response.status_code, 404)
        print("✓ Test for serving graphs (not found) passed.")

if __name__ == '__main__':
    unittest.main()