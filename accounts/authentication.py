import json
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from jose import jwt, JWTError
from django.core.cache import cache

User = get_user_model()

def get_client_ip(request):
    """
    Get the client's IP address from the request
    Priority: X-Client-IP header (from frontend) > X-Forwarded-For > REMOTE_ADDR
    """
    # Check if frontend sent IP in custom header
    client_ip_header = request.META.get('HTTP_X_CLIENT_IP')
    if client_ip_header:
        return client_ip_header.strip()
    
    # Fallback to server-detected IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
        return ip.strip()
    else:
        ip = request.META.get('REMOTE_ADDR')
        return ip

def is_owner_ip(ip_address):
    """
    Check if the IP address belongs to the owner
    Add your IP address here
    """
    # Replace with your actual IP address
    OWNER_IP_ADDRESSES = [
        '127.0.0.1',        # localhost for development
        '::1',              # localhost IPv6
        '127.0.1.1',        # your local IP
        '103.24.86.216',    # your public IP
        # Add more IP addresses as needed
    ]
    
    return ip_address in OWNER_IP_ADDRESSES


class Auth0Authentication(BaseAuthentication):
    """
    Custom authentication class for Auth0 JWT tokens
    """
    
    def authenticate(self, request):
        """
        Main authentication method called by Django REST Framework
        """
        # Extract token from Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        
        if not auth_header:
            return None
        
        try:
            # Expected format: "Bearer <token>"
            auth_type, token = auth_header.split(' ', 1)
            if auth_type.lower() != 'bearer':
                return None
        except ValueError:
            return None
        
        if not token:
            return None
        
        try:
            # Validate the token
            payload = self.validate_token(token)
            
            # Get or create user from token payload
            user = self.get_or_create_user(payload, request)
            
            return (user, token)
            
        except AuthenticationFailed:
            raise
        except Exception as e:
            raise AuthenticationFailed(f'Authentication failed: {str(e)}')
    
    def get_jwks(self):
        """
        Fetch Auth0's public keys for token validation
        """
        # Check cache first
        jwks = cache.get('auth0_jwks')
        if jwks:
            return jwks
        
        try:
            jwks_url = settings.JWT_SETTINGS['JWKS_URL']
            response = requests.get(jwks_url, timeout=10)
            response.raise_for_status()
            jwks = response.json()
            
            # Cache for 1 hour
            cache.set('auth0_jwks', jwks, 3600)
            return jwks
            
        except requests.RequestException as e:
            raise AuthenticationFailed(f'Unable to fetch JWKS: {str(e)}')
    
    def validate_token(self, token):
        """
        Validate JWT token signature and claims
        """
        try:
            # Get the key ID from token header
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get('kid')
            
            if not kid:
                raise AuthenticationFailed('Token header missing key ID')
            
            # Get JWKS
            jwks = self.get_jwks()
            
            # Find the correct key
            rsa_key = None
            for key in jwks['keys']:
                if key['kid'] == kid:
                    rsa_key = {
                        'kty': key['kty'],
                        'kid': key['kid'],
                        'use': key['use'],
                        'n': key['n'],
                        'e': key['e']
                    }
                    break
            
            if not rsa_key:
                raise AuthenticationFailed('Unable to find appropriate key')
            
            # Validate token
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=[settings.JWT_SETTINGS['ALGORITHM']],
                audience=settings.JWT_SETTINGS['AUDIENCE'],
                issuer=settings.JWT_SETTINGS['ISSUER']
            )
            
            return payload
            
        except JWTError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            raise AuthenticationFailed(f'Token validation failed: {str(e)}')
    
    def get_or_create_user(self, payload, request):
        """
        Create or update user from JWT token payload with IP-based role assignment
        """
        try:
            # Extract user information from JWT payload
            auth0_id = payload.get('sub')
            
            # Try both namespaced and regular claims
            namespace = 'https://anitamaxwynn.com/'
            email = payload.get(f'{namespace}email') or payload.get('email')
            name = payload.get(f'{namespace}name') or payload.get('name', '')
            picture = payload.get(f'{namespace}picture') or payload.get('picture', '')
            
            if not auth0_id:
                raise AuthenticationFailed('Token missing user identifier')
            
            if not email:
                raise AuthenticationFailed('Token missing email - check Auth0 configuration')
            
            # Get client IP and determine role
            client_ip = get_client_ip(request)
            role = 'owner' if is_owner_ip(client_ip) else 'customer'
            
            # Try to get existing user by auth0_id first
            try:
                user = User.objects.get(auth0_id=auth0_id)
                
                # Update user information if it has changed
                updated = False
                if user.email != email:
                    user.email = email
                    updated = True
                if user.name != name:
                    user.name = name
                    updated = True
                if user.profile_picture != picture:
                    user.profile_picture = picture
                    updated = True
                # NOTE: Role is NOT updated for existing users
                # Role is set only once during user creation
                
                if updated:
                    user.save()
                
                return user
                
            except User.DoesNotExist:
                # Try to find by email (in case auth0_id changed)
                try:
                    user = User.objects.get(email=email)
                    # Update the auth0_id and role
                    user.auth0_id = auth0_id
                    user.name = name
                    user.profile_picture = picture
                    user.role = role  # Set role based on IP
                    user.save()
                    return user
                    
                except User.DoesNotExist:
                    # Create new user with IP-based role
                    user = User.objects.create(
                        auth0_id=auth0_id,
                        email=email,
                        name=name,
                        profile_picture=picture,
                        role=role,  # Set role based on IP
                        is_active=True,
                    )
                    return user
                    
        except Exception as e:
            raise AuthenticationFailed(f'User creation failed: {str(e)}')
    
    def authenticate_header(self, request):
        """
        Return the authentication header that should be used for unauthenticated responses
        """
        return 'Bearer'
