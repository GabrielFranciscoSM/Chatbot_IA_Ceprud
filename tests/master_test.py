# test_vllm_endpoints.py

import unittest
import json
from vLLM_test import (
    call_completions,
    call_chat_completions,
    call_streaming_completions,
    call_embeddings
)

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

if __name__ == '__main__':
    unittest.main()