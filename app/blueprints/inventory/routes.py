# app/blueprints/inventory/routes.py
from flask import render_template, request, redirect, url_for, flash
from app.blueprints.inventory import inventory_bp
from app.service import lend_service

@inventory_bp.route('/lend', methods=['GET', 'POST'])
def lend():
    if request.method == 'POST':
        user_id = request.form['user_id']
        equipment_id = request.form['equipment_id']
        quantity = int(request.form['quantity'])

        try:
            result = lend_service.lend_equipment(user_id, equipment_id, quantity)
            flash(result['message'], 'success')
            return redirect(url_for('inventory.inventory'))
        except Exception as e:
            flash(str(e), 'danger')
            return redirect(url_for('inventory.lend'))

    return render_template('lend.html')
