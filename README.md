# Hamster Media

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd hamster_media
```

2. Create and activate virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create media directory:
```bash
mkdir media
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Run the development server:
```bash
python manage.py runserver
```

## Project Structure
- `media/`: Directory for storing uploaded files (not tracked in git)
- `venv/`: Python virtual environment (not tracked in git)

## Note
The `media` directory is not tracked in git. You need to create it manually after cloning the repository. Any files uploaded through the application will be stored in this directory. 