# Change Request Auto-Approver

A comprehensive ITIL-compliant change management system that automatically evaluates and approves low-risk change requests while routing complex changes to manager review. Built with Python Flask and designed to demonstrate business logic modeling, approval workflows, and ITIL best practices.

## 🚀 Features

### Core Functionality
- **Multi-Channel Intake**: Accept change requests via web form, CSV upload, or REST API
- **Auto-Approval Engine**: Intelligent evaluation based on configurable business rules
- **Manager Review Queue**: Complex changes routed for manual approval
- **Audit Trail**: Complete logging of all actions and decisions
- **ITIL Compliance**: Follows ITIL best practices for change management

### Key Components
- **Risk Assessment**: Evaluates impact, downtime, systems affected, and financial cost
- **Scoring System**: Weighted scoring algorithm for approval decisions
- **Dashboard**: Real-time overview of request status and system metrics
- **Responsive UI**: Modern Bootstrap-based interface
- **API Integration**: RESTful endpoints for external system integration

## 📸 Application Screenshots

### Dashboard Overview
The main dashboard provides a comprehensive overview of the change management system:

![Dashboard](screenshots/dashboard.png)

**Features shown:**
- **Statistics Cards**: Real-time counts of Total Requests, Auto Approved, Manager Review, and Pending requests
- **Navigation Sidebar**: Easy access to all system functions including Submit Request, All Requests, Manager Review, Upload CSV, and Approval Rules
- **Recent Requests**: Table showing the most recent change requests with status indicators
- **Quick Actions**: Direct buttons for common tasks like submitting new requests and accessing manager review
- **System Information**: Shows system status including Auto-Approval Engine (Active), ITIL Compliance (Enabled), Audit Logging (Enabled), and API endpoint information

### Submit Change Request Form
The request submission form provides a comprehensive interface for creating new change requests:

![Submit Request Form](screenshots/submit-request.png)

**Features shown:**
- **Comprehensive Form**: All required fields for change request details including title, description, requester information, change type, priority, and impact assessments
- **Auto-Approval Criteria**: Right sidebar showing the criteria used for automatic approval decisions
- **Smart Validation**: Form validation and user guidance
- **Tips Section**: Helpful tips for users to improve their request quality
- **Impact Assessment**: Dropdown selections for business impact, user impact, and financial impact
- **Systems Tracking**: Field to list all affected systems

### Manager Review Queue
The manager review interface shows requests that require manual approval:

![Manager Review Queue](screenshots/manager-review.png)

**Features shown:**
- **Clean Interface**: Shows pending requests count and status
- **Empty State**: Professional empty state when no requests are pending review
- **Request Cards**: When populated, shows detailed request information with approve/reject actions
- **Batch Processing**: Ability to review multiple requests efficiently
- **Audit Integration**: All manager actions are logged for compliance

### Key Interface Elements
- **Responsive Design**: Works seamlessly on desktop and mobile devices
- **Status Indicators**: Color-coded badges for different request statuses (Pending, Auto-Approved, Manager Review, Approved, Rejected)
- **Priority Levels**: Visual indicators for Low, Medium, High, and Critical priority requests
- **Professional Styling**: Clean, modern Bootstrap-based design suitable for enterprise environments

## 📋 Requirements

- Python 3.8+
- Flask 2.3+
- SQLAlchemy
- Pandas (for CSV processing)
- Bootstrap 5 (CDN)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd change-request-auto-approver
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python app.py
   ```

4. **Access the application**
   - Open your browser to `http://localhost:5000`
   - The database will be automatically created on first run
   - Default approval rules will be initialized

## 🏗️ Architecture

### Project Structure
```
change-request-auto-approver/
├── app.py                 # Flask application entry point
├── models.py              # Database models and schemas
├── routes.py              # Web routes and API endpoints
├── approval_engine.py     # Auto-approval business logic
├── utils.py               # Utility functions and initialization
├── requirements.txt       # Python dependencies
├── templates/             # HTML templates
│   ├── base.html         # Base template with navigation
│   ├── dashboard.html    # Main dashboard
│   ├── submit_request.html # Request submission form
│   ├── manager_review.html # Manager approval queue
│   ├── requests_list.html  # All requests listing
│   ├── request_detail.html # Individual request details
│   ├── upload_csv.html    # CSV upload interface
│   └── rules_list.html    # Approval rules display
└── uploads/               # CSV file upload directory
```

### Database Schema

#### ChangeRequest
- Request metadata (ID, title, description, requester)
- Change details (type, priority, systems affected)
- Impact assessment (business, user, financial)
- Approval status and scoring
- Timestamps and audit information

#### ApprovalRule
- Rule configuration (name, description, criteria)
- Thresholds (systems, downtime, financial impact)
- Scoring weights and auto-approval thresholds
- Rule status and metadata

#### AuditLog
- Action tracking (created, approved, rejected)
- User attribution and timestamps
- Detailed change history

