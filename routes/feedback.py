from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
from models import get_db_connection
feedback_bp = Blueprint('feedback', __name__, template_folder='templates')

                                             # зробив (Пахольчук Максим)

@feedback_bp.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if not session.get('is_client') or 'client_email' not in session:
        flash("Будь ласка, увійдіть у свій акаунт, щоб залишити відгук", "warning")
        return redirect(url_for('client.login', next=request.path))

    if request.method == 'POST':
        name = request.form['name']
        email = session['client_email']
        message = request.form['message']

        conn = get_db_connection()
        conn.execute(
            'INSERT INTO feedback (name, email, message) VALUES (?, ?, ?)',
            (name, email, message)
        )
        conn.commit()
        conn.close()

        flash("Дякуємо за ваш відгук", "success")
        return redirect(url_for('feedback.feedback'))

    return render_template('feedback.html')


