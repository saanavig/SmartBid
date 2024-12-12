# **SmartBid**  
A **Secure and Efficient E-Bidding System** that empowers users to list, bid on, buy, and sell items seamlessly. The platform supports multiple user roles with unique permissions and behaviors, making it a comprehensive solution for e-commerce.  

---

## **Overview**  
SmartBid offers a robust set of features for visitors, users, and super-users:  

### **Visitor Capabilities**  
- Browse and comment on listings.  
- Apply to become a User, with validation (e.g., random arithmetic question).  

### **User Capabilities**  
- Deposit/withdraw money from their account.  
- List items or services for sale or rent.  
- Bid on items within their budget.  
- Accept or reject bids.  
- Rate buyers/renters anonymously.  
- File complaints with Super-Users.  

### **Super-User Capabilities**  
- Approve or reject applications for Users.  
- Suspend Users based on ratings or violations.  
- Reactivate Users upon payment of fines or other conditions.  

### **Rating System**  
- Users can rate each other anonymously after completing a transaction.  
- Suspended Users can be reactivated by paying a fine or through Super-User intervention.  

### **VIP Features**  
- High-balance or frequent-transacting Users become VIPs, enjoying:  
  - 10% discount on transactions.  
  - Exemption from suspension under certain conditions.  
- VIPs have all User rights with additional privileges.  

### **Complaint Management**  
- Users can file complaints against others.  
- Super-Users resolve complaints and suspend Users based on violation severity.  

### **Graphical User Interface (GUI)**  
- Personalized dashboard for Users to:
  - View transaction history.
  - Check account details.
  - Track pending actions.

---

## **Tech Stack**  

### **Backend**  
- **Django**: Backend logic, user authentication, and database management.  
- **Supabase**: Real-time data handling, user management, and storing listings.  

### **Frontend**  
- **HTML/CSS**: User interface design with responsive layouts.  
- **JavaScript**: Enhances interactivity, especially in bidding features and real-time updates.  

---

## **Contributors**  

Sehr Abrar, Srewashi Mondal, Saanavi Goyal, Debasree Sen

---

## **Requirements**  

To run this system locally or in production, ensure the following are installed:

- **Python 3.x**: Required for the backend.  
- **Django**: Framework for backend logic and database management.  
- **Supabase Account**: Required for database management and storing listings.  
- **PostgreSQL**: Used as the database (compatible with Django's ORM).  

### **Python Packages**  
This project requires the following Python packages:

- Django 4.2.16  
- django-allauth 65.3.0  
- djangorestframework 3.15.2  
- exceptiongroup 1.2.2  
- load-dotenv 0.1.0  
- psycopg-binary 3.1.18  
- psycopg2 2.9.10  
- python-dotenv 1.0.1  
- supabase 2.10.0  
- urllib3 2.2.3  

Install the required Python packages using `pip` from the `requirements.txt` file:
`bash pip install -r requirements.txt`

---

