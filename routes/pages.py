from flask import Blueprint, render_template


def create_pages_blueprint():
    bp = Blueprint('pages', __name__)

    @bp.route('/')
    def index():
        return render_template('dashboard.html')

    @bp.route('/landing')
    def landing_page():
        return render_template('dashboard.html')

    @bp.route('/catalog')
    def catalog():
        return render_template('dashboard.html')

    @bp.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')

    @bp.route('/nexmart')
    def nexmart():
        return render_template('dashboard.html')

    @bp.route('/code')
    def code_page():
        return render_template('dashboard.html')

    return bp
