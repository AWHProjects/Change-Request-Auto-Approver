import json
from models import ApprovalRule
from app import db

def initialize_default_rules():
    """Initialize default approval rules for the system."""
    
    # Rule 1: Low-impact standard changes
    rule1 = ApprovalRule(
        name="Low Impact Standard Changes",
        description="Auto-approve low-impact standard changes with minimal risk",
        max_systems_affected=2,
        max_downtime_minutes=30,
        max_financial_impact=1000.0,
        allowed_business_impact="low",
        allowed_user_impact="low",
        allowed_change_types=json.dumps(["standard"]),
        allowed_priorities=json.dumps(["low", "medium"]),
        weight=1.0,
        auto_approve_threshold=80.0,
        is_active=True
    )
    
    # Rule 2: Emergency changes with higher threshold
    rule2 = ApprovalRule(
        name="Emergency Changes",
        description="Emergency changes require higher scrutiny",
        max_systems_affected=5,
        max_downtime_minutes=120,
        max_financial_impact=5000.0,
        allowed_business_impact="high",
        allowed_user_impact="high",
        allowed_change_types=json.dumps(["emergency"]),
        allowed_priorities=json.dumps(["high", "critical"]),
        weight=1.5,
        auto_approve_threshold=90.0,
        is_active=True
    )
    
    # Rule 3: Normal changes - balanced approach
    rule3 = ApprovalRule(
        name="Normal Changes",
        description="Standard approval criteria for normal changes",
        max_systems_affected=3,
        max_downtime_minutes=60,
        max_financial_impact=2500.0,
        allowed_business_impact="medium",
        allowed_user_impact="medium",
        allowed_change_types=json.dumps(["normal"]),
        allowed_priorities=json.dumps(["low", "medium", "high"]),
        weight=1.0,
        auto_approve_threshold=85.0,
        is_active=True
    )
    
    db.session.add_all([rule1, rule2, rule3])
    db.session.commit()
    
    print("Default approval rules initialized successfully!")

def generate_sample_csv():
    """Generate a sample CSV file for testing."""
    import pandas as pd
    
    sample_data = [
        {
            'title': 'Update database schema',
            'description': 'Add new index to improve query performance',
            'requester_name': 'John Smith',
            'requester_email': 'john.smith@company.com',
            'department': 'IT',
            'change_type': 'standard',
            'priority': 'medium',
            'systems_affected': 'Database Server, Application Server',
            'estimated_downtime': 15,
            'rollback_plan': 'Drop the new index if issues occur',
            'testing_plan': 'Run performance tests in staging environment',
            'business_impact': 'low',
            'user_impact': 'low',
            'financial_impact': 500,
            'maintenance_window': 'Saturday 2AM-4AM'
        },
        {
            'title': 'Security patch deployment',
            'description': 'Deploy critical security patches to web servers',
            'requester_name': 'Sarah Johnson',
            'requester_email': 'sarah.johnson@company.com',
            'department': 'Security',
            'change_type': 'emergency',
            'priority': 'critical',
            'systems_affected': 'Web Server 1, Web Server 2, Load Balancer',
            'estimated_downtime': 45,
            'rollback_plan': 'Restore from backup if patches cause issues',
            'testing_plan': 'Verify all services after patch deployment',
            'business_impact': 'medium',
            'user_impact': 'medium',
            'financial_impact': 0,
            'maintenance_window': 'Immediate'
        }
    ]
    
    df = pd.DataFrame(sample_data)
    df.to_csv('sample_change_requests.csv', index=False)
    print("Sample CSV file generated: sample_change_requests.csv")