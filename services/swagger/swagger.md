# Arclytics SimCCT API
Swagger OpenAPI spec 3 for documenting the simcct and arclytics Flask API microservices

## Version: 2.0.0

### /v1/sim/ping

#### GET
##### Summary:

Just a sanity check

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | You are not crazy. |

### /v1/sim/healthy

#### GET
##### Summary:

Readiness probe for GCP Ingress.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Empty response. |

### /v1/sim/users

#### GET
##### Summary:

Returns all users

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | A list of User objects |
| 400 | An invalid request body has been sent. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user

#### GET
##### Summary:

Returns a user based on a single user ID

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Returns the user object successfully. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### PATCH
##### Summary:

Update the User's details.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | User has been updated successfully and the new user details have been returned. |
| 400 | An invalid request body has been sent. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 418 | There has been some validation error saving to Mongo. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/profile

#### POST
##### Summary:

Create the User's profile details the first time they complete it.

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | The User's profile has been successfully saved. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/users/query

#### GET
##### Summary:

Return all users based on a query.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully returned user. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/users/search

#### GET
##### Summary:

Allows administrators to search the database for a user/users

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully returned user. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/last/simulation

#### GET
##### Summary:

Returns the user's last Alloy and Configurations used, and CCT/TTT results (if any)

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully returned the user's last Alloy and Configurations used. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### POST
##### Summary:

Save user's last Alloy and Configurations used, and CCT/TTT results

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successfully saved the configurations. |
| 400 | An invalid payload has been sent in the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/share/simulation/link

#### POST
##### Summary:

Generate link that can be used to share configurations.

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Link successfully generated. |
| 400 | Invalid payload in request body. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/share/simulation/email

#### POST
##### Summary:

Generate email that can be used to share configurations.

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Link successfully generated. |
| 400 | Invalid payload in request body. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/share/simulation/view/<token>

#### GET
##### Summary:

Generate email that can be used to share configurations.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfull. |
| 400 | Invalid payload in request body. |
| 404 | The user cannot be found. |

### /v1/sim/user/simulation

#### GET
##### Summary:

Retrieve the list of Configurations saved in the User's document.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully logged in |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### POST
##### Summary:

Save the list of Configuration.

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | Successfully saved. |
| 400 | An invalid payload has been sent in the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/simulation/{id}

#### GET
##### Summary:

Retrieve the list of Configurations saved in the User's document.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully retrieved simulation. |
| 400 | Invalid Object Id |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### DELETE
##### Summary:

Delete a saved simulation from saved_simulation.

##### Responses

| Code | Description |
| ---- | ----------- |
| 202 | Delete saved simulation |
| 400 | Invalid Object Id |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/auth/register

#### POST
##### Summary:

Register and create a new user

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | The user has been successfully created and you get an ID back. |
| 400 | Invalid payload in request body. |

### /v1/sim/auth/login

#### POST
##### Summary:

Logs a user in

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully logged in |
| 400 | An invalid payload has been sent in the request. |
| 403 | Unauthorized access. |

### /v1/sim/auth/status

#### GET
##### Summary:

Returns the logged in user's status

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The user's token is currently valid. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/auth/logout

#### GET
##### Summary:

Logs a user out

##### Responses

| Code | Description |
| ---- | ----------- |
| 202 | Successfully logged out |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/reset/password

#### POST
##### Summary:

Request an email for a reset of the user's password with their confirmed email.

##### Responses

| Code | Description |
| ---- | ----------- |
| 202 | The password reset email has been sent. |
| 400 | An invalid request payload has been sent. |
| 401 | The user is not verified and cannot reset their password. |

### /v1/sim/auth/password/reset

#### PUT
##### Summary:

An endpoint for the client to send the new passwords to reset a user's account password.

##### Responses

| Code | Description |
| ---- | ----------- |
| 202 | The password for the user has successfully been reset. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The JWT token has failed. |

### /v1/sim/auth/password/check

#### POST
##### Summary:

An endpoint for password check.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Correct password. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/auth/password/change

#### PUT
##### Summary:

An endpoint for changing password.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Correct password. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/auth/email/change

#### PUT
##### Summary:

An endpoint for changing email.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Email changed successfully. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/confirm/resend

#### GET
##### Summary:

An endpoint for sending confirmation email.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Confirmation email sent. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/confirm/<token>

#### GET
##### Summary:

Confirmation for URL link tokens sent for admin registration verification.

##### Responses

| Code | Description |
| ---- | ----------- |
| 302 | Redirect. |
| 400 | An invalid payload has been sent with the request. |

### /v1/sim/confirm/register/resend

#### PUT
##### Summary:

An endpoint for resending confirmation email.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Resend email |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/confirmadmin/<token>

#### GET
##### Summary:

Confirmation for URL link tokens sent for user registration verification.

##### Responses

| Code | Description |
| ---- | ----------- |
| 302 | Redirect. |

### /v1/sim/reset/password/confirm/<token>

#### GET
##### Summary:

Decode the token from the email to the confirm right person.

##### Responses

| Code | Description |
| ---- | ----------- |
| 302 | Redirect. |

### /v1/sim/admin/create

#### POST
##### Summary:

Create an admin account.

##### Responses

| Code | Description |
| ---- | ----------- |
| 202 | Admin successfully created. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/admin/create/cancel/<token>

#### GET
##### Summary:

