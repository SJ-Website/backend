# Django Admin Setup

## Creating a Superuser

To create a Django superuser (admin) account, run the following command from the Backend directory:

```bash
python manage.py createsuperuser
```

You will be prompted to enter:
- Email address (this will be the username)
- Password
- Password confirmation

## Managing User Roles

1. **Access Django Admin Panel**:
   - Start the Django server: `python manage.py runserver`
   - Navigate to: `http://localhost:8000/admin/`
   - Login with your superuser credentials

2. **Managing User Roles**:
   - Go to "Custom users" section
   - Click on any user to edit their profile
   - The "role" field can be changed to:
     - `customer` (default for new users)
     - `owner` (business owners)
     - Any other role you define

3. **User Role Restrictions**:
   - Users **CANNOT** change their own roles through the frontend
   - Role changes can **ONLY** be made through the Django admin panel
   - This ensures proper access control and prevents privilege escalation

## User Fields Available in Admin

- **Basic Info**: Email, Name, Profile Picture
- **Contact**: Phone Number
- **Personal**: Date of Birth, Bio
- **Role & Permissions**: Role, Premium Status, Staff Status
- **Auth0**: Auth0 ID (read-only)

## Default Role Assignment

- New users are automatically assigned the `customer` role when first created
- Admins can promote users to `owner` or other roles as needed
- Role assignments control access to different features in the application
