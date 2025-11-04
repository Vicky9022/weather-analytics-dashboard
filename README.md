# Weather Analytics Dashboard

A Django REST API application with PostgreSQL that tracks weather data for cities, integrates with OpenWeatherMap API, and provides analytics and visualization capabilities.

## Features

- **CRUD Operations**: Full Create, Read, Update, Delete functionality for Cities and Weather Records
- **Third-Party API Integration**: Fetches real-time weather data from OpenWeatherMap API
- **Data Analytics**: Provides statistical analysis and trends of weather data
- **RESTful API**: Well-structured REST endpoints with Django REST Framework
- **PostgreSQL Database**: Relational database with optimized queries and indexing
- **Data Visualization**: JSON endpoints optimized for frontend charting libraries

## Tech Stack

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL (or Supabase)
- **External API**: OpenWeatherMap API
- **Python**: 3.8+

## Prerequisites

- Python 3.8 or higher
- PostgreSQL 12+ (or Supabase account)
- OpenWeatherMap API key (free tier available)

## Installation & Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd weather-analytics
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: Local PostgreSQL

1. Install PostgreSQL on your system
2. Create database:
```bash
psql -U postgres
CREATE DATABASE weather_db;
\q
```

#### Option B: Supabase

1. Sign up at [supabase.com](https://supabase.com)
2. Create a new project
3. Get connection details from Settings > Database
4. Update `.env` with Supabase credentials
5. In `settings.py`, comment out local DB config and uncomment Supabase config

### 5. Environment Variables

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your values:
- Set `DJANGO_SECRET_KEY` (generate with: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`)
- Add your database credentials
- Add your OpenWeatherMap API key from https://openweathermap.org/api

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

### 8. Run Development Server

```bash
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`

## Project Structure

```
weather-analytics/
├── weather_project/
│   ├── settings.py          # Django settings
│   ├── urls.py              # URL routing
│   └── wsgi.py
├── weather/
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API views
│   └── admin.py             # Admin configuration
├── requirements.txt
├── .env.example
└── README.md
```

## API Endpoints

### Cities

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cities/` | List all cities |
| POST | `/api/cities/` | Create a new city |
| GET | `/api/cities/{id}/` | Get city details with recent weather |
| PUT | `/api/cities/{id}/` | Update city |
| DELETE | `/api/cities/{id}/` | Delete city |
| POST | `/api/cities/{id}/fetch_weather/` | Fetch current weather from API |

### Weather Records

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/weather-records/` | List all weather records |
| POST | `/api/weather-records/` | Create weather record manually |
| GET | `/api/weather-records/{id}/` | Get specific record |
| PUT | `/api/weather-records/{id}/` | Update record |
| DELETE | `/api/weather-records/{id}/` | Delete record |
| GET | `/api/weather-records/analytics/` | Get analytics and trends |

### Query Parameters

**Weather Records List:**
- `city_id`: Filter by city (e.g., `?city_id=1`)
- `days`: Filter by days (e.g., `?days=7`)

**Analytics:**
- `city_id`: Analytics for specific city
- `days`: Period in days (default: 7)

## Usage Examples

### 1. Create a City

```bash
curl -X POST http://localhost:8000/api/cities/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Mumbai",
    "country": "India",
    "latitude": 19.0760,
    "longitude": 72.8777
  }'
```

### 2. Fetch Weather Data from API

```bash
curl -X POST http://localhost:8000/api/cities/1/fetch_weather/
```

This will:
- Call OpenWeatherMap API
- Fetch current weather for the city
- Save the data to database
- Return the created weather record

### 3. Get Analytics

```bash
# Last 7 days analytics for all cities
curl http://localhost:8000/api/weather-records/analytics/

# Last 30 days for specific city
curl http://localhost:8000/api/weather-records/analytics/?city_id=1&days=30
```

### 4. List Weather Records

```bash
# All records
curl http://localhost:8000/api/weather-records/

# Filtered by city and time
curl "http://localhost:8000/api/weather-records/?city_id=1&days=7"
```

## Testing the Application

### 1. Using Django Admin

1. Access admin panel: `http://localhost:8000/admin/`
2. Login with superuser credentials
3. Add cities and view weather records

### 2. Using API Browser

1. Visit `http://localhost:8000/api/`
2. Use DRF's browsable API interface
3. Test all endpoints interactively

### 3. Sample Test Workflow

```bash
# 1. Create cities
curl -X POST http://localhost:8000/api/cities/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "London",
    "country": "UK",
    "latitude": 51.5074,
    "longitude": -0.1278
  }'

# 2. Fetch weather data
curl -X POST http://localhost:8000/api/cities/1/fetch_weather/

# 3. View analytics
curl http://localhost:8000/api/weather-records/analytics/?days=7

# 4. Get city details with weather
curl http://localhost:8000/api/cities/1/
```

## Data Visualization

The analytics endpoint returns data in a format optimized for charting libraries like Chart.js, Recharts, or D3.js:

```json
{
  "period": "Last 7 days",
  "statistics": {
    "average_temperature": 25.5,
    "max_temperature": 30.2,
    "min_temperature": 20.8,
    "average_humidity": 65.3,
    "total_records": 42
  },
  "daily_trends": [
    {
      "date": "2025-10-28",
      "avg_temperature": 24.5,
      "avg_humidity": 62.0
    }
  ],
  "city_summary": [
    {
      "city_name": "Mumbai",
      "country": "India",
      "avg_temperature": 28.5,
      "record_count": 15
    }
  ]
}
```

## Database Schema

### Cities Table
- id (Primary Key)
- name (String, Unique)
- country (String)
- latitude (Float)
- longitude (Float)
- created_at (DateTime)
- updated_at (DateTime)

### Weather Records Table
- id (Primary Key)
- city_id (Foreign Key → Cities)
- temperature (Float)
- feels_like (Float)
- humidity (Integer)
- pressure (Integer)
- wind_speed (Float)
- description (String)
- recorded_at (DateTime)
- created_at (DateTime)

## Environment Variables Reference

| Variable | Description | Required |
|----------|-------------|----------|
| DJANGO_SECRET_KEY | Django secret key | Yes |
| DEBUG | Debug mode (True/False) | No |
| DB_NAME | Database name | Yes |
| DB_USER | Database user | Yes |
| DB_PASSWORD | Database password | Yes |
| DB_HOST | Database host | Yes |
| DB_PORT | Database port | Yes |
| OPENWEATHER_API_KEY | OpenWeatherMap API key | Yes |

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running
- Check credentials in `.env`
- For Supabase, ensure IP is allowlisted

### API Key Issues
- Verify OpenWeatherMap API key is valid
- Free tier has rate limits (60 calls/minute)
- Check API key is in `.env` file

### Migration Issues
```bash
# Reset migrations
python manage.py migrate weather zero
python manage.py migrate
```

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Add your domain to `ALLOWED_HOSTS` in `settings.py`
3. Use secure secret key
4. Configure proper PostgreSQL connection
5. Set up HTTPS
6. Use environment-specific settings
7. Run `python manage.py collectstatic`

## License

MIT License

## Author

Created as a demonstration of Django REST API with PostgreSQL and third-party API integration.