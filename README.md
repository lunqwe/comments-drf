# Comments functionality

In this project I implemented live-time comments functionality that could be reused for different needs (e.g. social-network project, blog, etc.) 

## Instructions

1. **Running the Application:**
   - To get the project files, use the following command:
     ```
     git clone https://github.com/lunqwe/dZENcode-task
     ```
   - To run the project, use the following command (Docker required):
     ```
     docker-compose up --build
     ```

3. **API Documentation:**
   - API documentation can be accessed via [localhost:8000/swagger/](http://localhost:8000/swagger/) (for local server) or [http://13.60.84.5:8000/swagger/](http://13.60.84.5:8000/swagger/) (project deployed on server).

## Project Description

The main page demonstrates WebSocket functionality and provides a form for creating comments. When you create a comment, Websocket would display them.

### Application: accounts

This application handles user authentication using JWT. It includes:
- User login and registration
- Retrieving user by ID
- Updating user information (PUT/PATCH)

### Application: comments

This application implements comment functionality, including:
- WebSocket for continuous server connection
- Endpoints for creating new comments and updating existing ones

Both applications also use Celery tasks for creating a queue of worker processes.


