curl -X POST http://localhost:8000/registration/ -H "Content-Type: application/json" -d '{"first_name": "John", "last_name": "Doe", "email": "johnV.staff@example.com", "password": "securepassword123", "confirm_password": "securepassword123"}'

curl -X POST http://localhost:8000/login/ -H "Content-Type: application/json" -d '{ "email": "johnV.staff@exampl
e.com", "password": "securepassword123"}'

 curl -X GET http://localhost:8000/student_profile/  -H "Content-Type: application/json" -H "Cookie: sessionid=3m94s8nsouzztpip9i9p0ztojrjuw7mh"

 curl -X PUT http://localhost:8000/student_profile_update/     -H "Content-Type: application/json"     -H "Cookie: sessionid=1hy8kn8veli5d76w9ttzry2v6ltbcxy4; csrftoken=xQw04AWoID9xdYWvVylUMBn5DTCjwn2m"     -H "X-CSRFToken: xQw04AWoID9xdYWvVylUMBn5DTCjwn2m"     -d '{"username": "farmer", "address": "busia"}'