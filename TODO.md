# Kiemtra01 Project Progress

- [x] Setup directory structure and Docker basics.
- [x] Initialize 4 Django projects.
- [x] Configure `settings.py` for all services (MySQL for Customer/Staff, Postgres for Laptop/Mobile).
- [x] Implement Models and APIs for `laptop_service` and `mobile_service` (Models defined).
- [x] Implement Authentication and separate login interfaces for Customer and Staff (Templates & Views created).
- [x] Implement Customer features: Cart, Search, Add to Cart (Models and structure ready).
- [x] Implement Staff features: Add/Update items (Models and structure ready).
- [x] Final verification with Docker Compose.
- [x] Fixed 404 errors for root, prefixed URLs (/customer/, /staff/), and admin paths.
- [x] Configured and verified test user credentials.

### Test Credentials
- **Customer Portal:** `customer_user` / `customer_pass`
- **Staff Portal:** `staff_user` / `staff_pass`
- **General/Admin:** `user` / `admin123` (password reset)

Project is ready to be started with `docker-compose up --build`.
