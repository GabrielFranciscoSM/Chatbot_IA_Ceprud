"""
LTI Configuration Management

Handles LTI configuration, key generation, and platform setup.
"""

import os
import json
from typing import Optional, Dict
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from jwcrypto import jwk
import logging

logger = logging.getLogger(__name__)


class LTIConfig:
    """
    Manages LTI configuration and cryptographic keys.
    """
    
    def __init__(self, config_dir: str = "./lti_config"):
        """
        Initialize LTI configuration manager.
        
        Args:
            config_dir: Directory to store LTI configuration and keys
        """
        self.config_dir = config_dir
        self.private_key_path = os.path.join(config_dir, "private_key.pem")
        self.public_key_path = os.path.join(config_dir, "public_key.pem")
        self.jwks_path = os.path.join(config_dir, "jwks.json")
        self.kid = "lti-key-1"  # Key ID for JWT signing
        
        # Ensure config directory exists
        os.makedirs(config_dir, exist_ok=True)
        
        # Load or generate keys
        self._ensure_keys_exist()
    
    def _ensure_keys_exist(self):
        """Generate RSA key pair if they don't exist."""
        if not os.path.exists(self.private_key_path):
            logger.info("Generating new RSA key pair for LTI...")
            self._generate_rsa_keypair()
        else:
            logger.info("Using existing RSA key pair for LTI")
    
    def _generate_rsa_keypair(self):
        """Generate a new RSA key pair for LTI signing."""
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048,
            backend=default_backend()
        )
        
        # Save private key
        pem_private = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        with open(self.private_key_path, 'wb') as f:
            f.write(pem_private)
        logger.info(f"Private key saved to {self.private_key_path}")
        
        # Save public key
        public_key = private_key.public_key()
        pem_public = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        with open(self.public_key_path, 'wb') as f:
            f.write(pem_public)
        logger.info(f"Public key saved to {self.public_key_path}")
        
        # Generate JWKS
        self._generate_jwks(pem_private)
    
    def _generate_jwks(self, private_key_pem: bytes):
        """
        Generate JWKS (JSON Web Key Set) from private key.
        
        Args:
            private_key_pem: Private key in PEM format
        """
        # Create JWK from PEM
        key = jwk.JWK.from_pem(private_key_pem)
        
        # Export public key as JWK
        public_jwk = json.loads(key.export_public())
        
        # Add key ID and algorithm
        public_jwk['kid'] = 'lti-key-1'
        public_jwk['alg'] = 'RS256'
        public_jwk['use'] = 'sig'
        
        # Create JWKS structure
        jwks = {
            "keys": [public_jwk]
        }
        
        # Save JWKS
        with open(self.jwks_path, 'w') as f:
            json.dump(jwks, f, indent=2)
        logger.info(f"JWKS saved to {self.jwks_path}")
    
    def get_private_key(self) -> str:
        """
        Get the private key in PEM format.
        
        Returns:
            Private key as string
        """
        with open(self.private_key_path, 'r') as f:
            return f.read()
    
    def get_public_key(self) -> str:
        """
        Get the public key in PEM format.
        
        Returns:
            Public key as string
        """
        with open(self.public_key_path, 'r') as f:
            return f.read()
    
    def get_jwks(self) -> Dict:
        """
        Get the JWKS (JSON Web Key Set).
        
        Returns:
            JWKS as dictionary
        """
        with open(self.jwks_path, 'r') as f:
            return json.load(f)
    
    def get_tool_config(self, base_url: str) -> Dict:
        """
        Generate LTI tool configuration for Moodle registration.
        
        Args:
            base_url: Base URL of the chatbot application (e.g., https://chatbot.ugr.es)
        
        Returns:
            Tool configuration dictionary
        """
        return {
            "title": "CEPRUD AI Chatbot",
            "description": "AI-powered educational chatbot with RAG capabilities",
            "oidc_initiation_url": f"{base_url}/lti/login",
            "target_link_uri": f"{base_url}/lti/launch",
            "public_jwk_url": f"{base_url}/lti/jwks",
            "custom_fields": {
                "subject": "$Context.label",  # Map course short name to subject
                "user_email": "$Person.email.primary",
                "user_name": "$Person.name.full"
            },
            "scopes": [
                "https://purl.imsglobal.org/spec/lti-ags/scope/lineitem",
                "https://purl.imsglobal.org/spec/lti-ags/scope/result.readonly",
                "https://purl.imsglobal.org/spec/lti-nrps/scope/contextmembership.readonly"
            ]
        }
