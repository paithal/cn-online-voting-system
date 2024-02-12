# Online Voting System using Socket Programming

## Computer Networks Mini Project

This mini project implements an Online Voting System using Socket Programming. The system allows users to create accounts, participate in polls, and view results. The operations include:

### Operations
- Create User
  - User ID
  - Username
  - Password
- Login
- Delete User
- Modify Password
- Create Poll
  - Create
  - Modify
- Vote
  - New vote
  - Update vote
- Open/Close Poll (done by admin)
- Display Results
- Logout

*(Add more operations as needed)*

### Database (SQL Tables)

#### User data
- User ID
- Username
- Password

#### Poll (master)
- Poll ID
- Poll Description
- Owner ID
- Status (opened/closed)
- Open Date, Close Date (scheduling)

#### Poll Options
- Poll ID
- Choice ID
- Choice Description

#### Poll Selection (user)
- Poll ID
- User ID
- Choice ID

# Database Schema

## User data Table

| Field      | Type         | Description           |
|------------|--------------|-----------------------|
| User ID    | STR          | Unique user identifier|
| Username   | STR  | User's username       |
| Password   | STR  | User's password       |

## Poll Table

| Field          | Type         | Description                  |
|----------------|--------------|------------------------------|
| Poll ID        | STR          | Unique poll identifier       |
| Poll Description | STR | Description of the poll      |
| Owner ID       | STR          | User ID of the poll owner    |
| Status         | STR  | Poll status (opened/closed)  |
| Open Date      | DATETIME     | Scheduled opening date       |
| Close Date     | DATETIME     | Scheduled closing date       |

## Poll Options Table

| Field          | Type         | Description                  |
|----------------|--------------|------------------------------|
| Poll ID        | STR          | Poll identifier             |
| Choice ID      | STR          | Unique choice identifier     |
| Choice Description | STR | Description of the choice  |

## Poll Selection Table

| Field          | Type         | Description                  |
|----------------|--------------|------------------------------|
| Poll ID        | STR          | Poll identifier             |
| User ID        | STR          | User identifier             |
| Choice ID      | STR          | Selected choice identifier  |


### Message Types

- create_user
- login_user
- delete_user
- update_pwd
- create_poll
- add_choice (admin)
- delete_choice (admin)
- poll_selection (user)
- logout_user

### Message Format


|  |  |  |
|-------------------|-------------------|-------------------|
| MESSAGE TYPE            | REQ/RESP            | ---MESSAGE DATA---            |

