# MyCerts Module

## Overview
MyCerts is a comprehensive certificate and achievement management module designed for college students. It allows users to upload, categorize, organize, and export their various growth records, including competition awards, volunteer service certificates, research project participation, scholarships, and internship experiences.

## Features
- Dashboard with statistics and recent uploads
- Certificate upload with category classification
- List view with filtering and sorting
- Detailed view of each certificate
- Export functionality for creating personal achievement portfolios
- Support for multiple file formats (PDF, JPG, PNG)
- Volunteer hours tracking
- Date range support for activities
- Bilingual support (English/Chinese)

## Technical Integration

### Database Setup
1. The module uses SQLAlchemy for database operations
2. Required tables:
   - certificates (stores all certificate records)
   - users (referenced by certificates)

### API Endpoints
```python
# Main routes
GET  /mycerts              # Dashboard view
GET  /mycerts/upload       # Upload form
POST /mycerts/upload       # Handle file upload
GET  /mycerts/list         # List all certificates
GET  /mycerts/detail/<id>  # View certificate details
GET  /mycerts/export       # Export form
POST /mycerts/export       # Generate export file
GET  /mycerts/download/<id> # Download certificate file
```

### Integration Steps
1. Add the module to your Flask application:
```python
from MyCerts import mycerts

app.register_blueprint(mycerts)
```

2. Configure the database:
```python
from MyCerts.models import db

db.init_app(app)
```

3. Set up file upload directory:
```python
UPLOAD_FOLDER = 'uploads/certificates'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
```

### Dependencies
- Flask
- Flask-SQLAlchemy
- Werkzeug
- Python-dateutil

## File Structure
```
MyCerts/
├── __init__.py
├── models.py
├── routes.py
├── README.md
├── README_zh.md
└── prototype/
    ├── main.html
    ├── upload.html
    ├── list.html
    ├── detail.html
    └── export.html
```

## Usage Example
```python
# Initialize the module
from MyCerts import mycerts
app.register_blueprint(mycerts)

# Access certificate statistics
from MyCerts.models import Certificate
stats = Certificate.get_stats(user_id)
```

## Notes
- All file uploads are limited to 10MB
- Supported file formats: PDF, JPG, PNG
- The module requires user authentication (user_id must be provided)
- All dates are stored in UTC
- File paths are stored relative to the application root 