## 🎯 Auto-Approval Logic

The system evaluates change requests using a sophisticated scoring algorithm:

### Evaluation Criteria
1. **Systems Affected** (30% penalty if exceeded)
2. **Estimated Downtime** (25% penalty if exceeded)
3. **Financial Impact** (20% penalty if exceeded)
4. **Business Impact Level** (15% penalty if exceeded)
5. **User Impact Level** (15% penalty if exceeded)
6. **Change Type Validation** (10% penalty if not allowed)
7. **Priority Level Check** (10% penalty if not allowed)

### Default Rules
- **Low Impact Standard Changes**: ≤2 systems, ≤30min downtime, ≤$1000 impact
- **Normal Changes**: ≤3 systems, ≤60min downtime, ≤$2500 impact
- **Emergency Changes**: ≤5 systems, ≤120min downtime, ≤$5000 impact (90% threshold)

### Scoring Process
1. Each rule evaluates the request (0-100% score)
2. Scores are weighted and combined
3. Final score compared against highest threshold
4. Auto-approve if threshold met, otherwise queue for review

## 📊 Usage Examples

### Web Interface
1. **Submit Request**: Use the web form to create new change requests
2. **Dashboard**: Monitor system status and recent activity
3. **Manager Review**: Approve or reject queued requests
4. **CSV Upload**: Bulk import requests from spreadsheet

### API Integration
```bash
# Create a new change request
curl -X POST http://localhost:5000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Database index update",
    "description": "Add performance index to user table",
    "requester_name": "John Smith",
    "requester_email": "john@company.com",
    "department": "IT",
    "change_type": "standard",
    "priority": "medium",
    "systems_affected": ["Database Server"],
    "estimated_downtime": 15,
    "business_impact": "low",
    "user_impact": "low",
    "financial_impact": 500
  }'

# Get all requests
curl http://localhost:5000/api/requests

# Filter by status
curl http://localhost:5000/api/requests?status=auto_approved
```

### CSV Format
```csv
title,description,requester_name,requester_email,department,change_type,priority,systems_affected,estimated_downtime,business_impact,user_impact,financial_impact,rollback_plan,testing_plan,maintenance_window
"Update database schema","Add new index","John Smith","john@company.com","IT","standard","medium","Database Server,App Server",15,"low","low",500,"Drop index if issues","Test in staging","Saturday 2AM-4AM"
```

## 🔧 Configuration

### Approval Rules
Modify approval rules in `utils.py` or through the database:
- Adjust thresholds for different change types
- Configure scoring weights
- Set auto-approval percentages
- Enable/disable specific rules

### Application Settings
Configure in `app.py`:
- Database connection string
- Upload directory location
- Secret key for sessions
- Debug mode settings

## 🧪 Testing

### Manual Testing
1. Submit various types of change requests
2. Verify auto-approval logic with different parameters
3. Test manager review workflow
4. Upload CSV files with sample data
5. Check audit trail completeness

### Sample Data
Use the built-in sample CSV generator:
1. Go to Upload CSV page
2. Click "Generate Sample CSV"
3. Upload the generated file to test bulk processing

## 🔒 Security Considerations

- Input validation on all forms and API endpoints
- SQL injection protection via SQLAlchemy ORM
- File upload restrictions (CSV only)
- Audit logging for all actions
- Session management for web interface

## 📈 ITIL Compliance

This system implements ITIL change management best practices:

- **Change Advisory Board (CAB)**: Manager review queue
- **Risk Assessment**: Multi-factor impact evaluation
- **Change Categories**: Standard, Normal, Emergency types
- **Approval Workflows**: Automated and manual approval paths
- **Change Records**: Complete audit trail and documentation
- **Back-out Plans**: Rollback planning requirements

## 🚀 Deployment

### Production Considerations
- Use PostgreSQL or MySQL instead of SQLite
- Configure proper logging and monitoring
- Set up SSL/TLS encryption
- Implement authentication and authorization
- Configure backup and recovery procedures
- Set up load balancing for high availability

### Environment Variables
```bash
export FLASK_ENV=production
export DATABASE_URL=postgresql://user:pass@localhost/changedb
export SECRET_KEY=your-production-secret-key
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For questions or issues:
1. Check the documentation above
2. Review the code comments
3. Submit an issue on GitHub
4. Contact the development team

## 🎯 Skills Demonstrated

This project showcases:
- **Business Logic Modeling**: Complex approval rules and scoring algorithms
- **Workflow Management**: Multi-stage approval processes
- **ITIL Understanding**: Industry-standard change management practices
- **Full-Stack Development**: Python backend with modern web frontend
- **Database Design**: Normalized schema with proper relationships
- **API Development**: RESTful endpoints for integration
- **User Experience**: Intuitive interface for different user roles
- **Data Processing**: CSV import and validation
- **Audit and Compliance**: Complete activity logging

---

Built with ❤️ using Python Flask and Bootstrap