# Fuel Route Optimizer

A Django-based application that finds optimal routes for trucks considering fuel stops and costs along the way. The application uses OpenRouteService for routing and PostGIS for geospatial calculations.


## Architecture

### Hexagonal Architecture

This project implements Hexagonal Architecture (also known as Ports and Adapters pattern) to maintain clean separation of concerns and high testability. The architecture is structured in the following layers:

#### Domain Layer (Core)
Located in `fuel_route|data`:
- `data_types.py`: Core domain models using dataclasses
- `models.py`: Database entities
- `enums.py`: Domain enumerations
- `exceptions.py`: Domain-specific exceptions

#### Ports (Primary/Driving and Secondary/Driven)
Primary Ports (`fuel_route|controllers`):
- `fuel_route_controller.py`: Handles business operations
- Interfaces that define how the application can be used by external actors

Secondary Ports (`fuel_route|services`):
- Abstract interfaces for external services (geocoding, routing)
- Database operations interfaces

#### Adapters
Primary Adapters (`fuel_route|views`):
- REST API endpoints
- Web views
- Command-line interfaces

Secondary Adapters:
- `fuel_route|services|ors_service_client.py`: OpenRouteService integration
- `fuel_route|services|geocoding_service.py`: Geocoding service integration
- Database implementations in Django models

```
┌──────────────────────────────────────────────────────────────────┐
│                        Primary Adapters                          │
│ ┌────────────────┐ ┌─────────────────┐ ┌─────────────────────┐ │
│ │     Views      │ │   CLI Commands  │ │     API Endpoints    │ │
│ └───────┬────────┘ └────────┬────────┘ └──────────┬──────────┘ │
└─────────┼─────────────────┬─┴───────────────────┬─┴────────────┘
          │                 │                      │
          │                 ▼                      │
┌─────────┴─────────────────────────────────────┬─┴────────────┐
│                   Primary Ports                │              │
│  ┌──────────────────────────────────────────┐ │              │
│  │           Controllers Layer               │ │              │
│  └──────────────────┬───────────────────────┘ │   Domain     │
│                     │                         │    Layer      │
│  ┌──────────────────┴───────────────────────┐ │   (Core)     │
│  │           Secondary Ports                 │ │              │
│  └──────────────────┬───────────────────────┘ │              │
└──────────────────┬──┴─────────────────────────┴──────────────┘
                   │
┌──────────────────┴───────────────────────────────────────────┐
│                     Secondary Adapters                        │
│  ┌────────────────┐ ┌────────────────┐ ┌─────────────────┐  │
│  │  ORS Client    │ │    Database    │ │    Geocoding    │  │
│  └────────────────┘ └────────────────┘ └─────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

### Technical Details

#### Data Flow
1. HTTP requests are received by Django views (`fuel_route/views/fuel_route_view.py`)
2. Views validate input using serializers (`fuel_route/data/serializers.py`)
3. Controllers process business logic (`fuel_route/controllers/fuel_route_controller.py`)
4. Services handle external integrations (`fuel_route/services/`)
5. Data models manage persistence (`fuel_route/data/models.py`)

#### Key Components

##### Route Optimization Engine
- Implements specialized algorithms for finding optimal fuel stops
- Considers factors like:
  - Fuel tank capacity
  - Current fuel prices
  - Distance between stops
  - Vehicle fuel efficiency
  - Route constraints

```python
def calculate_optimal_fuel_stops(
    fuel_stations: QuerySet,
    route: LineString,
    total_distance: float
) -> List[FuelStation]:
    # Dynamic programming approach for optimal stops
    # Considers fuel prices, distances, and constraints
