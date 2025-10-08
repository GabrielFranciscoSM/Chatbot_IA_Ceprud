"""
LTI JWT Validation and Security

Handles JWT signature verification, nonce validation, and security checks.
"""

import jwt
import requests
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

logger = logging.getLogger(__name__)


class LTIJWTValidator:
    """
    Validates LTI 1.3 JWT tokens from Moodle.
    """
    
    def __init__(self, platform_id: str, client_id: str, jwks_url: str):
        """
        Initialize JWT validator.
        
        Args:
            platform_id: Moodle platform ID (issuer)
            client_id: OAuth 2.0 client ID
            jwks_url: URL to fetch Moodle's public keys
        """
        self.platform_id = platform_id
        self.client_id = client_id
        self.jwks_url = jwks_url
        self._public_keys = None
        self._keys_fetched_at = None
        self._nonce_cache = set()  # Simple nonce cache (use Redis in production)
    
    def _fetch_public_keys(self) -> Dict:
        """
        Fetch Moodle's public keys from JWKS endpoint.
        
        Returns:
            JWKS dictionary with public keys
        """
        # Cache keys for 1 hour
        if self._public_keys and self._keys_fetched_at:
            age = datetime.utcnow() - self._keys_fetched_at
            if age < timedelta(hours=1):
                logger.debug("Using cached public keys")
                return self._public_keys
        
        try:
            logger.info(f"Fetching public keys from {self.jwks_url}")
            response = requests.get(self.jwks_url, timeout=10)
            response.raise_for_status()
            
            self._public_keys = response.json()
            self._keys_fetched_at = datetime.utcnow()
            
            logger.info(f"Fetched {len(self._public_keys.get('keys', []))} public keys")
            return self._public_keys
            
        except Exception as e:
            logger.error(f"Failed to fetch public keys: {e}")
            raise ValueError(f"Cannot fetch Moodle public keys: {e}")
    
    def _get_public_key(self, kid: str) -> str:
        """
        Get a specific public key by Key ID.
        
        Args:
            kid: Key ID from JWT header
            
        Returns:
            Public key in PEM format
        """
        jwks = self._fetch_public_keys()
        
        for key in jwks.get('keys', []):
            if key.get('kid') == kid:
                # Convert JWK to PEM
                return jwt.algorithms.RSAAlgorithm.from_jwk(key)
        
        raise ValueError(f"Public key with kid '{kid}' not found")
    
    def validate_jwt(self, token: str, validate_signature: bool = True) -> Dict:
        """
        Validate and decode LTI JWT token.
        
        Args:
            token: JWT token string
            validate_signature: Whether to verify JWT signature (disable for testing)
            
        Returns:
            Decoded JWT payload
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Decode header to get kid
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if validate_signature:
                # Get public key for this kid
                public_key = self._get_public_key(kid)
                
                # Verify and decode
                decoded = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    audience=self.client_id,
                    issuer=self.platform_id,
                    options={
                        'verify_signature': True,
                        'verify_aud': True,
                        'verify_iss': True,
                        'verify_exp': True,
                        'require': ['iss', 'aud', 'sub', 'exp', 'iat', 'nonce']
                    }
                )
            else:
                # For testing: decode without verification
                logger.warning("JWT signature verification is DISABLED - for testing only!")
                decoded = jwt.decode(
                    token,
                    options={'verify_signature': False, 'verify_aud': False}
                )
            
            # Validate message type
            message_type = decoded.get('https://purl.imsglobal.org/spec/lti/claim/message_type')
            if message_type != 'LtiResourceLinkRequest':
                raise ValueError(f"Invalid message type: {message_type}")
            
            # Validate LTI version
            version = decoded.get('https://purl.imsglobal.org/spec/lti/claim/version')
            if version != '1.3.0':
                raise ValueError(f"Unsupported LTI version: {version}")
            
            # Validate nonce (prevent replay attacks)
            nonce = decoded.get('nonce')
            if validate_signature and nonce:
                if nonce in self._nonce_cache:
                    raise ValueError(f"Nonce already used (replay attack?)")
                self._nonce_cache.add(nonce)
                # TODO: Implement proper nonce expiration (use Redis with TTL)
            
            logger.info(f"JWT validated successfully for user {decoded.get('sub')}")
            return decoded
            
        except jwt.ExpiredSignatureError:
            raise ValueError("JWT token has expired")
        except jwt.InvalidAudienceError:
            raise ValueError(f"Invalid audience. Expected: {self.client_id}")
        except jwt.InvalidIssuerError:
            raise ValueError(f"Invalid issuer. Expected: {self.platform_id}")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid JWT token: {e}")
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            raise ValueError(f"JWT validation failed: {e}")
    
    def extract_user_info(self, decoded_jwt: Dict) -> Dict:
        """
        Extract user information from decoded JWT.
        
        Args:
            decoded_jwt: Decoded JWT payload
            
        Returns:
            Dictionary with user info
        """
        return {
            'lti_user_id': decoded_jwt.get('sub'),
            'email': decoded_jwt.get('email'),
            'name': decoded_jwt.get('name') or decoded_jwt.get('given_name', '') + ' ' + decoded_jwt.get('family_name', ''),
            'roles': decoded_jwt.get('https://purl.imsglobal.org/spec/lti/claim/roles', []),
            'platform_id': decoded_jwt.get('iss'),
        }
    
    def extract_context_info(self, decoded_jwt: Dict) -> Dict:
        """
        Extract course/context information from decoded JWT.
        
        Args:
            decoded_jwt: Decoded JWT payload
            
        Returns:
            Dictionary with context info
        """
        context = decoded_jwt.get('https://purl.imsglobal.org/spec/lti/claim/context', {})
        resource_link = decoded_jwt.get('https://purl.imsglobal.org/spec/lti/claim/resource_link', {})
        
        return {
            'context_id': context.get('id'),
            'context_label': context.get('label'),
            'context_title': context.get('title'),
            'context_type': context.get('type', []),
            'resource_link_id': resource_link.get('id'),
            'resource_link_title': resource_link.get('title'),
        }
    
    def get_deployment_id(self, decoded_jwt: Dict) -> str:
        """
        Extract deployment ID from JWT.
        
        Args:
            decoded_jwt: Decoded JWT payload
            
        Returns:
            Deployment ID
        """
        return decoded_jwt.get('https://purl.imsglobal.org/spec/lti/claim/deployment_id', '1')
