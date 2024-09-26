import logging
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer, ItemSerializer
from django.core.cache import cache
from .models import Item
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError

User = get_user_model()

# Set up logging
logger = logging.getLogger('inventory')

# API to user Registration
class UserRegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f'User registered: {user.username}')  # Log user registration

# API to user Login
class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)

        logger.info(f'User logged in: {user.username}')  # Log user login

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })


# API to List and Create Items
class ItemListCreateView(generics.ListCreateAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        item_data = serializer.validated_data

        # Check if item already exists
        if Item.objects.filter(name=item_data['name']).exists():
            logger.warning(f'Attempt to create duplicate item: {item_data["name"]}')  # Log duplicate item attempt
            raise ValidationError({'non_field_errors': ['Item already exists.']})

        # If the item doesn't exist, save the new item
        item = serializer.save()
        logger.info(f'Item created: {item.id} - {item.name}')  # Log item creation


# API to Retrieve, Update, and Delete Items (with Redis caching for retrieval)
class ItemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        item_id = self.kwargs.get('pk')
        cached_item = cache.get(f'item_{item_id}')
        
        if cached_item:
            logger.info(f'Item retrieved from cache: {item_id}')  # Log cache retrieval
            return Response(cached_item, status=status.HTTP_200_OK)
        
        response = super().get(request, *args, **kwargs)
        
        # Cache the item if it's fetched from the database
        if response.status_code == status.HTTP_200_OK:
            cache.set(f'item_{item_id}', response.data)
            logger.info(f'Item retrieved from database and cached: {item_id}')  # Log item caching
        
        return response

    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        
        # Update the cache after updating the item
        if response.status_code == status.HTTP_200_OK:
            cache.set(f'item_{self.kwargs.get("pk")}', response.data)
            logger.info(f'Item updated: {self.kwargs.get("pk")}')  # Log item update
        
        return response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)

        # Clear cache when an item is deleted
        if response.status_code == status.HTTP_204_NO_CONTENT:
            cache.delete(f'item_{self.kwargs.get("pk")}')
            logger.info(f'Item deleted: {self.kwargs.get("pk")}')  # Log item deletion

        return response
