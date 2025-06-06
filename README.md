# url_health_monitor
# URL Health Monitor

A web-based application that monitors the health and response times of URLs. It provides real-time status updates, response time tracking, and historical metrics for monitoring website availability.

![URL Health Monitor Screenshot](screenshot.png)
![URL Health Monitor Screenshot](screenshot.png(2))
![URL Health Monitor Screenshot](screenshot.png(3))

## Features

- **Real-time URL Health Checks**: Check the status of multiple URLs simultaneously
- **Response Time Tracking**: Monitor how long each URL takes to respond
- **Historical Data**: View up to 5 most recent checks in the history panel
- **Detailed Metrics**: Track uptime, response times, and downtime incidents
- **User-friendly Interface**: Simple and intuitive web interface
- **Docker Support**: Easy deployment using Docker
- **Responsive Design**: Works on both desktop and mobile devices

## Prerequisites

- Python 3.7 or higher
- pip (Python package installer)
- (Optional) Docker and Docker Compose

## Installation

### Using Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd url-health-monitor
   ```

2. Build and run the Docker container:
   ```bash
   docker build -t url-health-monitor .
   docker run -d -p 5001:5001 --name url-monitor url-health-monitor
   ```

3. Open your browser and navigate to: `http://localhost:5001`

### Manual Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd url-health-monitor
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the application:
   ```bash
   python app.py
   ```

5. Open your browser and navigate to: `http://localhost:5001`

## Usage

1. **Check URL Health**:
   - Enter one or more URLs (one per line) in the text area
   - Click the "Check URLs" button to perform the health check

2. **View Results**:
   - Green indicates the URL is up
   - Red indicates the URL is down
   - Response time is displayed in milliseconds

3. **View History**:
   - The right panel shows the history of recent checks
   - Click on a timestamp to view details of that check

4. **View Metrics**:
   - Click on the "View Metrics" button to see detailed metrics for all checked URLs
   - Includes uptime percentage, average response time, and more

## API Endpoints

The application also provides the following API endpoints:

- `GET /metrics` - Get metrics for all URLs
- `GET /metrics/<path:url>` - Get metrics for a specific URL
- `POST /clear-history` - Clear the check history

## Configuration

You can configure the application by setting the following environment variables:

- `FLASK_APP`: The application file (default: `app.py`)
- `FLASK_ENV`: The environment (default: `production`)
- `FLASK_DEBUG`: Enable/disable debug mode (default: `False`)

## Security Considerations

- The application uses Flask's built-in development server which is not suitable for production use. For production, consider using a production WSGI server like Gunicorn or uWSGI.
- By default, the application runs on all network interfaces (`0.0.0.0`). In production, make sure to properly secure the application.
- The application doesn't currently implement user authentication. If you plan to expose it to the internet, consider adding authentication.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built with [Flask](https://flask.palletsprojects.com/)
- Uses [Requests](https://docs.python-requests.org/) for HTTP requests
- Frontend built with HTML, CSS, and JavaScript
