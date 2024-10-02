# Movie API Documentation

## Overview

This is a simple Movie API that allows you to perform operations related to movies, such as retrieving a list of movies, adding a new movie, or deleting a movie. Additionally, it includes functionality to register and log in users.

## API Information

- **API Version**: 1.0.0
- **Base URL**: https://brite-test-388527781986.us-central1.run.app
- **Swagger**: https://app.swaggerhub.com/apis/ROBERTOAMENEIROS/movie-api/1.0.0#/

---

## Endpoints

### 1. **Retrieve a List of Movies**
   - **Endpoint**: `/movies`
   - **Method**: `GET`
   - **Description**: Retrieves a paginated list of movies with options to filter by title, year, movie type, or IMDb ID.
   
   #### Query Parameters:
   | Parameter   | Type   | Description                                 | Default Value | Example        |
   |-------------|--------|---------------------------------------------|---------------|----------------|
   | `limit`     | `int`  | Number of movies to return per page         | 10            | `limit=5`      |
   | `page`      | `int`  | Page number for pagination                  | 1             | `page=2`       |
   | `order_by`  | `enum` | Field to order results by (`title`, `year`, `movie_type`) | `title`        | `order_by=year`|
   | `title`     | `string` | Filter movies by title                     |               | `title=Inception` |
   | `year`      | `string` | Filter movies by release year              |               | `year=2010`    |
   | `movie_type`| `string` | Filter movies by movie type                |               | `movie_type=Action` |
   | `imdb_id`   | `string` | Filter movies by IMDb ID                   |               | `imdb_id=tt1375666`|

   #### Responses:
   - **200 OK**: A successful response containing the list of movies.
   - **400 Bad Request**: The request contains invalid query parameters.
   - **404 Not Found**: No movies found.

   #### Notes:
- You can set how many records are returned in a single API response, with a default of 10.
- Pagination is implemented in the backend to navigate through the list of movies.
- By default, data is ordered by title.
- There is no dedicated endpoint to search for a movie by title. Instead, you can filter the list of movies using the `title` query parameter in the GET request to the `/movies` endpoint. This decision was made because multiple movies may share the same title.
---

### 2. **Add a New Movie**
   - **Endpoint**: `/movies`
   - **Method**: `POST`
   - **Description**: Adds a new movie to the database.
   
   #### Request Body:
   ```json
   {
     "title": "string"
   }
   ```

   #### Responses:
   - **201 Created**: Movie successfully added.
   - **400 Bad Request**: The request body is missing required fields.
   - **404 Not Found**: Movie not found in OMDB.
   - **409 Conflict**: The movie is already registered in the database.

   #### Notes:
   - The title of the movie must be provided in the request. Upon adding the movie, the API fetches all relevant movie details from the OMDB API and saves them in the database.

---

### 3. **Get a Movie by ID**
   - **Endpoint**: `/movies/{movie_id}`
   - **Method**: `GET`
   - **Description**: Retrieves a movie by its unique ID.
   
   #### Path Parameters:
   | Parameter   | Type   | Description                |
   |-------------|--------|----------------------------|
   | `movie_id`  | `int`  | The ID of the movie to retrieve |

   #### Responses:
   - **200 OK**: Movie details are returned.
   - **404 Not Found**: No movie found with the given ID.

---

### 4. **Delete a Movie by ID**
   - **Endpoint**: `/movies/{movie_id}`
   - **Method**: `DELETE`
   - **Description**: Deletes a movie from the database by its unique ID.
   
   #### Path Parameters:
   | Parameter   | Type   | Description                |
   |-------------|--------|----------------------------|
   | `movie_id`  | `int`  | The ID of the movie to delete |

   #### Responses:
   - **204 No Content**: Movie successfully deleted.
   - **401 Unauthorized**: Authentication token is missing or invalid.
   - **404 Not Found**: No movie found with the given ID.
#### Notes:
   - This endpoint is protected and requires authentication. Only authorized users can perform this action.
---

### 5. **Register a New User**
   - **Endpoint**: `/register`
   - **Method**: `POST`
   - **Description**: Registers a new user with a username and password.
   
   #### Request Body:
   ```json
   {
     "username": "string",
     "password": "string"
   }
   ```
   #### Responses:
   - **204 No Content**: 201 Created: User successfully registered.
   - **400 Bad Request**: Invalid input (e.g., missing fields).
   - **409 Conflict**: Username already exists.


---

### 6. **Login an Existing User**
   - **Endpoint**: `/login`
   - **Method**: `POST`
   - **Description**: Logs in an existing user and returns a token for authentication.
   
   #### Request Body:
   ```json
   {
     "username": "string",
     "password": "string"
   }
   ```
   #### Responses:
   - **200 Ok**: Login successful. Returns an authentication token.
   - **400 Bad Request**: Invalid input (e.g., missing fields).
   - **401 Unauthorized**: Invalid credentials.

---

## Authentication

To authenticate a user, you need to use the `/login` endpoint. Upon a successful login, you will receive a token that must be included in the `Authorization` header for all protected endpoints.

### Example:
```http
Authorization: Bearer <your_token_here>
```

--

## Database Initialization

When the Movie API starts, it initializes the database by creating a table for movies and populating it with unique movie data. Here's a brief overview of how this process works:

1. **Check for Existing Movies**:
   - The API checks if the movies table is empty. If it is, it proceeds to fetch a list of unique movies.

2. **Fetch Unique Movies**:
   - The API retrieves movie data from a predefined list of movie titles specified in the `MOVIES_TITLES_DEFAULT` variable. This variable contains a comma-separated string of movie titles. The API fetches movie data from an external movie database API (like OMDB) until it has gathered a set number of unique movies.

3. **Insert Movies into Database**:
   - Once the unique movies are fetched, they are inserted into the database for use by the API.

This process ensures that when you start the API, there will be movies available to retrieve.


## Services Used

- **Google Cloud Run**: The API is deployed using Google Cloud Run.
- **Database**: Instead of using Cloud SQL due to associated costs and the lightweight nature of the test, SQLite was chosen as the database solution.




## Environment Variables
   To run the application, you need to define some environment variables. Below are the required variables:
   
   - **OMDB_API_KEY**: (required) Your API key to access the OMDB database.
   
   - **SECRET_KEY**: (required) A secret key used for authentication and token 
   signing. 
   
   - MOVIE_TITLES: (optional) A comma-separated list of movie titles. If not 
   set, the application will use default values