```

##### Geospatial Processing
- Uses PostGIS for spatial queries and calculations
- Implements custom geospatial functions:
  - Route interpolation
  - Point-to-line distance calculations
  - Buffer zone creation
  - Coordinate transformations

##### External Service Integration
- OpenRouteService for route calculation
- Geocoding services for address resolution
- Error handling and retry mechanisms
- Rate limiting and caching

#### Performance Considerations

1. Database Optimization
- Spatial indexes on geometry columns
- Efficient queries using Django's spatial lookups
- Proper model relationships and indexes

2. Caching Strategy
- Route calculations caching
- Geocoding results caching
- Fuel price updates caching

3. Async Operations
- Asynchronous geocoding
- Batch processing for fuel station imports
- Background tasks for data updates

#### Security Measures

1. Input Validation
- Schema validation using serializers
- Coordinate and address verification
- Rate limiting on API endpoints

2. Data Protection
- Environment variable configuration
- API key security
- Database connection security

3. Error Handling
- Graceful degradation
- Comprehensive error messages
- Logging and monitoring

#### Scalability

The application is designed to scale horizontally:
- Stateless application layer
- Containerized deployment support
- Separated concerns for easy component scaling
- Cache-friendly architecture
- Background task processing capability

#### Monitoring and Logging

1. Application Metrics
- Route calculation times
- External service response times
- Database query performance
- API endpoint usage

2. Logging Strategy
- Structured logging
- Error tracking
- Performance monitoring
- External service integration status


## Features

- Route optimization with fuel stop planning
- Real-time fuel price consideration
- Interactive map visualization using Folium
- Geocoding support
- RESTful API endpoints
- Support for HGV (Heavy Goods Vehicle) routing

## Prerequisites

### Local Development
- Python 3.12.7
- PostgreSQL 14+ with PostGIS extension
- OpenRouteService API key
- Pipenv (for dependency management)

### Docker Development
- Docker
- Docker Compose

## Local Development Setup

1. Install PostgreSQL and PostGIS:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib postgis
```

2. Create PostgreSQL database and user:
```sql
CREATE DATABASE spotter_route;
CREATE USER spotter_route_user WITH PASSWORD 'spotter_route_password';
ALTER ROLE spotter_route_user SET client_encoding TO 'utf8';
ALTER ROLE spotter_route_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE spotter_route_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE spotter_route TO spotter_route_user;
\c spotter_route
CREATE EXTENSION postgis;
```

3. Clone the repository:
```bash
git clone <repository-url>
cd spotter-route
```

4. Install Pipenv:
```bash
pip install pipenv
```

5. Install dependencies:
```bash
pipenv install
```

6. Create .env file:
```bash
OPENROUTESERVICE_API_KEY=your-api-key-here
DB_NAME=spotter_route
DB_USER=spotter_route_user
DB_PASSWORD=spotter_route_password
DB_HOST=localhost
DB_PORT=5432
DEBUG=True
SECRET_KEY=your-secret-key-here
```

7. Activate virtual environment:
```bash
pipenv shell
```

8. Run migrations:
```bash
python manage.py migrate
```

9. Import fuel stations data:
```bash
python manage.py import_fuel_stations fuel_stations.csv
```

10. Run development server:
```bash
python manage.py runserver
```

## Docker Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd spotter-route
```

2. Create .env file (same as above)

3. Build and run with Docker Compose:
```bash
docker-compose build
docker-compose up -d
```

4. Run migrations in Docker:
```bash
docker-compose exec web python manage.py migrate
```

5. Import fuel stations data in Docker:
```bash
docker-compose exec web python manage.py import_fuel_stations fuel_stations.csv
```

## API Endpoints

### Optimal Route
- **URL**: `/api/optimal-route/`
- **Method**: POST
- **Body**:
```json
{
    "start": "New York, NY",
    "end": "Los Angeles, CA",
    "include_map_html": true
}
```
- **Response**:
```json
{
    "route": {
        "start": "New York, NY",
        "end": "Los Angeles, CA",
        "distance": 2789.4,
        "fuel_stops": [...],
        "total_cost": 523.45,
        "coordinates": [...]
    },
    "map_html": "<html>...</html>"
}
```

## Development

### Running Tests
```bash
# Local
pipenv run python manage.py test

# Docker
docker-compose exec web python manage.py test
```

### Code Quality
```bash
# Install dev dependencies
pipenv install --dev

# Run linting
pipenv run flake8

# Run type checking
pipenv run mypy .
```

## Project Structure

```
spotter-route/
├── fuel_route/
│   ├── controllers/     # Business logic controllers
│   ├── data/           # Data models and types
│   ├── management/     # Django management commands
│   ├── migrations/     # Database migrations
│   ├── services/       # External service integrations
│   └── views/          # API views and endpoints
├── spotter_route/      # Project settings
└── manage.py          # Django management script
```

## Dependencies

Main project dependencies include:
- Django 3.2.23
- django-rest-framework
- openrouteservice
- Folium
- geopy
- PostGIS
- psycopg2-binary

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| OPENROUTESERVICE_API_KEY | OpenRouteService API key | None |
| DB_NAME | Database name | spotter_route |
| DB_USER | Database user | spotter_route_user |
| DB_PASSWORD | Database password | spotter_route_password |
| DB_HOST | Database host | localhost |
| DB_PORT | Database port | 5432 |
| DEBUG | Debug mode | False |
| SECRET_KEY | Django secret key | None |

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.