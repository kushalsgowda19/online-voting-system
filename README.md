# Online Voting System

## Backend (Django)

### 1. Install dependencies

```
pip install -r requirements.txt
```

If `requirements.txt` does not exist, install manually:
```
pip install django djangorestframework djangorestframework-simplejwt django-cors-headers
```

### 2. Run migrations

```
python manage.py migrate
```

### 3. Create a superuser (for admin)

```
python manage.py createsuperuser
```

### 4. (Optional) Load example data

You can use the Django admin to create elections and candidates, or load the following fixture:

```
python manage.py loaddata example_data.json
```

### 5. Run the backend server

```
python manage.py runserver
```

The API will be available at `http://localhost:8000/api/`


## Frontend (React)

### 1. Install dependencies

```
cd voting_system_frontend
npm install
```

### 2. Start the frontend

```
npm start
```

The app will be available at `http://localhost:3000/`


## Example API Endpoints

- Register: `POST /api/register/`
- Login: `POST /api/token/`
- List elections: `GET /api/elections/`
- Election detail: `GET /api/elections/<id>/`
- Vote: `POST /api/vote/` (JWT required)
- My votes: `GET /api/my-votes/` (JWT required)
- Results: `GET /api/results/<election_id>/`


## Example Data (fixture)

Create a file `example_data.json` in your project root with the following content:

```
[
  {
    "model": "elections.election",
    "pk": 1,
    "fields": {
      "name": "Presidential Election",
      "description": "Vote for the next president!",
      "start_time": "2024-07-01T09:00:00Z",
      "end_time": "2024-07-31T17:00:00Z"
    }
  },
  {
    "model": "elections.candidate",
    "pk": 1,
    "fields": {
      "name": "Alice Smith",
      "election": 1
    }
  },
  {
    "model": "elections.candidate",
    "pk": 2,
    "fields": {
      "name": "Bob Johnson",
      "election": 1
    }
  }
]
```


## Notes
- Use Django admin at `/admin/` to manage users, elections, and candidates.
- JWT tokens are stored in localStorage on the frontend.
- CORS is enabled for development.
- Only authenticated users can vote, and only once per election.
- Results are visible to all users.