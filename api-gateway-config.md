# API Gateway Configuration for Weather Service
# Adjust based on your API Gateway technology (Kong, Nginx, Traefik, etc.)

## Example 1: Kong Configuration
# Create service
curl -X POST http://your-kong-admin:8001/services \
  --data "name=weather-service" \
  --data "url=http://weather-backend:8000"

# Create route for weather automation
curl -X POST http://your-kong-admin:8001/services/weather-service/routes \
  --data "paths[]=/api/v1/weather" \
  --data "strip_path=true"

## Example 2: Nginx Configuration
server {
    listen 80;
    server_name your-api-gateway.domain;

    location /api/v1/weather/ {
        proxy_pass http://weather-backend:8000/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

## Example 3: Traefik Configuration (docker-compose.yml)
labels:
  - "traefik.enable=true"
  - "traefik.http.routers.weather-api.rule=Host(`your-api-gateway.domain`) && PathPrefix(`/api/v1/weather`)"
  - "traefik.http.routers.weather-api.middlewares=weather-stripprefix"
  - "traefik.http.middlewares.weather-stripprefix.stripprefix.prefixes=/api/v1/weather"
  - "traefik.http.services.weather-api.loadbalancer.server.port=8000"

## Example 4: AWS API Gateway / Azure API Management
# REST API Configuration:
# Resource: /weather/{proxy+}
# Method: ANY
# Integration: HTTP Proxy
# Endpoint URL: http://your-weather-backend:8000/{proxy}
