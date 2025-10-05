# LTI 1.3 Moodle Integration

This directory contains the configuration for integrating the CEPRUD AI Chatbot with Moodle using LTI 1.3 (Learning Tools Interoperability).

## 📋 Overview

The LTI 1.3 integration allows your chatbot to be embedded directly into Moodle courses as an external tool. Students and teachers can access the chatbot without leaving Moodle, with automatic user authentication and course-to-subject mapping.

## 🏗️ Architecture

```
Moodle Course → LTI Launch → Chatbot App
                              ↓
                    User Auto-Created/Logged In
                              ↓
                    Course Mapped to Subject
                              ↓
                    Chat Interface Displayed
```

## 🚀 Quick Start

### Step 1: Install Dependencies

Run the setup script from the project root:

```bash
chmod +x setup_lti.sh
./setup_lti.sh
```

This will:
- Install required Python packages
- Generate RSA key pair for JWT signing
- Create JWKS (JSON Web Key Set) for Moodle

### Step 2: Configure Environment

Edit `moodle/.env` with your Moodle instance details:

```bash
# Your Moodle instance URL
MOODLE_PLATFORM_ID="https://moodle.ugr.es"

# Client ID provided by Moodle when registering the tool
MOODLE_CLIENT_ID="your_client_id_here"

# Moodle LTI endpoints (usually the same pattern)
MOODLE_AUTH_LOGIN_URL="https://moodle.ugr.es/mod/lti/auth.php"
MOODLE_AUTH_TOKEN_URL="https://moodle.ugr.es/mod/lti/token.php"
MOODLE_KEY_SET_URL="https://moodle.ugr.es/mod/lti/certs.php"

# Your chatbot's public URL
CHATBOT_BASE_URL="https://chatbot.ugr.es"
```

### Step 3: Register Tool in Moodle

1. **Go to Moodle Site Administration**
   - Navigate to: `Plugins > Activity modules > External tool > Manage tools`

2. **Configure External Tool**
   - Click "Configure a tool manually"
   - Enter the following information:

   | Field | Value |
   |-------|-------|
   | Tool name | CEPRUD AI Chatbot |
   | Tool URL | `https://chatbot.ugr.es/lti/launch` |
   | LTI version | LTI 1.3 |
   | Public keyset URL | `https://chatbot.ugr.es/lti/jwks` |
   | Initiate login URL | `https://chatbot.ugr.es/lti/login` |
   | Redirection URI(s) | `https://chatbot.ugr.es/lti/launch` |

3. **Copy the Client ID**
   - Moodle will generate a Client ID
   - Add it to your `moodle/.env` file

4. **Configure Tool Settings**
   - Set privacy settings (share name, email)
   - Enable in courses

### Step 4: Add to Course

1. Go to your Moodle course
2. Turn editing on
3. Add an activity → External tool
4. Select "CEPRUD AI Chatbot"
5. Configure activity name and settings
6. Save

## 🔧 Configuration

### Subject Mapping

By default, the chatbot maps Moodle course labels to subjects. Configure mappings in `moodle/.env`:

```bash
DEFAULT_SUBJECT_MAPPINGS='{
  "IS": "ingenieria_de_servidores",
  "MAC": "modelos_avanzados_computacion",
  "MH": "metaheuristicas"
}'
```

### Custom Parameters

You can pass custom parameters from Moodle to the chatbot:

- `$Context.label` - Course short name (used for subject mapping)
- `$Person.email.primary` - User email
- `$Person.name.full` - User full name

## 🔐 Security

### Keys and Certificates

- **Private Key**: `lti_config/private_key.pem` (Keep secret!)
- **Public Key**: `lti_config/public_key.pem` (Share with Moodle)
- **JWKS**: `lti_config/jwks.json` (Public via `/lti/jwks` endpoint)

⚠️ **Important**: Never commit your private key to version control!

### JWT Validation

All LTI launches are validated:
1. JWT signature verification using Moodle's public key
2. Audience and issuer validation
3. Expiration time checks
4. Nonce validation to prevent replay attacks

## 📡 API Endpoints

The LTI integration adds the following endpoints:

- **`GET /lti/jwks`** - Public keyset (JWKS)
- **`POST /lti/login`** - OIDC login initiation
- **`POST /lti/launch`** - LTI launch and resource display
- **`GET /lti/config`** - Tool configuration (for debugging)

## 🧪 Testing

### Test LTI Launch Locally

For development, you can test with ngrok:

```bash
# Start ngrok
ngrok http 8080

# Update CHATBOT_BASE_URL in .env with ngrok URL
CHATBOT_BASE_URL="https://your-subdomain.ngrok.io"

# Configure Moodle with ngrok URLs
```

### Debug Mode

Enable debug logging in `app.py`:

```python
logging.getLogger('app.lti').setLevel(logging.DEBUG)
```

## 🔍 Troubleshooting

### Issue: "Invalid JWT signature"

**Solution**: 
- Verify JWKS URL is accessible from Moodle
- Check that Moodle has the correct public key
- Ensure time synchronization between servers

### Issue: "Platform not configured"

**Solution**: 
- Check `moodle/.env` configuration
- Verify platform_id matches Moodle's issuer
- Ensure MongoDB is running (stores platform configs)

### Issue: "Subject not mapped"

**Solution**: 
- Update subject mappings in `moodle/.env`
- Check that `$Context.label` is passed correctly
- Set a default subject in configuration

## 📚 LTI 1.3 Specification

For more details on LTI 1.3, see:
- [IMS LTI 1.3 Core Specification](https://www.imsglobal.org/spec/lti/v1p3/)
- [LTI Advantage](https://www.imsglobal.org/lti-advantage-overview)
- [Moodle LTI Documentation](https://docs.moodle.org/en/LTI)

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review Moodle and chatbot logs
3. Verify all endpoints are accessible
4. Contact your system administrator
