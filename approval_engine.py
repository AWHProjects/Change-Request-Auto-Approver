import json
from models import ChangeRequest, ApprovalRule, AuditLog, ChangeRequestStatus
from app import db
from datetime import datetime

class AutoApprovalEngine:
    """
    Auto-approval engine that evaluates change requests against predefined rules
    following ITIL best practices for change management.
    """
    
    def __init__(self):
        self.rules = self._load_active_rules()
    
    def _load_active_rules(self):
        """Load all active approval rules from the database."""
        return ApprovalRule.query.filter_by(is_active=True).all()
    
    def evaluate_change_request(self, change_request):
        """
        Evaluate a change request against all active approval rules.
        Returns a tuple of (should_auto_approve, score, reasons)
        """
        if not self.rules:
            return False, 0.0, ["No approval rules configured"]
        
        total_score = 0.0
        max_possible_score = 0.0
        evaluation_details = []
        
        for rule in self.rules:
            rule_score, rule_details = self._evaluate_against_rule(change_request, rule)
            total_score += rule_score * rule.weight
            max_possible_score += 100.0 * rule.weight
            evaluation_details.append({
                'rule_name': rule.name,
                'score': rule_score,
                'weight': rule.weight,
                'details': rule_details
            })
        
        # Calculate percentage score
        final_score = (total_score / max_possible_score * 100) if max_possible_score > 0 else 0
        
        # Determine if should auto-approve based on the highest threshold among rules
        auto_approve_threshold = max([rule.auto_approve_threshold for rule in self.rules])
        should_auto_approve = final_score >= auto_approve_threshold
        
        return should_auto_approve, final_score, evaluation_details
    
    def _evaluate_against_rule(self, change_request, rule):
        """
        Evaluate a change request against a specific rule.
        Returns a tuple of (score, details)
        """
        score = 100.0  # Start with perfect score
        details = []
        
        # Check systems affected
        if rule.max_systems_affected is not None:
            if change_request.systems_count > rule.max_systems_affected:
                score -= 30
                details.append(f"Systems affected ({change_request.systems_count}) exceeds limit ({rule.max_systems_affected})")
            else:
                details.append(f"Systems affected check passed ({change_request.systems_count} <= {rule.max_systems_affected})")
        
        # Check downtime
        if rule.max_downtime_minutes is not None:
            if change_request.estimated_downtime > rule.max_downtime_minutes:
                score -= 25
                details.append(f"Estimated downtime ({change_request.estimated_downtime}min) exceeds limit ({rule.max_downtime_minutes}min)")
            else:
                details.append(f"Downtime check passed ({change_request.estimated_downtime}min <= {rule.max_downtime_minutes}min)")
        
        # Check financial impact
        if rule.max_financial_impact is not None:
            if change_request.financial_impact > rule.max_financial_impact:
                score -= 20
                details.append(f"Financial impact (${change_request.financial_impact}) exceeds limit (${rule.max_financial_impact})")
            else:
                details.append(f"Financial impact check passed (${change_request.financial_impact} <= ${rule.max_financial_impact})")
        
        # Check business impact
        if rule.allowed_business_impact:
            impact_levels = {'low': 1, 'medium': 2, 'high': 3}
            allowed_level = impact_levels.get(rule.allowed_business_impact, 3)
            request_level = impact_levels.get(change_request.business_impact, 3)
            
            if request_level > allowed_level:
                score -= 15
                details.append(f"Business impact ({change_request.business_impact}) exceeds allowed level ({rule.allowed_business_impact})")
            else:
                details.append(f"Business impact check passed ({change_request.business_impact} <= {rule.allowed_business_impact})")
        
        # Check user impact
        if rule.allowed_user_impact:
            impact_levels = {'low': 1, 'medium': 2, 'high': 3}
            allowed_level = impact_levels.get(rule.allowed_user_impact, 3)
            request_level = impact_levels.get(change_request.user_impact, 3)
            
            if request_level > allowed_level:
                score -= 15
                details.append(f"User impact ({change_request.user_impact}) exceeds allowed level ({rule.allowed_user_impact})")
            else:
                details.append(f"User impact check passed ({change_request.user_impact} <= {rule.allowed_user_impact})")
        
        # Check change type
        if rule.allowed_change_types:
            try:
                allowed_types = json.loads(rule.allowed_change_types)
                if change_request.change_type.value not in allowed_types:
                    score -= 10
                    details.append(f"Change type ({change_request.change_type.value}) not in allowed types ({allowed_types})")
                else:
                    details.append(f"Change type check passed ({change_request.change_type.value} in {allowed_types})")
            except (json.JSONDecodeError, AttributeError):
                details.append("Could not parse allowed change types")
        
        # Check priority
        if rule.allowed_priorities:
            try:
                allowed_priorities = json.loads(rule.allowed_priorities)
                if change_request.priority.value not in allowed_priorities:
                    score -= 10
                    details.append(f"Priority ({change_request.priority.value}) not in allowed priorities ({allowed_priorities})")
                else:
                    details.append(f"Priority check passed ({change_request.priority.value} in {allowed_priorities})")
            except (json.JSONDecodeError, AttributeError):
                details.append("Could not parse allowed priorities")
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        return score, details
    
    def process_change_request(self, change_request):
        """
        Process a change request through the auto-approval engine.
        Updates the change request status and creates audit logs.
        """
        should_auto_approve, score, evaluation_details = self.evaluate_change_request(change_request)
        
        # Update change request with evaluation results
        change_request.auto_approval_score = score
        
        if should_auto_approve:
            change_request.status = ChangeRequestStatus.AUTO_APPROVED
            change_request.approved_by = "Auto-Approval System"
            change_request.approved_at = datetime.utcnow()
            change_request.approval_reason = f"Auto-approved with score {score:.1f}%"
            
            # Create audit log
            audit_log = AuditLog(
                change_request_id=change_request.id,
                action="auto_approved",
                performed_by="Auto-Approval System",
                details=json.dumps({
                    'score': score,
                    'evaluation_details': evaluation_details
                })
            )
        else:
            change_request.status = ChangeRequestStatus.MANAGER_REVIEW
            change_request.approval_reason = f"Requires manager review (score: {score:.1f}%)"
            
            # Create audit log
            audit_log = AuditLog(
                change_request_id=change_request.id,
                action="queued_for_review",
                performed_by="Auto-Approval System",
                details=json.dumps({
                    'score': score,
                    'evaluation_details': evaluation_details,
                    'reason': 'Score below auto-approval threshold'
                })
            )
        
        db.session.add(audit_log)
        db.session.commit()
        
        return should_auto_approve, score, evaluation_details