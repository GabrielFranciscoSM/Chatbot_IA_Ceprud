# Phase 1: Infrastructure Setup - Summary

## ✅ What We've Created

### 1. **Dependencies** (`requirements.txt`)
Added the following LTI 1.3 packages:
- `PyLTI1p3==3.6.0` - Main LTI 1.3 library
- `PyJWT==2.10.1` - JWT token handling
- `cryptography==44.0.0` - Cryptographic operations
- `jwcrypto==1.6.0` - JWKS generation

### 2. **LTI Module** (`app/lti/`)
Created a new LTI module with:

#### `app/lti/models.py`
- `LTIPlatformConfig` - Stores Moodle platform configuration (URLs, keys, client IDs)
- `LTISession` - Tracks LTI launch sessions and maps Moodle users/courses to chatbot
- `LTILaunchRequest` - Request model for LTI launches
- `LTILaunchResponse` - Response model after successful launch

#### `app/lti/config.py`
- `LTIConfig` - Manages RSA key generation and JWKS creation
- Automatic key pair generation (2048-bit RSA)
- JWKS export for Moodle registration
- Tool configuration generator

### 3. **Configuration** (`moodle/.env`)
Environment variables for:
- Moodle platform details (URLs, client ID)
- Deployment configuration
- Subject mapping (Moodle courses → Chatbot subjects)

### 4. **Setup Script** (`setup_lti.sh`)
Automated installation script that:
- Installs Python dependencies
- Generates RSA key pair
- Creates JWKS
- Displays configuration URLs

### 5. **Documentation** (`moodle/README.md`)
Complete guide covering:
- Quick start instructions
- Moodle registration steps
- Configuration options
- Security considerations
- Troubleshooting guide

## 📁 File Structure

```
Chatbot_IA_Ceprud/
├── requirements.txt (updated)
├── setup_lti.sh (new)
├── app/
│   └── lti/
│       ├── __init__.py
│       ├── models.py
│       └── config.py
├── moodle/
│   ├── .env (updated)
│   └── README.md (new)
└── lti_config/ (will be created on setup)
    ├── private_key.pem
    ├── public_key.pem
    └── jwks.json
```

## 🔑 Key Concepts

### LTI 1.3 Flow
1. **OIDC Login** - Initial authentication request from Moodle
2. **Launch** - Main launch with JWT containing user/course data
3. **Session** - Create chatbot session linked to Moodle user
4. **Mapping** - Map Moodle course to chatbot subject

### Security
- RSA 2048-bit key pair for JWT signing
- JWT signature verification
- Nonce validation to prevent replay attacks
- Platform allowlist (only configured Moodle instances)

### Data Models
- **Platform Config** - Stored in MongoDB, one per Moodle instance
- **LTI Session** - Links Moodle launch to chatbot session
- **User Mapping** - LTI user ID → Chatbot user ID

## 🎯 Next Steps (Phase 2)

Once you approve, we'll create:
1. LTI endpoint routes (`/lti/login`, `/lti/launch`, `/lti/jwks`)
2. JWT validation logic
3. User authentication from LTI claims
4. Course-to-subject mapping logic
5. Session management for LTI users

## ⚠️ Notes

- The imports will show errors until dependencies are installed
- Keys will be generated when you run `setup_lti.sh`
- `.env` file contains example values - update with your Moodle details
- Private keys should be kept secret and excluded from git

---

**Ready for Phase 2?** Let me know if you want to:
1. Proceed to implementing the LTI endpoints
2. Make changes to Phase 1
3. Test the current setup first
