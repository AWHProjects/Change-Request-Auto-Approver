from app import db
from datetime import datetime
from enum import Enum

class ChangeRequestStatus(Enum):
    PENDING = "pending"
    AUTO_APPROVED = "auto_approved"
    MANAGER_REVIEW = "manager_review"
    APPROVED = "approved"
    REJECTED = "rejected"

class ChangeRequestPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ChangeRequestType(Enum):
    STANDARD = "standard"
    NORMAL = "normal"
    EMERGENCY = "emergency"

class ChangeRequest(db.Model):
    __tablename__ = 'change_requests'
    
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requester_name = db.Column(db.String(100), nullable=False)
    requester_email = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    
    # Change details
    change_type = db.Column(db.Enum(ChangeRequestType), nullable=False)
    priority = db.Column(db.Enum(ChangeRequestPriority), nullable=False)
    systems_affected = db.Column(db.Text)  # JSON string of affected systems
    systems_count = db.Column(db.Integer, default=0)
    estimated_downtime = db.Column(db.Integer, default=0)  # in minutes
    rollback_plan = db.Column(db.Text)
    testing_plan = db.Column(db.Text)
    
    # Business impact
    business_impact = db.Column(db.String(50))  # low, medium, high
    user_impact = db.Column(db.String(50))  # low, medium, high
    financial_impact = db.Column(db.Float, default=0.0)
    
    # Scheduling
    requested_start_date = db.Column(db.DateTime)
    requested_end_date = db.Column(db.DateTime)
    maintenance_window = db.Column(db.String(100))
    
    # Status and approval
    status = db.Column(db.Enum(ChangeRequestStatus), default=ChangeRequestStatus.PENDING)
    auto_approval_score = db.Column(db.Float, default=0.0)
    approval_reason = db.Column(db.Text)
    approved_by = db.Column(db.String(100))
    approved_at = db.Column(db.DateTime)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'request_id': self.request_id,
            'title': self.title,
            'description': self.description,
            'requester_name': self.requester_name,
            'requester_email': self.requester_email,
            'department': self.department,
            'change_type': self.change_type.value if self.change_type else None,
            'priority': self.priority.value if self.priority else None,
            'systems_affected': self.systems_affected,
            'systems_count': self.systems_count,
            'estimated_downtime': self.estimated_downtime,
            'business_impact': self.business_impact,
            'user_impact': self.user_impact,
            'financial_impact': self.financial_impact,
            'status': self.status.value if self.status else None,
            'auto_approval_score': self.auto_approval_score,
            'approval_reason': self.approval_reason,
            'approved_by': self.approved_by,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ApprovalRule(db.Model):
    __tablename__ = 'approval_rules'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Rule conditions
    max_systems_affected = db.Column(db.Integer)
    max_downtime_minutes = db.Column(db.Integer)
    max_financial_impact = db.Column(db.Float)
    allowed_business_impact = db.Column(db.String(50))  # low, medium, high
    allowed_user_impact = db.Column(db.String(50))  # low, medium, high
    allowed_change_types = db.Column(db.Text)  # JSON string of allowed types
    allowed_priorities = db.Column(db.Text)  # JSON string of allowed priorities
    
    # Rule scoring
    weight = db.Column(db.Float, default=1.0)
    auto_approve_threshold = db.Column(db.Float, default=80.0)
    
    # Rule status
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    change_request_id = db.Column(db.Integer, db.ForeignKey('change_requests.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # created, approved, rejected, etc.
    performed_by = db.Column(db.String(100), nullable=False)
    details = db.Column(db.Text)  # JSON string with additional details
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    change_request = db.relationship('ChangeRequest', backref=db.backref('audit_logs', lazy=True))