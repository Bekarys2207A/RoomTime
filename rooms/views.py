from rest_framework import generics
from rest_framework.permissions import IsAdminUser, AllowAny
from .models import Resource
from .serializer import ResourceSerializer


class ResourceListCreateAPIView(generics.ListCreateAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    # Разрешения по действию (list/create)
    permission_classes_by_action = {
        'list': [AllowAny],
        'create': [IsAdminUser],
    }

    def get_permissions(self):
        # У ListCreateAPIView действия предоставляются миксинами list/create
        # Если нет действия (редкий случай), даём безопасный fallback.
        action = getattr(self, 'action', None)
        # Для GenericAPIView без ViewSet self.action обычно не выставляется автоматически.
        # Поэтому сопоставим по методу запроса.
        if action is None:
            method = self.request.method
            if method == 'GET':
                action = 'list'
            elif method == 'POST':
                action = 'create'
        perms = self.permission_classes_by_action.get(action, [AllowAny])
        return [perm() for perm in perms]

    def get_queryset(self):
        queryset = Resource.objects.all()
        is_active = self.request.query_params.get('is_active')
        location = self.request.query_params.get('location')
        capacity = self.request.query_params.get('capacity')

        if is_active is not None:
            # Преобразуем строку в bool: 'true'/'1'/'yes' → True
            val = is_active.strip().lower()
            is_true = val in ('true', '1', 'yes', 'y')
            is_false = val in ('false', '0', 'no', 'n')
            if is_true:
                queryset = queryset.filter(is_active=True)
            elif is_false:
                queryset = queryset.filter(is_active=False)
            # иначе игнорируем некорректное значение

        if location is not None:
            queryset = queryset.filter(location__icontains=location)

        if capacity is not None:
            try:
                queryset = queryset.filter(capacity__gte=int(capacity))
            except (TypeError, ValueError):
                # Некорректное число — просто игнорируем фильтр
                pass

        return queryset


class ResourceRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Resource.objects.all()
    serializer_class = ResourceSerializer

    # Разрешения по действию (retrieve/update/destroy)
    permission_classes_by_action = {
        'retrieve': [AllowAny],
        'update': [IsAdminUser],
        'partial_update': [IsAdminUser],
        'destroy': [IsAdminUser],
    }

    def get_permissions(self):
        # Для RUD-вью сопоставим действия по методу запроса
        # PUT/PATCH → update/partial_update, DELETE → destroy, GET → retrieve
        action = getattr(self, 'action', None)
        if action is None:
            method = self.request.method
            if method == 'GET':
                action = 'retrieve'
            elif method == 'PUT':
                action = 'update'
            elif method == 'PATCH':
                action = 'partial_update'
            elif method == 'DELETE':
                action = 'destroy'
        perms = self.permission_classes_by_action.get(action, [AllowAny])
        return [perm() for perm in perms]
