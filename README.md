# Bookings API

## Описание
Модуль бронирований для системы RoomTime. Позволяет пользователям бронировать ресурсы (комнаты) с проверкой доступности.

## Эндпоинты

### Основные CRUD операции
- `GET /api/bookings/` - список бронирований
- `POST /api/bookings/` - создать бронирование
- `GET /api/bookings/{id}/` - детали бронирования
- `PUT /api/bookings/{id}/` - обновить бронирование
- `DELETE /api/bookings/{id}/` - удалить бронирование

### Дополнительные эндпоинты
- `POST /api/bookings/{id}/cancel/` - отменить бронирование
- `GET /api/bookings/resources/{id}/availability/?date=YYYY-MM-DD` - проверить доступность ресурса

## Фильтрация и поиск
- `?resource=1` - фильтрация по ресурсу
- `?mine=true` - только мои бронирования
- `?search=room` - поиск по названию ресурса или email пользователя
- `?ordering=starts_at` - сортировка по времени начала
- `?ordering=-created_at` - сортировка по дате создания (новые сначала)

## Примеры запросов

### Создание бронирования
```http
POST /api/bookings/
Content-Type: application/json

{
  "resource": 1,
  "starts_at": "2025-01-15T10:00:00Z",
  "ends_at": "2025-01-15T12:00:00Z"
}