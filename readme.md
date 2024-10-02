# Movie API Documentation

## Overview

This is a simple Movie API that allows you to perform operations related to movies, such as retrieving a list of movies, adding a new movie, or deleting a movie. Additionally, it includes functionality to register and log in users.

## API Information

- **API Version**: 1.0.0
- **Base URL**: `http://localhost:8000`

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
   - **404 Not Found**: No movie found with the given ID.

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
