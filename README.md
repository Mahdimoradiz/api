# 🚀 Nex Backend

Welcome to **Nex Backend**, the powerful core of our social networking platform! Built with **Django** and **Django REST Framework (DRF)**, this backend provides a robust and scalable API for managing users, posts, likes, comments, and more.

---

## 📌 Features

| Feature               | Description |
|----------------------|-------------|
| ✅ **JWT Authentication** | Secure login, signup, and token-based authentication |
| ✅ **Post Management** | Upload, edit, and delete posts (Images/Videos) |
| ✅ **Like & Comment System** | Users can interact with posts |
| ✅ **Follow/Unfollow System** | Connect with other users |
| ✅ **Smart Categorization** | Posts are automatically categorized |
| ✅ **High-Quality Media Support** | Premium users can upload 4K+ content |
| ✅ **Optimized API** | Fast and efficient response times |
| ✅ **Admin Panel** | Fully customized admin interface |

---

## 🛠 Installation & Setup

### 1️⃣ **Clone the Repository**
```bash
git clone https://github.com/yourusername/nex-backend.git
cd nex-backend
```

### 2️⃣ **Create & Activate Virtual Environment**
```bash
python -m venv env
source env/bin/activate  # macOS/Linux
env\Scripts\activate  # Windows
```

### 3️⃣ **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4️⃣ **Apply Migrations**
```bash
python manage.py migrate
```

### 5️⃣ **Create a Superuser (Admin Panel Access)**
```bash
python manage.py createsuperuser
```

### 6️⃣ **Run the Development Server**
```bash
python manage.py runserver 0.0.0.0:8000
```

---

## 🔥 API Endpoints

### **Authentication**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/register/` | Register a new user |
| `POST` | `/api/auth/login/` | Login and obtain a JWT token |
| `POST` | `/api/auth/logout/` | Logout the user |

### **User Management**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/{username}/` | Retrieve user profile |
| `POST` | `/api/users/follow/{username}/` | Follow a user |

### **Posts**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/posts/` | Get all posts |
| `POST` | `/api/posts/create/` | Create a new post |
| `DELETE` | `/api/posts/{id}/` | Delete a post |

### **Likes & Comments**
| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/posts/{id}/like/` | Like a post |
| `POST` | `/api/posts/{id}/comment/` | Add a comment |

---

## 🔐 Security & Authentication
- Uses **JWT Authentication** for user sessions.
- **Role-Based Access Control (RBAC)** for different user levels.
- Secure **API Rate Limiting** to prevent abuse.

---

## 🚀 Upcoming Features

| Feature | Status |
|---------|--------|
| 🔜 Live Streaming | Coming Soon |
| 🔜 Push Notifications | Coming Soon |
| 🔜 Direct Messaging | Coming Soon |
| 🔜 AI-Powered Post Recommendations | Coming Soon |
| 🔜 Stories Feature | Coming Soon |

---

## 💻 Tech Stack
| Technology | Purpose |
|------------|---------|
| **Django** | Backend Framework |
| **Django REST Framework** | API Development |
| **PostgreSQL** | Database |
| **Celery + Redis** | Background Tasks |
| **JWT Authentication** | Secure Authentication |

---

## 🤝 Contributing

We welcome contributions from the community! Feel free to submit a **Pull Request (PR)** or open an **Issue**.

### 🛠 Contribution Steps
1. Fork the repo & create a new branch.
2. Make your changes and ensure everything works.
3. Submit a **Pull Request (PR)** for review.

---

## 📌 Contact & Support

📧 **Email:** support@nex.com  
💬 **Telegram:** @nexsupport  
📸 **Instagram:** @nex.app  

**❤️ Thanks for supporting Nex! Let's build something amazing! 🚀🔥**