Allow an admin to cancel their promotion of another user

##### Responses

| Code | Description |
| ---- | ----------- |
| 302 | Redirect. |

### /v1/sim/admin/create/verify/<token>

#### GET
##### Summary:

Allow a user to acknowledge their promotion and in doing so verify their status as an admin

##### Responses

| Code | Description |
| ---- | ----------- |
| 302 | Redirect. |

### /v1/sim/disable/user

#### PUT
##### Summary:

Disable a User's account if an Admin has requested.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The user has been successfully disabled. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/disable/user/confirm/<token>

#### GET
##### Summary:

Send confirmation to disable user account if an Admin has requested.

##### Responses

| Code | Description |
| ---- | ----------- |
| 302 | Redirect. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/enable/user

#### PUT
##### Summary:

Disable a User's account if an Admin has requested.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The user has been successfully enabled. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/global/alloys

#### POST
##### Summary:

Create a new alloy and store it in the Alloys database.

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | An alloy has been successfully created and stored in the database. |
| 400 | An invalid payload has been sent. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 412 | The name is not a unique value. |
| 500 | An internal server error has occurred. |

#### GET
##### Summary:

The full list of Alloys from the database.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The request has been successful and there is data to respond with. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

### /v1/sim/global/alloys/{id}

#### GET
##### Summary:

Get a single alloy from the Alloys database.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path | An ObjectId of an existing Alloy in the database. | Yes | string (bytes) |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The request has been successful. |
| 400 | Invalid payload sent in the request body. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

#### PUT
##### Summary:

Update a single existing Alloy.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path | An ObjectId of an existing Alloy in the database. | Yes | string (bytes) |

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The request was successful and the updated Alloy is returned. |
| 400 | An invalid payload has been sent. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

#### DELETE
##### Summary:

Delete a single alloy by ID.

##### Parameters

| Name | Located in | Description | Required | Schema |
| ---- | ---------- | ----------- | -------- | ---- |
| id | path | An ObjectId of an existing Alloy in the database. | Yes | string (bytes) |

##### Responses

| Code | Description |
| ---- | ----------- |
| 202 | Your request was successfully completed. |
| 400 | An invalid request parameter has been sent. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

### /v1/sim/user/alloys

#### POST
##### Summary:

Save an alloy to the User's database.

##### Responses

| Code | Description |
| ---- | ----------- |
| 201 | The Alloy has been saved to the User's Alloys database. |
| 400 | An invalid request body has been sent. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### GET
##### Summary:

We get the list of User's alloys stored in their document.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Return the User's Alloys database successfully. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/alloys/{id}

#### GET
##### Summary:

We get the requested alloy from the parameter's ObjectId.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Return the User's alloy detail successfully. |
| 400 | An invalid request body has been sent. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 418 | Multiple objects have been returned from the query. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### PUT
##### Summary:

Update an alloy to the User's database.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The alloy has been successfully updated and returned in the response. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | There are no alloys saved to the user's document or user to find. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### DELETE
##### Summary:

Delete an alloy from the user's database.

##### Responses

| Code | Description |
| ---- | ----------- |
| 202 | An alloy has successfully been deleted. |
| 400 | The request has an invalid request parameter. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | There are no alloys saved to the user's document or user to find. |
| 418 | Multiple objects have been returned from the query. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/alloys/update

#### POST
##### Summary:

Initiate an Alloy and Configuration Session store.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The alloy and its compositions was successfully updated and stored in the Session for the user. An initial Configurations with default values were set. |
| 400 | An invalid request has been made. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/configs/ms

#### POST
##### Summary:

Initiate calculation for MS.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The auto calculate for MS store has been updated and returned. |
| 400 | An invalid request has been made. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/configs/bs

#### POST
##### Summary:

Initiate calculation for BS.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The auto calculate for BS store has been updated and returned. |
| 400 | An invalid request has been made. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/configs/ae

#### POST
##### Summary:

Initiate calculation for Ae.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The auto calculate for Ae store has been updated and returned. |
| 400 | An invalid request has been made. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/simulate

#### POST
##### Summary:

Run the simulation and get the results back.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The CCT and TTT simulations have been completed and the Graphs result returned. |
| 400 | An invalid request has been made. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/ae3equilibrium

#### POST
##### Summary:

Run the Ae3Simulation and get the results back.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Ae3 Equilibrium ran successfully. |
| 400 | An invalid request has been made. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/rating

#### POST
##### Summary:

Create ratings.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The User rating has been successfully saved. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/feedback

#### GET
##### Summary:

Return a list of feedback based of get request from Admin

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The User rating has been successfully saved. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

#### POST
##### Summary:

Method to post feedback.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | The User rating has been successfully saved. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/feedback/search

#### GET
##### Summary:

Return a list of feedback based of get request from Admin

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully returned feedback. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |

### /v1/sim/user/feedback/list/subscribe

#### POST
##### Summary:

Route for Admins to subscribe to the feedback mailing list.

##### Responses

| Code | Description |
| ---- | ----------- |
| 200 | Successfully subscribed. |
| 400 | An invalid payload has been sent with the request. |
| 401 | The user is not authenticated to perform this request. |
| 403 | Unauthorized access. |
| 404 | The user cannot be found. |
| 500 | An internal server error has occurred. |

##### Security

| Security Schema | Scopes |
| --- | --- |
| cookieAuth | |
