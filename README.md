# Fuel Route Optimization API

This project provides an API for optimizing fuel routes, finding the most cost-effective fuel stops along a given route.

## Features

- Calculate optimal route between two locations
- Find cost-effective fuel stops along the route
- Generate a map of the route with fuel stops
- Calculate total fuel cost for the trip

## Tech Stack

- Django 3.2.23
- Python 3.12.7
- PostgreSQL with PostGIS
- Docker and Docker Compose

## Setup and Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/fuel-route-optimization.git
   cd fuel-route-optimization
   ```

2. Build and run the Docker containers:
   ```
   docker-compose up --build
   ```

3. The API will be available at `http://localhost:8000/api/optimal-route/`

## Usage

Send a POST request to `/api/optimal-route/` with the following JSON body:

```json
{
  "start": "New York, NY",
  "end": "Los Angeles, CA"
}
```

The API will return a JSON response with the optimal route, fuel stops, and a map of the route.

## Running Tests

To run the tests, use the following command:

```
docker-compose run web python manage.py test
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.