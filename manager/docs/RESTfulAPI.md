# RESTful API Documentation for ConfigDistributor

This is the documentation for RESTful API of ConfigDistributor.

## Authentication

We use Token Authentication for this API. 

For clients to authenticate, the token key should be included in the `Authorization` HTTP header. The key should be prefixed by the string literal "Token", with whitespace separating the two strings. For example:

```http
Authorization: Token f30c6afdb076abbee13dc056e59017d3
```

You can get token by generating token from the web page `http://hostname/web/auth/token/generate/`, or use username and password to get token from RESTful API `http://hostname/api/login/` using POST http method like:

```bash
$ curl -X POST -d "username=username&password=userpassword" http://localhost:8000/api/login/
{"token":"f32231692ece3d61bc385cb67f66ecca"}
```

If request has no username or no password will get:

```json
{"error":"Please provide both username and password"}
```

If with invalid username or password you will get:

```json
{"error":"Invalid Credentials"}
```

## Configs/Agents/Tasks/Users

Configs is the data of config file, agents is the data of servers, tasks is the data of tasks, and users is the data of users.

### Configs

Get all data of configs:

```http
GET /api/configs/
```

```json
[
    {
        "id":1,
        "name":"shadowsocks",
        "status":"Normal",
        "contents":"test_config_data",
        "create_time":"2018-10-01T21:13:28.820611+08:00",
        "description":"test config file",
        "path":"/home/test/config.json",
        "is_deleted":false
    },
    {
        "id":2,
        "name":"nginx",
        "status":"Disabled",
        "contents":"test_config_data",
        "create_time":"2018-10-05T14:35:19.858964+08:00",
        "description":"test config",
        "path":"/etc/test/test.conf",
        "is_deleted":false
    }
]
```

Get config data by id:

```http
GET /api/configs/1/
```

```json
{
    "id":1,
    "name":"shadowsocks",
    "status":"Normal",
    "contents":"test_config_data",
    "create_time":"2018-10-01T21:13:28.820611+08:00",
    "description":"test config file",
    "path":"/home/test/config.json",
    "is_deleted":false
}
```

Create new config:

```http
POST /api/configs/
{
    "name": "test new config",
    "status": "Normal",
    "contents": "test data contents",
    "description": "a new test config",
    "path": "/home/test/test.txt"
}
```

```json
{
    "name": "test new config",
    "status": "Normal",
    "contents": "test data contents",
    "description": "a new test config",
    "path": "/home/test/test.txt"
}
```

Update data of config by id:

```http
PUT /api/configs/1/
{
    // new data
}
```

```json
{
    // data after updating
}
```

Delete data of config by id:

```http
DELETE /api/configs/1/
```

```json
// empty json
```

## Create New Task

### TEST

This task is used for test servers' connection:

```http
POST /api/new_task/
{
    "type": "TEST",
    "client_list": [
        {
            "id": 1,
            "ip_address": "192.168.1.3"
        },
        {
            "id": 2,
            "ip_address": "192.168.2.1"
        }
    ]
}
```

```json
{
    "id": 1
}
```

If task created successfully, server will return a json data with the task id, then you can view the task status via `/api/tasks/<id>/`

### GET

This task is used for pull config files from servers.

```http
POST /api/new_task/
{
    "type": "GET",
    "client_list": [
        {
            "id": 1,
            "ip_address": "192.168.1.2"
        },
        {
            "id": 2,
            "ip_address": "123.123.123.123"
        }
    ],
    "remote_path": [
        "/etc/nginx/sites-enabled/default.conf",
        "/etc/shadowsocks/config.json"
    ]
}
```

```json
{
    "id": 1
}
```

If task created successfully, server will return a json data with the task id, then you can view the task status via `/api/tasks/<id>/`

### POST

This task is used for distributing config files to servers.

```http
POST /api/new_task/
{
    "type": "POST",
    "client_list": [
        {
            "id": 1,
            "ip_address": "192.168.1.2",
        },
        {
            "id": 2,
            "ip_address": "123.123.123.123",
        }
    ],
    "file_list": [
        {
            "remote_path": "/etc/nginx/sites-enabled/default.conf",
            "file_content_b64": "<plain text>"
        },
        {
            "remote_path": "/etc/nginx/sites-enabled/default.conf",
            "file_content_b64": "<plain text>"
        },
    ]
}
```

```json
{
    "id": 1
}
```

If task created successfully, server will return a json data with the task id, then you can view the task status via `/api/tasks/<id>/`