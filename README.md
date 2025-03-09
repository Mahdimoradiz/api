# nex-server
🚀 Nex Backend - The Power Behind Our Social Network!
Welcome to Nex Backend! 🎉 This is the core engine of our fast, secure, and scalable social network. Built with Django and Django REST Framework (DRF), it provides a powerful API for managing users, posts, likes, comments, and more.

⚡ Key Features
✅ JWT Authentication (Signup, Login, Password Reset)
✅ Post Upload & Management (Images, Videos, Captions, etc.)
✅ Like & Comment System for user interactions
✅ Follow/Unfollow System to connect users
✅ Smart Post Categorization without user input
✅ Support for High-Quality Media (For premium users)
✅ Optimized API for speed & efficiency
✅ Live Streaming (Coming Soon!)

🚀 Installation & Setup
1. Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/nex-backend.git
cd nex-backend
2. Create & Activate Virtual Environment
bash
Copy
Edit
python -m venv env
source env/bin/activate  # macOS/Linux
env\Scripts\activate  # Windows
3. Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
4. Apply Migrations
bash
Copy
Edit
python manage.py migrate
5. Create a Superuser (Admin Panel Access)
bash
Copy
Edit
python manage.py createsuperuser
6. Run the Development Server
bash
Copy
Edit
python manage.py runserver 0.0.0.0:8000
🔥 API Endpoints
📌 Authentication
🔹 POST /api/auth/register/ → Register a new user
🔹 POST /api/auth/login/ → Login & obtain a token
🔹 POST /api/auth/logout/ → Logout user

📌 User Management
🔹 GET /api/users/{username}/ → Get user profile
🔹 POST /api/users/follow/{username}/ → Follow a user

📌 Posts
🔹 GET /api/posts/ → Get all posts
🔹 POST /api/posts/create/ → Create a new post
🔹 DELETE /api/posts/{id}/ → Delete a post

📌 Likes & Comments
🔹 POST /api/posts/{id}/like/ → Like a post
🔹 POST /api/posts/{id}/comment/ → Add a comment

🔐 Authentication & Security
JWT Authentication ensures user security.
APIs are designed to keep user data safe and protected.
Rate Limiting will be added soon to prevent abuse.
📌 Upcoming Features
✅ Live Streaming for Users
✅ Push Notifications for New Activity
✅ Direct Messaging & Chat System
✅ AI-Powered Post Recommendations
✅ Stories Feature

🛠 Tech Stack
🔹 Django & Django REST Framework
🔹 PostgreSQL (or SQLite for development)
🔹 Celery + Redis for background tasks
🔹 JWT Authentication for user security

🤝 Contributing
Want to help? Feel free to submit a Pull Request (PR) or open an Issue! 😊

📌 Contact Us:
🔹 Email: support@nex.com
🔹 Telegram: @nexsupport
🔹 Instagram: @nex.app

❤️ Thank you for supporting Nex! Let’s build something great! 🚀🔥
