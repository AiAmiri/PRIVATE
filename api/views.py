from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework import status as http_status
from rest_framework.permissions import IsAuthenticated, AllowAny, BasePermission
from django.contrib.auth import login, logout
from django.contrib.sessions.models import Session
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import api_view, permission_classes
from django.db import models


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    Read permissions are allowed to any authenticated user.
    """
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return request.session.get('is_authenticated', False)
        
        # Write permissions are only allowed to authenticated users
        return request.session.get('is_authenticated', False)
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any authenticated request
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Write permissions are only allowed to the owner of the object
        # Check if the authenticated user is the owner of the SarafProfile
        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')
        
        if user_type == 'saraf' and hasattr(obj, 'saraf_id'):
            return obj.saraf_id == user_id
        
        return False


from Core.models import (
    SarafProfile, Currency, Province, SupportedCurrency, 
    sendhawala, ReceiveHawala, 
    CustomerTransaction, SarafColleague, SarafLoan, CurrencyExchange,
    Message, MessageAttachment, CustomerAccount, CustomerBalance,
    normal_user_Profile, SarafPost
)
from django.core.exceptions import ValidationError as DjangoValidationError
from .serializers import (
    sendhawalaSerializer, 
    SarafProfileSerializer, 
    SarafProfileReadSerializer,
    SarafProfileLiteSerializer,
    SarafProfileLoginSerializer,
    SarafProfileDualLoginSerializer,
    NormalUserProfileSerializer,
    NormalUserProfileReadSerializer,
    CustomerAccountSerializer,
    CustomerAccountCreateSerializer,
    CustomerBalanceSerializer,
    CustomerTransactionSerializer,
    CustomerFinancialOperationSerializer,
    NormalUserProfileLoginSerializer,
    CurrencySerializer,
    ProvinceSerializer,
    BalanceOperationInputSerializer,
    SupportedCurrencySerializer,
    ReceiveHawalaSerializer,
    ReceiveHawalaCreateSerializer,
    MessageSerializer,
    MessageCreateSerializer,
    MessageAttachmentSerializer,
    ConversationSerializer,
    SarafColleagueSerializer, SarafColleagueCreateSerializer,
    SarafLoanSerializer, SarafLoanCreateSerializer,
    CurrencyExchangeSerializer, CurrencyExchangeCreateSerializer,
    SarafPostSerializer,
)


class sendhawalaAV(APIView):
    def get(self, request):
        """Get all sendhawala records for authenticated user"""
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        hawalas = sendhawala.objects.all().order_by('-created_at')
        serializer = sendhawalaSerializer(hawalas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# SarafPost Views
class SarafPostCreateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        """Create a new SarafPost (saraf must be authenticated via session)."""
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Authentication required (saraf). Please login first.'}, status=status.HTTP_401_UNAUTHORIZED)

        serializer = SarafPostSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            post = serializer.save()
            return Response(SarafPostSerializer(post).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FilteredsendhawalaAV(APIView):
    def get(self, request):
        """Get filtered sendhawala records"""
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get filter parameters
        status_param = request.query_params.get('status')
        sender_name = request.query_params.get('sender_name')
        receiver_name = request.query_params.get('receiver_name')
        hawala_number = request.query_params.get('hawala_number')
        
        # Start with all hawalas
        hawalas = sendhawala.objects.all()
        
        # Apply filters
        if status_param:
            # Validate status parameter
            valid_statuses = [choice[0] for choice in sendhawala.STATUS_CHOICES]
            if status_param not in valid_statuses:
                return Response({
                    'error': f'Invalid status. Valid options are: {", ".join(valid_statuses)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            hawalas = hawalas.filter(status=status_param)
        
        if sender_name:
            hawalas = hawalas.filter(sender_name__icontains=sender_name)
            
        if receiver_name:
            hawalas = hawalas.filter(receiver_name__icontains=receiver_name)
            
        if hawala_number:
            try:
                hawala_number = int(hawala_number)
                hawalas = hawalas.filter(hawala_number=hawala_number)
            except ValueError:
                return Response({
                    'error': 'hawala_number must be a valid integer'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        # Order by creation date (newest first)
        hawalas = hawalas.order_by('-created_at')
        
        serializer = sendhawalaSerializer(hawalas, many=True)
        return Response({
            'count': hawalas.count(),
            'results': serializer.data
        }, status=status.HTTP_200_OK)


class SarafProfileCreateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Create a new SarafProfile with secure password storage and photo uploads
        """
        # Handle both form data and file uploads
        data = request.data.copy()
        files = request.FILES
        
        # If saraf_logo is uploaded, add it to data
        if 'saraf_logo' in files:
            data['saraf_logo'] = files['saraf_logo']
        
        # If saraf_logo_wallpeper is uploaded, add it to data
        if 'saraf_logo_wallpeper' in files:
            data['saraf_logo_wallpeper'] = files['saraf_logo_wallpeper']
        
        # If licence_photo is uploaded, add it to data
        if 'licence_photo' in files:
            data['licence_photo'] = files['licence_photo']
        
        serializer = SarafProfileSerializer(data=data)
        if serializer.is_valid():
            saraf_profile = serializer.save()
            read_serializer = SarafProfileReadSerializer(saraf_profile)
            return Response({
                'message': 'SarafProfile created successfully',
                'data': read_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SarafProfileLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Login for SarafProfile with session creation
        """
        serializer = SarafProfileLoginSerializer(data=request.data)
        if serializer.is_valid():
            saraf_profile = serializer.validated_data['saraf_profile']
            
            # Create session for the user
            request.session['user_id'] = saraf_profile.saraf_id
            request.session['user_type'] = 'saraf'
            request.session['is_authenticated'] = True
            request.session.save()  # Ensure session is saved
            
            return Response({
                'message': 'Login successful',
                'saraf_id': saraf_profile.saraf_id,
                'name': saraf_profile.name,
                'session_id': request.session.session_key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SarafProfileDualLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Dual login for SarafProfile - requires both email and phone number
        """
        serializer = SarafProfileDualLoginSerializer(data=request.data)
        if serializer.is_valid():
            saraf_profile = serializer.validated_data['saraf_profile']
            
            # Create session for the user
            request.session['user_id'] = saraf_profile.saraf_id
            request.session['user_type'] = 'saraf'
            request.session['is_authenticated'] = True
            request.session.save()  # Ensure session is saved
            
            return Response({
                'message': 'Dual login successful',
                'saraf_id': saraf_profile.saraf_id,
                'name': saraf_profile.name,
                'session_id': request.session.session_key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SarafProfileDetailView(APIView):
    permission_classes = [IsOwnerOrReadOnly]
    
    def get_object(self, saraf_id):
        """Get the SarafProfile object"""
        try:
            return SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        except SarafProfile.DoesNotExist:
            return None
    
    def get(self, request, saraf_id):
        """
        Get SarafProfile details
        """
        saraf_profile = self.get_object(saraf_id)
        if not saraf_profile:
            return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        self.check_object_permissions(request, saraf_profile)
        
        serializer = SarafProfileReadSerializer(saraf_profile)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, saraf_id):
        """
        Delete SarafProfile with password validation
        Body: { "password": "..." }
        """
        saraf_profile = self.get_object(saraf_id)
        if not saraf_profile:
            return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check permissions
        self.check_object_permissions(request, saraf_profile)

        password = request.data.get('password')
        if not password:
            return Response({'error': 'Password is required to delete profile'}, status=status.HTTP_400_BAD_REQUEST)

        if not saraf_profile.check_password(password):
            return Response({'error': 'Invalid password'}, status=status.HTTP_400_BAD_REQUEST)

        saraf_profile.delete()
        return Response({'message': 'SarafProfile deleted successfully'}, status=status.HTTP_200_OK)


# Currency Views
class CurrencyListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get all active currencies, optionally filter by ?code=USD or ?symbol=$
        """
        code = request.query_params.get('code')
        symbol = request.query_params.get('symbol')
        currencies = Currency.get_active_currencies()
        if code:
            currencies = currencies.filter(code__iexact=code)
        if symbol:
            currencies = currencies.filter(symbol=symbol)
        serializer = CurrencySerializer(currencies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CurrencyDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, currency_id):
        """
        Get currency details
        """
        try:
            currency = Currency.objects.get(id=currency_id)
            serializer = CurrencySerializer(currency)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Currency.DoesNotExist:
            return Response({'error': 'Currency not found'}, status=status.HTTP_404_NOT_FOUND)


class ProvincesListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """
        Get all active provinces ordered by name
        """
        provinces = Province.objects.filter(is_active=True).order_by('name')
        serializer = ProvinceSerializer(provinces, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ProvinceDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, province_name):
        """
        Get single province by name (case-insensitive)
        """
        try:
            province = Province.objects.get(name__iexact=province_name, is_active=True)
        except Province.DoesNotExist:
            return Response({'error': 'Province not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = ProvinceSerializer(province)
        return Response(serializer.data, status=status.HTTP_200_OK)



class SarafProfileListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get all active SarafProfiles (lite fields only)
        """
        saraf_profiles = SarafProfile.objects.filter(is_active=True)
        serializer = SarafProfileLiteSerializer(saraf_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SarafSupportedCurrenciesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, saraf_id):
        """
        List supported currencies for a Saraf.
        Optional filter: ?is_active=true|false
        """
        try:
            saraf = SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        except SarafProfile.DoesNotExist:
            return Response({'error': 'SarafProfile not found'}, status=http_status.HTTP_404_NOT_FOUND)

        qs = SupportedCurrency.objects.filter(saraf=saraf)
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            if is_active.lower() in ('true', '1', 'yes'):
                qs = qs.filter(is_active=True)
            elif is_active.lower() in ('false', '0', 'no'):
                qs = qs.filter(is_active=False)
        serializer = SupportedCurrencySerializer(qs, many=True)
        return Response(serializer.data, status=http_status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def change_password(request, saraf_id):
    """
    Change password for SarafProfile
    """
    try:
        saraf_profile = SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        if not old_password or not new_password or not new_password_confirm:
            return Response({
                'error': 'old_password, new_password, and new_password_confirm are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not saraf_profile.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != new_password_confirm:
            return Response({'error': 'New passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            saraf_profile.set_password(new_password)
            return Response({
                'message': 'Password changed successfully',
                'saraf_id': saraf_profile.saraf_id
            }, status=status.HTTP_200_OK)
        except DjangoValidationError:
            return Response({
                'error': 'Password does not meet security requirements',
                'requirements': saraf_profile.get_password_requirements()
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    except SarafProfile.DoesNotExist:
        return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)



class SarafProfilePhotoUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def _update_photos(self, request, saraf_id):
        """
        Update photo fields for a SarafProfile.
        Accepts multipart/form-data with any of the following keys:
        - saraf_logo
        - saraf_logo_wallpeper
        - licence_photo

        To clear a field, send the key with an empty value ("", "null", or "None").
        """
        try:
            saraf = SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        except SarafProfile.DoesNotExist:
            return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES
        data = request.data

        updatable_fields = ['saraf_logo', 'saraf_logo_wallpeper', 'licence_photo']
        update_fields = []

        for field in updatable_fields:
            if field in files:
                setattr(saraf, field, files[field])
                update_fields.append(field)
            elif field in data:
                val = data.get(field)
                if val in ("", None, "null", "None"):
                    setattr(saraf, field, None)
                    update_fields.append(field)

        if not update_fields:
            return Response(
                {'error': 'Provide at least one of: saraf_logo, saraf_logo_wallpeper, licence_photo'},
                status=status.HTTP_400_BAD_REQUEST
            )

        saraf.save(update_fields=update_fields)

        read = SarafProfileReadSerializer(saraf)
        return Response({
            'message': 'Photos updated successfully',
            'updated_fields': update_fields,
            'data': read.data
        }, status=status.HTTP_200_OK)

    def put(self, request, saraf_id):
        return self._update_photos(request, saraf_id)

    def patch(self, request, saraf_id):
        return self._update_photos(request, saraf_id)

# Individual photo field update endpoints
class SarafLogoUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, saraf_id):
        return self._update_field(request, saraf_id)

    def patch(self, request, saraf_id):
        return self._update_field(request, saraf_id)

    def _update_field(self, request, saraf_id):
        try:
            saraf = SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        except SarafProfile.DoesNotExist:
            return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'saraf_logo' in request.FILES:
            saraf.saraf_logo = request.FILES['saraf_logo']
        elif 'saraf_logo' in request.data:
            val = request.data.get('saraf_logo')
            if val in ("", None, "null", "None"):
                saraf.saraf_logo = None
            else:
                return Response({'error': 'Provide saraf_logo as file or empty to clear'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'saraf_logo is required'}, status=status.HTTP_400_BAD_REQUEST)

        saraf.save(update_fields=['saraf_logo'])
        return Response({'message': 'saraf_logo updated', 'saraf_id': saraf.saraf_id}, status=status.HTTP_200_OK)


class SarafLogoWallpaperUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, saraf_id):
        return self._update_field(request, saraf_id)

    def patch(self, request, saraf_id):
        return self._update_field(request, saraf_id)

    def _update_field(self, request, saraf_id):
        try:
            saraf = SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        except SarafProfile.DoesNotExist:
            return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        key = 'saraf_logo_wallpeper'
        if key in request.FILES:
            setattr(saraf, key, request.FILES[key])
        elif key in request.data:
            val = request.data.get(key)
            if val in ("", None, "null", "None"):
                setattr(saraf, key, None)
            else:
                return Response({'error': f'Provide {key} as file or empty to clear'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': f'{key} is required'}, status=status.HTTP_400_BAD_REQUEST)

        saraf.save(update_fields=[key])
        return Response({'message': f'{key} updated', 'saraf_id': saraf.saraf_id}, status=status.HTTP_200_OK)


class LicencePhotoUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, saraf_id):
        return self._update_field(request, saraf_id)

    def patch(self, request, saraf_id):
        return self._update_field(request, saraf_id)

    def _update_field(self, request, saraf_id):
        try:
            saraf = SarafProfile.objects.get(saraf_id=saraf_id, is_active=True)
        except SarafProfile.DoesNotExist:
            return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        key = 'licence_photo'
        if key in request.FILES:
            setattr(saraf, key, request.FILES[key])
        elif key in request.data:
            val = request.data.get(key)
            if val in ("", None, "null", "None"):
                setattr(saraf, key, None)
            else:
                return Response({'error': f'Provide {key} as file or empty to clear'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': f'{key} is required'}, status=status.HTTP_400_BAD_REQUEST)

        saraf.save(update_fields=[key])
        return Response({'message': f'{key} updated', 'saraf_id': saraf.saraf_id}, status=status.HTTP_200_OK)

# Normal User Profile Views
class NormalUserProfileCreateView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Create a new NormalUserProfile with secure password storage
        """
        serializer = NormalUserProfileSerializer(data=request.data)
        if serializer.is_valid():
            normal_user_profile = serializer.save()
            read_serializer = NormalUserProfileReadSerializer(normal_user_profile)
            return Response({
                'message': 'NormalUserProfile created successfully',
                'data': read_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NormalUserProfileLoginView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Login for NormalUserProfile with session creation
        """
        serializer = NormalUserProfileLoginSerializer(data=request.data)
        if serializer.is_valid():
            normal_user_profile = serializer.validated_data['normal_user_profile']
            
            # Create session for the user
            request.session['user_id'] = normal_user_profile.normal_user_id
            request.session['user_type'] = 'normal_user'
            request.session['is_authenticated'] = True
            
            read_serializer = NormalUserProfileReadSerializer(normal_user_profile)
            return Response({
                'message': 'Login successful',
                'session_id': request.session.session_key,
                'data': read_serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NormalUserProfileDetailView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, normal_user_id):
        """
        Get NormalUserProfile details
        """
        try:
            normal_user_profile = normal_user_Profile.objects.get(normal_user_id=normal_user_id)
            serializer = NormalUserProfileReadSerializer(normal_user_profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except normal_user_Profile.DoesNotExist:
            return Response({'error': 'NormalUserProfile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, normal_user_id):
        """
        Update NormalUserProfile
        """
        try:
            normal_user_profile = normal_user_Profile.objects.get(normal_user_id=normal_user_id)
            
            serializer = NormalUserProfileSerializer(normal_user_profile, data=request.data, partial=True)
            if serializer.is_valid():
                updated_profile = serializer.save()
                read_serializer = NormalUserProfileReadSerializer(updated_profile)
                return Response({
                    'message': 'NormalUserProfile updated successfully',
                    'data': read_serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except normal_user_Profile.DoesNotExist:
            return Response({'error': 'NormalUserProfile not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, saraf_id):
        """
        Delete SarafProfile with password validation
        """
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            saraf_profile = SarafProfile.objects.get(saraf_id=saraf_id)
            password = request.data.get('password')
            
            if not password:
                return Response({'error': 'Password is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
            
            if not saraf_profile.check_password(password):
                return Response({'error': 'Invalid password'}, status=status.HTTP_401_UNAUTHORIZED)
            
            # Soft delete by setting is_active to False
            saraf_profile.is_active = False
            saraf_profile.save()
            
            return Response({'message': 'SarafProfile deleted successfully'}, status=status.HTTP_200_OK)
        except SarafProfile.DoesNotExist:
            return Response({'error': 'SarafProfile not found'}, status=status.HTTP_404_NOT_FOUND)


class NormalUserProfileListView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        """
        Get all NormalUserProfiles
        """
        normal_user_profiles = normal_user_Profile.objects.all()
        serializer = NormalUserProfileReadSerializer(normal_user_profiles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([AllowAny])
def normal_user_change_password(request, normal_user_id):
    """
    Change password for NormalUserProfile
    """
    try:
        normal_user_profile = normal_user_Profile.objects.get(normal_user_id=normal_user_id)
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        new_password_confirm = request.data.get('new_password_confirm')
        
        if not old_password or not new_password or not new_password_confirm:
            return Response({
                'error': 'old_password, new_password, and new_password_confirm are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not normal_user_profile.check_password(old_password):
            return Response({'error': 'Invalid old password'}, status=status.HTTP_400_BAD_REQUEST)
        
        if new_password != new_password_confirm:
            return Response({'error': 'New passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            normal_user_profile.set_password(new_password)
            return Response({
                'message': 'Password changed successfully',
                'normal_user_id': normal_user_profile.normal_user_id
            }, status=status.HTTP_200_OK)
        except DjangoValidationError:
            return Response({
                'error': 'Password does not meet security requirements',
                'requirements': normal_user_profile.get_password_requirements()
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    except normal_user_Profile.DoesNotExist:
        return Response({'error': 'NormalUserProfile not found'}, status=status.HTTP_404_NOT_FOUND)


# Normal User Profile Photo Update Views
class NormalUserProfilePhotoUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def _update_photos(self, request, normal_user_id):
        """
        Update photo fields for a NormalUserProfile.
        Accepts multipart/form-data with any of the following keys:
        - user_logo
        - user_wallpaper

        To clear a field, send the key with an empty value ("", "null", or "None").
        """
        try:
            normal_user = normal_user_Profile.objects.get(normal_user_id=normal_user_id)
        except normal_user_Profile.DoesNotExist:
            return Response({'error': 'NormalUserProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        files = request.FILES
        data = request.data

        updatable_fields = ['user_logo', 'user_wallpaper']
        update_fields = []

        for field in updatable_fields:
            if field in files:
                setattr(normal_user, field, files[field])
                update_fields.append(field)
            elif field in data:
                val = data.get(field)
                if val in ("", None, "null", "None"):
                    setattr(normal_user, field, None)
                    update_fields.append(field)

        if not update_fields:
            return Response(
                {'error': 'Provide at least one of: user_logo, user_wallpaper'},
                status=status.HTTP_400_BAD_REQUEST
            )

        normal_user.save(update_fields=update_fields)

        read = NormalUserProfileReadSerializer(normal_user)
        return Response({
            'message': 'Photos updated successfully',
            'updated_fields': update_fields,
            'data': read.data
        }, status=status.HTTP_200_OK)

    def put(self, request, normal_user_id):
        return self._update_photos(request, normal_user_id)

    def patch(self, request, normal_user_id):
        return self._update_photos(request, normal_user_id)


class NormalUserLogoUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, normal_user_id):
        return self._update_field(request, normal_user_id)

    def patch(self, request, normal_user_id):
        return self._update_field(request, normal_user_id)

    def _update_field(self, request, normal_user_id):
        try:
            normal_user = normal_user_Profile.objects.get(normal_user_id=normal_user_id)
        except normal_user_Profile.DoesNotExist:
            return Response({'error': 'NormalUserProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        if 'user_logo' in request.FILES:
            normal_user.user_logo = request.FILES['user_logo']
        elif 'user_logo' in request.data:
            val = request.data.get('user_logo')
            if val in ("", None, "null", "None"):
                normal_user.user_logo = None
            else:
                return Response({'error': 'Provide user_logo as file or empty to clear'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'user_logo is required'}, status=status.HTTP_400_BAD_REQUEST)

        normal_user.save(update_fields=['user_logo'])
        return Response({'message': 'user_logo updated', 'normal_user_id': normal_user.normal_user_id}, status=status.HTTP_200_OK)


class NormalUserWallpaperUpdateView(APIView):
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, normal_user_id):
        return self._update_field(request, normal_user_id)

    def patch(self, request, normal_user_id):
        return self._update_field(request, normal_user_id)

    def _update_field(self, request, normal_user_id):
        try:
            normal_user = normal_user_Profile.objects.get(normal_user_id=normal_user_id)
        except normal_user_Profile.DoesNotExist:
            return Response({'error': 'NormalUserProfile not found'}, status=status.HTTP_404_NOT_FOUND)

        key = 'user_wallpaper'
        if key in request.FILES:
            setattr(normal_user, key, request.FILES[key])
        elif key in request.data:
            val = request.data.get(key)
            if val in ("", None, "null", "None"):
                setattr(normal_user, key, None)
            else:
                return Response({'error': f'Provide {key} as file or empty to clear'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': f'{key} is required'}, status=status.HTTP_400_BAD_REQUEST)

        normal_user.save(update_fields=[key])
        return Response({'message': f'{key} updated', 'normal_user_id': normal_user.normal_user_id}, status=status.HTTP_200_OK)


# Logout View
class LogoutView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Logout user and clear session
        """
        if request.session.get('is_authenticated'):
            request.session.flush()  # Clear all session data
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'No active session found'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get(self, request):
        """
        Logout user and clear session (GET method for convenience)
        """
        if request.session.get('is_authenticated'):
            request.session.flush()  # Clear all session data
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'message': 'No active session found'
            }, status=status.HTTP_400_BAD_REQUEST)


# Messaging Views
class MessageSendView(APIView):
    """Send a message to another user"""
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        # Check session authentication
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = MessageCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Get sender information from session
            sender_type = request.session.get('user_type')
            sender_id = request.session.get('user_id')
            
            if not sender_type or not sender_id:
                return Response({
                    'error': 'Invalid session data'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Prepare message data
            message_data = {
                'content': serializer.validated_data.get('content', ''),
                'attachment_files': serializer.validated_data.get('attachment_files', [])
            }
            
            # Set sender
            if sender_type == 'saraf':
                message_data['sender_saraf'] = sender_id
            else:
                message_data['sender_normal_user'] = sender_id
            
            # Set receiver
            receiver_type = serializer.validated_data['receiver_type']
            receiver_id = serializer.validated_data['receiver_id']
            
            if receiver_type == 'saraf':
                message_data['receiver_saraf'] = receiver_id
            else:
                message_data['receiver_normal_user'] = receiver_id
            
            # Create message using MessageSerializer
            message_serializer = MessageSerializer(data=message_data, context={'request': request})
            if message_serializer.is_valid():
                message = message_serializer.save()
                return Response(MessageSerializer(message, context={'request': request}).data, 
                              status=status.HTTP_201_CREATED)
            else:
                return Response(message_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class MessageListView(APIView):
    """List messages between authenticated user and another user"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Check session authentication
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        sender_type = request.session.get('user_type')
        sender_id = request.session.get('user_id')
        
        # Get query parameters
        other_user_type = request.query_params.get('user_type')
        other_user_id = request.query_params.get('user_id')
        
        if not other_user_type or not other_user_id:
            return Response({
                'error': 'user_type and user_id query parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Build filter for messages between these two users
        from django.db.models import Q
        
        if sender_type == 'saraf':
            if other_user_type == 'saraf':
                messages = Message.objects.filter(
                    Q(sender_saraf=sender_id, receiver_saraf=other_user_id) |
                    Q(sender_saraf=other_user_id, receiver_saraf=sender_id)
                ).filter(
                    Q(is_deleted_by_sender=False) | Q(is_deleted_by_receiver=False)
                )
            else:
                messages = Message.objects.filter(
                    Q(sender_saraf=sender_id, receiver_normal_user=other_user_id) |
                    Q(sender_normal_user=other_user_id, receiver_saraf=sender_id)
                ).filter(
                    Q(is_deleted_by_sender=False) | Q(is_deleted_by_receiver=False)
                )
        else:
            if other_user_type == 'saraf':
                messages = Message.objects.filter(
                    Q(sender_normal_user=sender_id, receiver_saraf=other_user_id) |
                    Q(sender_saraf=other_user_id, receiver_normal_user=sender_id)
                ).filter(
                    Q(is_deleted_by_sender=False) | Q(is_deleted_by_receiver=False)
                )
            else:
                messages = Message.objects.filter(
                    Q(sender_normal_user=sender_id, receiver_normal_user=other_user_id) |
                    Q(sender_normal_user=other_user_id, receiver_normal_user=sender_id)
                ).filter(
                    Q(is_deleted_by_sender=False) | Q(is_deleted_by_receiver=False)
                )
        
        messages = messages.order_by('-created_at')
        serializer = MessageSerializer(messages, many=True, context={'request': request})
        return Response(serializer.data)


class MessageMarkReadView(APIView):
    """Mark a message as read"""
    permission_classes = [AllowAny]
    
    def post(self, request, message_id):
        # Check session authentication
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            message = Message.objects.get(id=message_id)
            
            # Check if user is the receiver
            user_type = request.session.get('user_type')
            user_id = request.session.get('user_id')
            
            is_receiver = False
            if user_type == 'saraf' and message.receiver_saraf and message.receiver_saraf.saraf_id == user_id:
                is_receiver = True
            elif user_type == 'normal_user' and message.receiver_normal_user and message.receiver_normal_user.normal_user_id == user_id:
                is_receiver = True
            
            if not is_receiver:
                return Response({
                    'error': 'You can only mark messages you received as read'
                }, status=status.HTTP_403_FORBIDDEN)
            
            message.is_read = True
            from django.utils import timezone
            message.read_at = timezone.now()
            message.save()
            
            return Response({'message': 'Message marked as read'})
            
        except Message.DoesNotExist:
            return Response({
                'error': 'Message not found'
            }, status=status.HTTP_404_NOT_FOUND)


class ConversationListView(APIView):
    """List all conversations for the authenticated user"""
    permission_classes = [AllowAny]
    
    def get(self, request):
        # Check session authentication
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        user_type = request.session.get('user_type')
        user_id = request.session.get('user_id')
        
        from django.db.models import Q, Max, Count, Case, When
        
        # Get all messages where user is sender or receiver
        if user_type == 'saraf':
            messages = Message.objects.filter(
                Q(sender_saraf=user_id) | Q(receiver_saraf=user_id)
            ).filter(
                Q(is_deleted_by_sender=False) | Q(is_deleted_by_receiver=False)
            )
        else:
            messages = Message.objects.filter(
                Q(sender_normal_user=user_id) | Q(receiver_normal_user=user_id)
            ).filter(
                Q(is_deleted_by_sender=False) | Q(is_deleted_by_receiver=False)
            )
        
        # Group conversations and get latest message info
        conversations = []
        processed_participants = set()
        
        for message in messages.order_by('-created_at'):
            # Determine the other participant
            if user_type == 'saraf':
                if message.sender_saraf and message.sender_saraf.saraf_id == user_id:
                    # User is sender, get receiver
                    if message.receiver_saraf:
                        participant_id = message.receiver_saraf.saraf_id
                        participant_type = 'saraf'
                        participant_name = message.receiver_saraf.exchange_name
                    else:
                        participant_id = message.receiver_normal_user.normal_user_id
                        participant_type = 'normal_user'
                        participant_name = message.receiver_normal_user.full_name
                else:
                    # User is receiver, get sender
                    if message.sender_saraf:
                        participant_id = message.sender_saraf.saraf_id
                        participant_type = 'saraf'
                        participant_name = message.sender_saraf.exchange_name
                    else:
                        participant_id = message.sender_normal_user.normal_user_id
                        participant_type = 'normal_user'
                        participant_name = message.sender_normal_user.full_name
            else:
                if message.sender_normal_user and message.sender_normal_user.normal_user_id == user_id:
                    # User is sender, get receiver
                    if message.receiver_saraf:
                        participant_id = message.receiver_saraf.saraf_id
                        participant_type = 'saraf'
                        participant_name = message.receiver_saraf.exchange_name
                    else:
                        participant_id = message.receiver_normal_user.normal_user_id
                        participant_type = 'normal_user'
                        participant_name = message.receiver_normal_user.full_name
                else:
                    # User is receiver, get sender
                    if message.sender_saraf:
                        participant_id = message.sender_saraf.saraf_id
                        participant_type = 'saraf'
                        participant_name = message.sender_saraf.exchange_name
                    else:
                        participant_id = message.sender_normal_user.normal_user_id
                        participant_type = 'normal_user'
                        participant_name = message.sender_normal_user.full_name
            
            participant_key = f"{participant_type}_{participant_id}"
            
            if participant_key not in processed_participants:
                processed_participants.add(participant_key)
                
                # Count unread messages from this participant
                unread_count = 0
                if user_type == 'saraf':
                    if participant_type == 'saraf':
                        unread_count = Message.objects.filter(
                            sender_saraf=participant_id,
                            receiver_saraf=user_id,
                            is_read=False
                        ).count()
                    else:
                        unread_count = Message.objects.filter(
                            sender_normal_user=participant_id,
                            receiver_saraf=user_id,
                            is_read=False
                        ).count()
                else:
                    if participant_type == 'saraf':
                        unread_count = Message.objects.filter(
                            sender_saraf=participant_id,
                            receiver_normal_user=user_id,
                            is_read=False
                        ).count()
                    else:
                        unread_count = Message.objects.filter(
                            sender_normal_user=participant_id,
                            receiver_normal_user=user_id,
                            is_read=False
                        ).count()
                
                conversations.append({
                    'participant_id': participant_id,
                    'participant_type': participant_type,
                    'participant_name': participant_name,
                    'last_message': message.content[:100] if message.content else 'Attachment',
                    'last_message_time': message.created_at,
                    'unread_count': unread_count
                })
        
        serializer = ConversationSerializer(conversations, many=True)
        return Response(serializer.data)


# Custom permission class for session-based authentication
class IsSessionAuthenticated:
    """
    Custom permission to check if user is authenticated via session
    """
    def has_permission(self, request, view):
        return request.session.get('is_authenticated', False)


# ReceiveHawala Views
class ReceiveHawalaCreateView(APIView):
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        """
        Create a new ReceiveHawala record by linking to existing sendhawala via hawala_number
        Required fields: hawala_number, receiver_phone, receiver_address
        Optional files: receiver_id_card_photo, receiver_finger_photo
        """
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = ReceiveHawalaCreateSerializer(data=request.data)
        if serializer.is_valid():
            try:
                receive_hawala = serializer.save()
                read_serializer = ReceiveHawalaSerializer(receive_hawala)
                return Response({
                    'message': 'ReceiveHawala created successfully with sendhawala details',
                    'data': read_serializer.data
                }, status=status.HTTP_201_CREATED)
            except serializers.ValidationError as e:
                return Response({
                    'error': 'Validation error',
                    'details': e.detail if hasattr(e, 'detail') else str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({
                    'error': f'Failed to create ReceiveHawala: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ReceiveHawalaDetailView(APIView):
    def get(self, request, pk):
        """
        Get ReceiveHawala details by ID
        """
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            receive_hawala = ReceiveHawala.objects.get(id=pk)
            serializer = ReceiveHawalaSerializer(receive_hawala)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except ReceiveHawala.DoesNotExist:
            return Response({'error': 'ReceiveHawala not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self, request, pk):
        """
        Update ReceiveHawala details
        """
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            receive_hawala = ReceiveHawala.objects.get(id=pk)
            serializer = ReceiveHawalaSerializer(receive_hawala, data=request.data, partial=True)
            if serializer.is_valid():
                updated_receive_hawala = serializer.save()
                return Response({
                    'message': 'ReceiveHawala updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except ReceiveHawala.DoesNotExist:
            return Response({'error': 'ReceiveHawala not found'}, status=status.HTTP_404_NOT_FOUND)


class ReceiveHawalaListView(APIView):
    def get(self, request):
        """
        Get all ReceiveHawala records with optional filtering
        """
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        queryset = ReceiveHawala.objects.all().select_related('sendhawala', 'verified_by')
        
        # Optional filtering
        hawala_number = request.query_params.get('hawala_number')
        receiver_name = request.query_params.get('receiver_name')
        verified_by = request.query_params.get('verified_by')
        
        if hawala_number:
            queryset = queryset.filter(sendhawala__hawala_number=hawala_number)
        if receiver_name:
            queryset = queryset.filter(sendhawala__receiver_name__icontains=receiver_name)
        if verified_by:
            queryset = queryset.filter(verified_by__saraf_id=verified_by)
        
        serializer = ReceiveHawalaSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ReceiveHawalaVerifyView(APIView):
    def post(self, request, pk):
        """
        Verify a ReceiveHawala by a Saraf
        """
        # Check if user is authenticated via session
        if not request.session.get('is_authenticated'):
            return Response({
                'error': 'Authentication required. Please login first.'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Get saraf from session
        saraf_id = request.session.get('user_id')
        user_type = request.session.get('user_type')
        
        if user_type != 'saraf':
            return Response({
                'error': 'Only Saraf users can verify receive hawala'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            receive_hawala = ReceiveHawala.objects.get(id=pk)
            saraf = SarafProfile.objects.get(saraf_id=saraf_id)
            
            # Set verification details
            receive_hawala.verified_by = saraf
            from django.utils import timezone
            receive_hawala.verification_date = timezone.now()
            receive_hawala.save()
            
            serializer = ReceiveHawalaSerializer(receive_hawala)
            return Response({
                'message': 'ReceiveHawala verified successfully', 
                'verified_by': saraf.name, 
                'verification_date': receive_hawala.verification_date
            }, status=status.HTTP_200_OK)
        except ReceiveHawala.DoesNotExist:
            return Response({'error': 'ReceiveHawala not found'}, status=status.HTTP_404_NOT_FOUND)
        except SarafProfile.DoesNotExist:
            return Response({'error': 'Saraf profile not found'}, status=status.HTTP_404_NOT_FOUND)


# CustomerAccount API Views
class CustomerAccountCreateView(APIView):
    """Create a new customer account"""
    
    def post(self, request):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = CustomerAccountCreateSerializer(data=request.data)
        if serializer.is_valid():
            customer_account = serializer.save()
            response_serializer = CustomerAccountSerializer(customer_account)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerAccountListView(APIView):
    """List customer accounts for authenticated saraf"""
    
    def get(self, request):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        customer_accounts = CustomerAccount.objects.filter(saraf_id=saraf_id, is_active=True)
        
        # Optional filtering
        account_number = request.query_params.get('account_number')
        full_name = request.query_params.get('full_name')
        
        if account_number:
            customer_accounts = customer_accounts.filter(account_number__icontains=account_number)
        if full_name:
            customer_accounts = customer_accounts.filter(full_name__icontains=full_name)
        
        serializer = CustomerAccountSerializer(customer_accounts, many=True)
        return Response(serializer.data)


class CustomerAccountDetailView(APIView):
    """Get, update, or delete a specific customer account"""
    
    def get_object(self, account_id, saraf_id):
        try:
            return CustomerAccount.objects.get(id=account_id, saraf_id=saraf_id)
        except CustomerAccount.DoesNotExist:
            return None
    
    def get(self, request, account_id):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        customer_account = self.get_object(account_id, request.session.get('user_id'))
        if not customer_account:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CustomerAccountSerializer(customer_account)
        return Response(serializer.data)
    
    def put(self, request, account_id):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        customer_account = self.get_object(account_id, request.session.get('user_id'))
        if not customer_account:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CustomerAccountSerializer(customer_account, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, account_id):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        customer_account = self.get_object(account_id, request.session.get('user_id'))
        if not customer_account:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        customer_account.is_active = False
        customer_account.save()
        return Response({'message': 'Customer account deactivated successfully'})




class CustomerAccountDepositView(APIView):
    """Customer deposit"""
    
    def post(self, request, account_id):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            customer_account = CustomerAccount.objects.get(id=account_id, saraf_id=request.session.get('user_id'))
        except CustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CustomerFinancialOperationSerializer(data=request.data)
        if serializer.is_valid():
            new_balance = customer_account.deposit(
                currency=serializer.validated_data['currency'],
                amount=serializer.validated_data['amount'],
                description=serializer.validated_data.get('description', '')
            )
            return Response({
                'message': 'Deposit successful',
                'new_balance': str(new_balance),
                'currency': serializer.validated_data['currency'].name
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerAccountWithdrawView(APIView):
    """Customer withdrawal"""
    
    def post(self, request, account_id):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            customer_account = CustomerAccount.objects.get(id=account_id, saraf_id=request.session.get('user_id'))
        except CustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CustomerFinancialOperationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                new_balance = customer_account.withdraw(
                    currency=serializer.validated_data['currency'],
                    amount=serializer.validated_data['amount'],
                    description=serializer.validated_data.get('description', '')
                )
                return Response({
                    'message': 'Withdrawal successful',
                    'new_balance': str(new_balance),
                    'currency': serializer.validated_data['currency'].name
                })
            except ValueError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerAccountTransactionsView(APIView):
    """Get transaction history for customer account"""
    
    def get(self, request, account_id):
        # Check session authentication
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            customer_account = CustomerAccount.objects.get(id=account_id, saraf_id=request.session.get('user_id'))
        except CustomerAccount.DoesNotExist:
            return Response({'error': 'Customer account not found'}, status=status.HTTP_404_NOT_FOUND)
        
        transactions = CustomerTransaction.objects.filter(customer=customer_account)
        
        # Optional filtering
        transaction_type = request.query_params.get('type')
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        
        serializer = CustomerTransactionSerializer(transactions, many=True)
        return Response(serializer.data)


# Colleague Management Views
class SarafColleagueListView(APIView):
    """List all colleagues for authenticated saraf"""
    
    def get(self, request):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        status_filter = request.query_params.get('status')  # 'delivered', 'undelivered'
        
        # Get colleagues where current saraf is either requester or colleague
        colleagues = SarafColleague.objects.filter(
            models.Q(requester_id=saraf_id) | models.Q(colleague_id=saraf_id)
        ).select_related('requester', 'colleague')
        
        # Apply status filter if provided
        if status_filter:
            colleagues = colleagues.filter(status=status_filter)
        
        colleagues = colleagues.order_by('-created_at')
        serializer = SarafColleagueSerializer(colleagues, many=True)
        return Response(serializer.data)


class SarafColleagueCreateView(APIView):
    """Add a new colleague"""
    
    def post(self, request):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = SarafColleagueCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                colleague_relation = serializer.save()
                return Response(SarafColleagueSerializer(colleague_relation).data, status=status.HTTP_201_CREATED)
            except ValidationError as e:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SarafColleagueDetailView(APIView):
    """View colleague relationship details"""
    
    def get(self, request, colleague_id):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        
        try:
            # Find colleague relationship where colleague_id is the saraf_id of the colleague
            colleague_relation = SarafColleague.objects.get(
                models.Q(requester__saraf_id=saraf_id, colleague__saraf_id=colleague_id) |
                models.Q(colleague__saraf_id=saraf_id, requester__saraf_id=colleague_id)
            )
            serializer = SarafColleagueSerializer(colleague_relation)
            return Response(serializer.data)
        except SarafColleague.DoesNotExist:
            return Response({'error': 'Colleague relationship not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, colleague_id):
        """Update colleague status"""
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        
        try:
            # Find colleague relationship where colleague_id is the saraf_id of the colleague
            colleague_relation = SarafColleague.objects.get(
                models.Q(requester__saraf_id=saraf_id, colleague__saraf_id=colleague_id) |
                models.Q(colleague__saraf_id=saraf_id, requester__saraf_id=colleague_id)
            )
            
            new_status = request.data.get('status')
            if new_status not in ['delivered', 'undelivered']:
                return Response({'error': 'Invalid status. Must be delivered or undelivered'}, status=status.HTTP_400_BAD_REQUEST)
            
            colleague_relation.status = new_status
            colleague_relation.save()
            
            serializer = SarafColleagueSerializer(colleague_relation)
            return Response({
                'message': f'Colleague status updated to {new_status}',
                'data': serializer.data
            })
        except SarafColleague.DoesNotExist:
            return Response({'error': 'Colleague relationship not found'}, status=status.HTTP_404_NOT_FOUND)
    


# Loan Management Views
class SarafLoanListView(APIView):
    """List loans given or received by authenticated saraf"""
    
    def get(self, request):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        loan_type = request.query_params.get('type', 'all')  # 'given', 'received', 'all'
        status_filter = request.query_params.get('status')  # 'delivered', 'undelivered'
        separate_filter = request.query_params.get('separate')  # 'delivered', 'undelivered'
        
        if loan_type == 'given':
            loans = SarafLoan.objects.filter(lender_id=saraf_id)
        elif loan_type == 'received':
            loans = SarafLoan.objects.filter(borrower_id=saraf_id)
        else:
            loans = SarafLoan.objects.filter(
                models.Q(lender_id=saraf_id) | models.Q(borrower_id=saraf_id)
            )
        
        # Apply status filter (original functionality)
        if status_filter:
            loans = loans.filter(status=status_filter)
        
        # Apply separate filter (new functionality)
        if separate_filter:
            loans = loans.filter(status=separate_filter)
        
        loans = loans.select_related('lender', 'borrower', 'currency').order_by('-date')
        serializer = SarafLoanSerializer(loans, many=True)
        return Response(serializer.data)


class SarafLoanCreateView(APIView):
    """Create a new loan to a colleague"""
    
    def post(self, request):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = SarafLoanCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            loan = serializer.save()
            response_serializer = SarafLoanSerializer(loan)
            return Response({
                'message': 'Loan created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SarafLoanDetailView(APIView):
    """View loan details"""
    
    def get(self, request, loan_id):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        
        try:
            loan = SarafLoan.objects.get(
                models.Q(id=loan_id) &
                (models.Q(lender_id=saraf_id) | models.Q(borrower_id=saraf_id))
            )
            serializer = SarafLoanSerializer(loan)
            return Response(serializer.data)
        except SarafLoan.DoesNotExist:
            return Response({'error': 'Loan not found or access denied'}, status=status.HTTP_404_NOT_FOUND)


class SarafLoanRepayView(APIView):
    """Repay a loan"""
    
    def post(self, request, loan_id):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        
        try:
            loan = SarafLoan.objects.get(id=loan_id, borrower_id=saraf_id, status='active')
        except SarafLoan.DoesNotExist:
            return Response({'error': 'Active loan not found or you are not the borrower'}, status=status.HTTP_404_NOT_FOUND)
        
        # Mark loan as repaid
        loan.repay()
        
        serializer = SarafLoanSerializer(loan)
        return Response({
            'message': 'Loan repaid successfully',
            'data': serializer.data
        })


class SarafLoanDefaultView(APIView):
    """Mark a loan as defaulted (only lender can do this)"""
    
    def post(self, request, loan_id):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        
        try:
            loan = SarafLoan.objects.get(id=loan_id, lender_id=saraf_id, status='active')
        except SarafLoan.DoesNotExist:
            return Response({'error': 'Active loan not found or you are not the lender'}, status=status.HTTP_404_NOT_FOUND)
        
        # Mark loan as defaulted
        loan.default()
        
        serializer = SarafLoanSerializer(loan)
        return Response({
            'message': 'Loan marked as defaulted',
            'data': serializer.data
        })


# Currency Exchange Views
class CurrencyExchangeListView(APIView):
    """List currency exchanges made or received by authenticated saraf"""
    
    def get(self, request):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        exchange_type = request.query_params.get('type', 'all')  # 'made', 'received', 'all'
        status_filter = request.query_params.get('status')
        
        if exchange_type == 'made':
            exchanges = CurrencyExchange.objects.filter(exchanger_id=saraf_id)
        elif exchange_type == 'received':
            exchanges = CurrencyExchange.objects.filter(receiver_id=saraf_id)
        else:
            exchanges = CurrencyExchange.objects.filter(
                models.Q(exchanger_id=saraf_id) | models.Q(receiver_id=saraf_id)
            )
        
        if status_filter:
            exchanges = exchanges.filter(status=status_filter)
        
        exchanges = exchanges.select_related('exchanger', 'receiver', 'from_currency', 'to_currency').order_by('-date')
        serializer = CurrencyExchangeSerializer(exchanges, many=True)
        return Response(serializer.data)


class CurrencyExchangeCreateView(APIView):
    """Create a new currency exchange"""
    
    def post(self, request):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = CurrencyExchangeCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            exchange = serializer.save()
            response_serializer = CurrencyExchangeSerializer(exchange)
            return Response({
                'message': 'Currency exchange created successfully',
                'data': response_serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrencyExchangeDetailView(APIView):
    """View currency exchange details"""
    
    def get(self, request, exchange_id):
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        
        try:
            exchange = CurrencyExchange.objects.get(
                models.Q(id=exchange_id) &
                (models.Q(exchanger_id=saraf_id) | models.Q(receiver_id=saraf_id))
            )
            serializer = CurrencyExchangeSerializer(exchange)
            return Response(serializer.data)
        except CurrencyExchange.DoesNotExist:
            return Response({'error': 'Exchange not found or access denied'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, exchange_id):
        """Update exchange status (delivered/undelivered)"""
        if not request.session.get('is_authenticated') or request.session.get('user_type') != 'saraf':
            return Response({'error': 'Saraf authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        saraf_id = request.session.get('user_id')
        new_status = request.data.get('status')
        
        if new_status not in ['delivered', 'undelivered']:
            return Response({'error': 'Status must be either "delivered" or "undelivered"'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            exchange = CurrencyExchange.objects.get(
                models.Q(id=exchange_id) &
                (models.Q(exchanger_id=saraf_id) | models.Q(receiver_id=saraf_id))
            )
            exchange.status = new_status
            exchange.save()
            
            serializer = CurrencyExchangeSerializer(exchange)
            return Response({
                'message': f'Exchange status updated to {new_status}',
                'data': serializer.data
            })
        except CurrencyExchange.DoesNotExist:
            return Response({'error': 'Exchange not found or access denied'}, status=status.HTTP_404_NOT_FOUND)