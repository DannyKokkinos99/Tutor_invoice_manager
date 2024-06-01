# Tutor Invoice Manager

Tutor Invoice Manager is a web application designed to help tutors manage their students' invoices efficiently. This application allows tutors to create, manage, and send invoices to their students, track payment statuses, and generate financial reports.

## Mockups

<div id="slideshow">
    <img src="static/screenshots/landing_page.JPG" class="slide" style="display: none;">    
    <img src="static/screenshots/add_student.JPG" class="slide" style="display: block;">
    <img src="static/screenshots/invoice_inspector.JPG" class="slide" style="display: none;">
</div>

<style>
#slideshow {
    position: relative;
    width: 100%;
    max-width: 600px;
    margin: auto;
}
.slide {
    position: absolute;
    width: 100%;
}
</style>

<script>
let currentSlide = 0;
const slides = document.querySelectorAll('#slideshow .slide');

function showSlide(index) {
    slides[currentSlide].style.display = 'none';
    currentSlide = (index + slides.length) % slides.length;
    slides[currentSlide].style.display = 'block';
}

function nextSlide() {
    showSlide(currentSlide + 1);
}

setInterval(nextSlide, 3000);
</script>

## Features

- **Add**: Add new student profiles and invoices.
- **Remove**: Remove student profiles and invoices.
- **Edit**: Edit existing student profiles and invoices.
- **Create Invoice**: Generate invoices for individual students or groups.
- **Automatic Emailer**: Send email notifications for invoice status updates automatically.

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- [Python](https://www.python.org/downloads/) (version X.X.X)
- [pip](https://pip.pypa.io/en/stable/installation/) (version X.X.X)
- [MongoDB](https://www.mongodb.com/) (or any other preferred database)

### Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/tutor-invoice-manager.git
    cd tutor-invoice-manager
    ```

2. **Create a virtual environment:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables:**

    Create a `.env` file in the root directory and add the following:

    ```env
    DATABASE_URL=your_database_url
    SECRET_KEY=your_secret_key
    EMAIL_SERVICE=your_email_service
    EMAIL_USER=your_email_user
    EMAIL_PASS=your_email_password
    ```

5. **Run database migrations (if applicable):**

    ```bash
    python manage.py migrate
    ```

6. **Start the application:**

    ```bash
    python manage.py runserver
    ```

    The application will run on `http://localhost:8000`.

### Running Tests

To run tests, use the following command:

```bash
python -m unittest discover
