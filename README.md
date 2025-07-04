---

# 💧 Water Quality Analysis Backend

A backend service built with **FastAPI** for analyzing and predicting water quality. This system provides RESTful APIs to handle data measurement, machine learning predictions, report generation, and user authentication.

---

## 🚀 Features

* 🔍 **Water Quality Prediction** using trained ML models
* 🌐 **RESTful APIs** for measurements, analysis, and reporting
* 🔐 **JWT-based Authentication** and user management
* 📄 **PDF Report Generation** with analysis summaries
* 📊 **Trend Analysis** and smart recommendations
* 🗃️ **PostgreSQL Database Integration**

---

## 🛠️ Tech Stack

* **Language:** Python 3.8+
* **Framework:** FastAPI
* **ORM:** SQLAlchemy
* **Database:** PostgreSQL
* **ML:** scikit-learn
* **PDF Reports:** reportlab
* **Auth:** JWT

---

## ⚙️ Prerequisites

* Python 3.8 or higher
* PostgreSQL installed and running
* pip or conda for package management

---

## 📦 Installation

1. **Clone the Repository**

   ```bash
   git clone https://github.com/yourusername/water-quality-backend.git
   cd water-quality-backend
   ```

2. **Create a Virtual Environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**

   ```bash
   cp .env.example .env
   ```

   Update `.env` with your custom configuration.

5. **Initialize the Database**

   ```bash
   python init_db.py
   ```

---

## ▶️ Running the Server

Start the FastAPI development server:

```bash
uvicorn main:app --reload
```

Access the API at:
**[http://localhost:8000](http://localhost:8000)**

---

## 📚 API Documentation

* **Swagger UI:** `http://localhost:8000/docs`
* **Redoc UI:** `http://localhost:8000/redoc`

---

## 🧱 Project Structure

```
water-quality-backend/
├── api/             # API routes
├── database/        # Models & DB logic
├── models/          # ML models
├── recommender/     # Suggestion engine
├── utils/           # Helper functions
├── tests/           # Unit & integration tests
├── main.py          # Application entry point
├── requirements.txt # Dependencies
└── .env.example     # Sample environment variables
```

---

## 🔐 Environment Configuration

Update the `.env` file with:

```
DATABASE_URL=postgresql://user:password@localhost:5432/water_quality
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

---

## ✅ Running Tests

Run all tests using:

```bash
pytest
```

---

## 🤝 Contributing

We welcome contributions!

1. Fork this repository
2. Create a new feature branch
3. Commit your changes
4. Push your branch
5. Open a Pull Request

---

## 📄 License

Licensed under the **MIT License**. See the `LICENSE` file for more details.

---
