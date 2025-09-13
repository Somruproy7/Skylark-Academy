🎓 Skylark Academy - University Registration System

[!Django](https://www.djangoproject.com/)
[!MySQL](https://www.mysql.com/)
[!Python](https://www.python.org/)
[!Bootstrap](https://getbootstrap.com/)
[!License](LICENSE)

A comprehensive, modern university registration and management system built with Django and MySQL. Designed to streamline academic operations for educational institutions of all sizes.

!Skylark Academy Dashboard

🌟 Key Features

🎯 Core Functionality
•  Student Management - Complete student lifecycle from registration to graduation
•  Course Management - Multi-discipline course catalog with flexible credit systems  
•  Module Registration - Intelligent eligibility checking and real-time enrollment
•  Academic Tracking - Progress monitoring and credit accumulation
•  Admin Dashboard - Comprehensive analytics and management tools

🚀 Advanced Features
•  Auto-Setup System - Automatic database creation, migrations, and sample data
•  Multi-Platform Deployment - Ready for Azure, GCP, Heroku, and local hosting
•  Real-time Analytics - Enrollment trends, geographic distribution, performance metrics
•  Bulk Operations - CSV import/export, batch processing, mass updates
•  Audit Logging - Complete activity tracking for compliance and security

🎨 User Experience
•  Responsive Design - Mobile-first, Bootstrap-based interface
•  Modern UI - Clean, intuitive navigation with professional aesthetics
•  Smart Search - Advanced filtering and search across all entities
•  Role-based Access - Secure, permission-based user management

📸 Screenshots

<details>
<summary>Click to view screenshots</summary>

Home Page
!Home Page

Module Catalog
!Module Catalog

Admin Dashboard
!Admin Dashboard

Student Profile
!Student Profile

</details>

🚀 Quick Start

Prerequisites

•  Python 3.8+ 
•  MySQL 5.7+ or 8.0+
•  Git

Installation

1. Clone the repository
bash
2. Install dependencies
bash
3. Configure environment variables

   Create a .env file in the project root:
env
4. Start the application
bash
That's it! 🎉 The system will automatically:
•  Create the MySQL database
•  Run all migrations
•  Populate sample data (10 courses, 15 modules)
•  Start the development server at http://127.0.0.1:8000

🪟 Windows Quick Start

For Windows users, use the included convenience scripts:

PowerShell:
pwsh
Command Prompt:
cmd
📊 System Architecture

Database Schema
mermaid
Technology Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| Backend | Django 5.2.5 | Web framework & API |
| Database | MySQL 8.0+ | Data persistence |
| Frontend | Bootstrap 5.3 | Responsive UI |
| Authentication | Django Auth | User management |
| Deployment | Docker, Azure, GCP, Heroku | Multi-platform hosting |

🎯 Usage Guide

For Students
1. Register - Create your account and complete profile
2. Enroll - Choose your degree program
3. Browse - Explore available modules by category
4. Register - Sign up for modules that match your course
5. Track - Monitor your progress and credits

For Administrators
1. Dashboard - Access comprehensive analytics at /admin/dashboard/
2. Manage - Add/edit courses, modules, and students
3. Monitor - Track enrollments and system usage
4. Export - Generate reports and data exports
5. Audit - Review system activity logs

📚 API Endpoints

Public Endpoints
•  GET /api/modules/ - List all available modules
•  GET /api/external/ - External data integration

Admin Endpoints
•  GET /admin/dashboard/ - System analytics
•  GET /admin/reports/ - Generated reports
•  GET /admin/audit-logs/ - Activity logs

🔧 Configuration

Environment Variables
| Variable | Description | Default |
|----------|-------------|---------|
| DB_NAME | MySQL database name | skylark_academy |
| DB_USER | MySQL username | root |
| DB_PASSWORD | MySQL password | required |
| DB_HOST | MySQL host | localhost |
| DB_PORT | MySQL port | 3306 |
| AUTO_POPULATE_DB | Auto-load sample data | false |
| DEBUG | Debug mode | False |

Sample Data
When AUTO_POPULATE_DB=true, the system includes:
•  10 Academic Courses (Computer Science, Engineering, Business, etc.)
•  15 Learning Modules (Programming, Calculus, Design, etc.)
•  User Groups for role-based access
•  Admin Audit System ready for use

🚀 Deployment

Local Development
bash
Production Deployment

<details>
<summary>Azure Deployment</summary>
bash
</details>

<details>
<summary>Docker Deployment</summary>
dockerfile
</details>

<details>
<summary>Heroku Deployment</summary>
bash
</details>

🧪 Testing

Run the test suite:
bash
Generate test coverage:
bash
📈 Performance

•  Database: Optimized MySQL queries with proper indexing
•  Frontend: Compressed static files, lazy loading
•  Caching: Redis integration ready
•  Monitoring: Built-in audit logging and analytics

🤝 Contributing

We welcome contributions! Please see our Contributing Guide for details.

1. Fork the repository
2. Create a feature branch (git checkout -b feature/amazing-feature)
3. Commit changes (git commit -m 'Add amazing feature')
4. Push to branch (git push origin feature/amazing-feature)
5. Open a Pull Request

📋 Project Structure
📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

👥 Team

•  Lead Developer - Your Name
•  UI/UX Design - Modern, responsive interface
•  Database Design - Optimized MySQL schema
•  DevOps - Multi-platform deployment ready

🙏 Acknowledgments

•  Django Software Foundation for the excellent web framework
•  Bootstrap team for the responsive UI components
•  MySQL for reliable database performance
•  The open-source community for inspiration and support

📞 Support

•  Documentation: Wiki Pages
•  Issues: GitHub Issues
•  Discussions: GitHub Discussions



<div align="center">

⭐ Star this repository if you find it helpful! ⭐

Made with ❤️ for educational institutions worldwide

📚 Documentation | 🚀 Live Demo | 🐛 Report Bug

</div>
