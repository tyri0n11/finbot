# Nginx Setup Instructions for Weather API Gateway

## 1. Install Nginx (if not already installed)
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx
# or
sudo dnf install nginx
```

## 2. Deploy Configuration
```bash
# Copy configuration file
sudo cp nginx-weather-api.conf /etc/nginx/sites-available/weather-api

# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/weather-api /etc/nginx/sites-enabled/

# Test nginx configuration
sudo nginx -t

# Reload nginx
sudo systemctl reload nginx
```

## 3. Update Domain/IP
Edit the configuration file and change:
```nginx
server_name your-weather-api.domain.com;
```
to your actual domain or IP address.

## 4. Setup SSL (Optional but Recommended)
```bash
# Using Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-weather-api.domain.com

# Or update SSL paths in the configuration
ssl_certificate /path/to/your/ssl/certificate.pem;
ssl_certificate_key /path/to/your/ssl/private.key;
```

## 5. Test the Setup
```bash
# Test health endpoint
curl http://your-weather-api.domain.com/health

# Test weather crawl endpoint
curl -X POST http://your-weather-api.domain.com/api/v1/weather/automation/crawl \
  -H "Content-Type: application/json" \
  -d '{"location": "Ho Chi Minh City"}'
```

## 6. N8N Configuration
In your N8N workflows, use these URLs:

**HTTP Request Node:**
- URL: `http://your-weather-api.domain.com/api/v1/weather/automation/crawl`
- Method: POST
- Headers: `Content-Type: application/json`
- Body: `{"location": "City Name"}`

## 7. Monitoring
```bash
# Check nginx status
sudo systemctl status nginx

# View access logs
sudo tail -f /var/log/nginx/weather-api.access.log

# View error logs
sudo tail -f /var/log/nginx/weather-api.error.log
```

## 8. Firewall Configuration
```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 'Nginx Full'
# or
sudo ufw allow 80
sudo ufw allow 443
```
