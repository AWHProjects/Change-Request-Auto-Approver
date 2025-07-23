from flask import render_template, request, jsonify, redirect, url_for, flash
from app import app
from models import ChangeRequest, ApprovalRule, AuditLog, ChangeRequestStatus, ChangeRequestPriority, ChangeRequestType, db
from approval_engine import AutoApprovalEngine
from werkzeug.utils import secure_filename
import pandas as pd
import json
import os
from datetime import datetime
import uuid

@app.route('/')
def index():
    """Dashboard showing overview of change requests."""
    total_requests = ChangeRequest.query.count()
    pending_requests = ChangeRequest.query.filter_by(status=ChangeRequestStatus.PENDING).count()
    auto_approved = ChangeRequest.query.filter_by(status=ChangeRequestStatus.AUTO_APPROVED).count()
    manager_review = ChangeRequest.query.filter_by(status=ChangeRequestStatus.MANAGER_REVIEW).count()
    
    recent_requests = ChangeRequest.query.order_by(ChangeRequest.created_at.desc()).limit(10).all()
    
    stats = {
        'total': total_requests,
        'pending': pending_requests,
        'auto_approved': auto_approved,
        'manager_review': manager_review
    }
    
    return render_template('dashboard.html', stats=stats, recent_requests=recent_requests)

@app.route('/requests')
def list_requests():
    """List all change requests with filtering options."""
    status_filter = request.args.get('status')
    priority_filter = request.args.get('priority')
    
    query = ChangeRequest.query
    
    if status_filter:
        query = query.filter_by(status=ChangeRequestStatus(status_filter))
    
    if priority_filter:
        query = query.filter_by(priority=ChangeRequestPriority(priority_filter))
    
    requests = query.order_by(ChangeRequest.created_at.desc()).all()
    
    return render_template('requests_list.html', requests=requests, 
                         status_filter=status_filter, priority_filter=priority_filter)

@app.route('/requests/<int:request_id>')
def view_request(request_id):
    """View detailed information about a specific change request."""
    change_request = ChangeRequest.query.get_or_404(request_id)
    audit_logs = AuditLog.query.filter_by(change_request_id=request_id).order_by(AuditLog.timestamp.desc()).all()
    
    return render_template('request_detail.html', request=change_request, audit_logs=audit_logs)

