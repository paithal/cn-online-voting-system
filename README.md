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