@app.route('/submit', methods=['GET', 'POST'])
def submit_request():
    """Submit a new change request via web form."""
    if request.method == 'GET':
        return render_template('submit_request.html')
    
    try:
        # Generate unique request ID
        request_id = f"CR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
        
        # Parse systems affected
        systems_affected = request.form.get('systems_affected', '').strip()
        systems_list = [s.strip() for s in systems_affected.split(',') if s.strip()]
        
        # Create new change request
        change_request = ChangeRequest(
            request_id=request_id,
            title=request.form.get('title'),
            description=request.form.get('description'),
            requester_name=request.form.get('requester_name'),
            requester_email=request.form.get('requester_email'),
            department=request.form.get('department'),
            change_type=ChangeRequestType(request.form.get('change_type')),
            priority=ChangeRequestPriority(request.form.get('priority')),
            systems_affected=json.dumps(systems_list),
            systems_count=len(systems_list),
            estimated_downtime=int(request.form.get('estimated_downtime', 0)),
            rollback_plan=request.form.get('rollback_plan'),
            testing_plan=request.form.get('testing_plan'),
            business_impact=request.form.get('business_impact'),
            user_impact=request.form.get('user_impact'),
            financial_impact=float(request.form.get('financial_impact', 0)),
            maintenance_window=request.form.get('maintenance_window')
        )
        
        # Parse dates if provided
        if request.form.get('requested_start_date'):
            change_request.requested_start_date = datetime.fromisoformat(request.form.get('requested_start_date'))
        if request.form.get('requested_end_date'):
            change_request.requested_end_date = datetime.fromisoformat(request.form.get('requested_end_date'))
        
        db.session.add(change_request)
        db.session.commit()
        
        # Create initial audit log
        audit_log = AuditLog(
            change_request_id=change_request.id,
            action="created",
            performed_by=change_request.requester_name,
            details=json.dumps({'method': 'web_form'})
        )
        db.session.add(audit_log)
        
        # Process through auto-approval engine
        engine = AutoApprovalEngine()
        auto_approved, score, details = engine.process_change_request(change_request)
        
        db.session.commit()
        
        if auto_approved:
            flash(f'Change request {request_id} has been automatically approved!', 'success')
        else:
            flash(f'Change request {request_id} has been submitted for manager review.', 'info')
        
        return redirect(url_for('view_request', request_id=change_request.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting request: {str(e)}', 'error')
        return render_template('submit_request.html')

@app.route('/upload-csv', methods=['GET', 'POST'])
def upload_csv():
    """Upload and process change requests from CSV file."""
    if request.method == 'GET':
        return render_template('upload_csv.html')
    
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect(request.url)
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect(request.url)
    
    if file and file.filename.lower().endswith('.csv'):
        try:
            # Save uploaded file
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Process CSV
            df = pd.read_csv(filepath)
            processed_count = 0
            errors = []
            
            engine = AutoApprovalEngine()
            
            for index, row in df.iterrows():
                try:
                    # Generate unique request ID
                    request_id = f"CR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
                    
                    # Parse systems affected
                    systems_affected = str(row.get('systems_affected', '')).strip()
                    systems_list = [s.strip() for s in systems_affected.split(',') if s.strip()]
                    
                    # Create change request from CSV row
                    change_request = ChangeRequest(
                        request_id=request_id,
                        title=str(row.get('title', '')),
                        description=str(row.get('description', '')),
                        requester_name=str(row.get('requester_name', '')),
                        requester_email=str(row.get('requester_email', '')),
                        department=str(row.get('department', '')),
                        change_type=ChangeRequestType(row.get('change_type', 'normal')),
                        priority=ChangeRequestPriority(row.get('priority', 'medium')),
                        systems_affected=json.dumps(systems_list),
                        systems_count=len(systems_list),
                        estimated_downtime=int(row.get('estimated_downtime', 0)),
                        rollback_plan=str(row.get('rollback_plan', '')),
                        testing_plan=str(row.get('testing_plan', '')),
                        business_impact=str(row.get('business_impact', 'low')),
                        user_impact=str(row.get('user_impact', 'low')),
                        financial_impact=float(row.get('financial_impact', 0)),
                        maintenance_window=str(row.get('maintenance_window', ''))
                    )
                    
                    db.session.add(change_request)
                    db.session.commit()
                    
                    # Create audit log
                    audit_log = AuditLog(
                        change_request_id=change_request.id,
                        action="created",
                        performed_by="CSV Import",
                        details=json.dumps({'method': 'csv_upload', 'filename': filename})
                    )
                    db.session.add(audit_log)
                    
                    # Process through auto-approval engine
                    engine.process_change_request(change_request)
                    
                    processed_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
                    db.session.rollback()
            
            db.session.commit()
            
            # Clean up uploaded file
            os.remove(filepath)
            
            if errors:
                flash(f'Processed {processed_count} requests with {len(errors)} errors: {"; ".join(errors[:5])}', 'warning')
            else:
                flash(f'Successfully processed {processed_count} change requests from CSV', 'success')
            
            return redirect(url_for('list_requests'))
            
        except Exception as e:
            flash(f'Error processing CSV file: {str(e)}', 'error')
            return redirect(request.url)
    
    else:
        flash('Please upload a valid CSV file', 'error')
        return redirect(request.url)

@app.route('/manager-review')
def manager_review():
    """Manager review queue for change requests requiring manual approval."""
    pending_requests = ChangeRequest.query.filter_by(status=ChangeRequestStatus.MANAGER_REVIEW).order_by(ChangeRequest.created_at.desc()).all()
    
    return render_template('manager_review.html', requests=pending_requests)

@app.route('/approve/<int:request_id>', methods=['POST'])
def approve_request(request_id):
    """Approve a change request (manager action)."""
    change_request = ChangeRequest.query.get_or_404(request_id)
    manager_name = request.form.get('manager_name', 'Manager')
    approval_comments = request.form.get('comments', '')
    
    change_request.status = ChangeRequestStatus.APPROVED
    change_request.approved_by = manager_name
    change_request.approved_at = datetime.utcnow()
    change_request.approval_reason = f"Manually approved by {manager_name}"
    
    # Create audit log
    audit_log = AuditLog(
        change_request_id=change_request.id,
        action="approved",
        performed_by=manager_name,
        details=json.dumps({'comments': approval_comments})
    )
    db.session.add(audit_log)
    db.session.commit()
    
    flash(f'Change request {change_request.request_id} has been approved', 'success')
    return redirect(url_for('manager_review'))

@app.route('/reject/<int:request_id>', methods=['POST'])
def reject_request(request_id):
    """Reject a change request (manager action)."""
    change_request = ChangeRequest.query.get_or_404(request_id)
    manager_name = request.form.get('manager_name', 'Manager')
    rejection_reason = request.form.get('reason', '')
    
    change_request.status = ChangeRequestStatus.REJECTED
    change_request.approval_reason = f"Rejected by {manager_name}: {rejection_reason}"
    
    # Create audit log
    audit_log = AuditLog(
        change_request_id=change_request.id,
        action="rejected",
        performed_by=manager_name,
        details=json.dumps({'reason': rejection_reason})
    )
    db.session.add(audit_log)
    db.session.commit()
    
    flash(f'Change request {change_request.request_id} has been rejected', 'info')
    return redirect(url_for('manager_review'))

@app.route('/api/requests', methods=['GET', 'POST'])
def api_requests():
    """API endpoint for change requests."""
    if request.method == 'GET':
        # Get all requests or filter by status
        status_filter = request.args.get('status')
        query = ChangeRequest.query
        
        if status_filter:
            query = query.filter_by(status=ChangeRequestStatus(status_filter))
        
        requests = query.order_by(ChangeRequest.created_at.desc()).all()
        return jsonify([req.to_dict() for req in requests])
    
    elif request.method == 'POST':
        # Create new request via API
        try:
            data = request.get_json()
            
            # Generate unique request ID
            request_id = f"CR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Parse systems affected
            systems_affected = data.get('systems_affected', [])
            if isinstance(systems_affected, str):
                systems_list = [s.strip() for s in systems_affected.split(',') if s.strip()]
            else:
                systems_list = systems_affected
            
            # Create change request
            change_request = ChangeRequest(
                request_id=request_id,
                title=data.get('title'),
                description=data.get('description'),
                requester_name=data.get('requester_name'),
                requester_email=data.get('requester_email'),
                department=data.get('department'),
                change_type=ChangeRequestType(data.get('change_type', 'normal')),
                priority=ChangeRequestPriority(data.get('priority', 'medium')),
                systems_affected=json.dumps(systems_list),
                systems_count=len(systems_list),
                estimated_downtime=int(data.get('estimated_downtime', 0)),
                rollback_plan=data.get('rollback_plan', ''),
                testing_plan=data.get('testing_plan', ''),
                business_impact=data.get('business_impact', 'low'),
                user_impact=data.get('user_impact', 'low'),
                financial_impact=float(data.get('financial_impact', 0)),
                maintenance_window=data.get('maintenance_window', '')
            )
            
            db.session.add(change_request)
            db.session.commit()
            
            # Create audit log
            audit_log = AuditLog(
                change_request_id=change_request.id,
                action="created",
                performed_by=change_request.requester_name,
                details=json.dumps({'method': 'api'})
            )
            db.session.add(audit_log)
            
            # Process through auto-approval engine
            engine = AutoApprovalEngine()
            auto_approved, score, details = engine.process_change_request(change_request)
            
            db.session.commit()
            
            return jsonify({
                'success': True,
                'request_id': request_id,
                'id': change_request.id,
                'auto_approved': auto_approved,
                'score': score,
                'status': change_request.status.value
            }), 201
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/rules')
def list_rules():
    """List all approval rules."""
    rules = ApprovalRule.query.order_by(ApprovalRule.created_at.desc()).all()
    return render_template('rules_list.html', rules=rules)