from flask import Flask, render_template, redirect, url_for, flash
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from forms import LoanApplicationForm, LoginForm, RegistrationForm
from models import db, Client, Loan
from flask_login import LoginManager, login_user, logout_user, login_required, current_user


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] \
    = 'sqlite:///C:/Users/eachi/PycharmProjects/bank_loan_automatize/instance/database.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


# Добавляем миграции
migrate = Migrate(app, db)

with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return Client.query.get(int(user_id))


@app.route('/')
def index():
    return redirect(url_for('bank_login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data)
        new_user = Client(name=form.name.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Регистрация прошла успешно!', 'success')
        return redirect(url_for('bank_login'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Client.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Вы вошли в систему!', 'success')
            # Условие для перенаправления
            if user.is_admin:
                return redirect(url_for('bank_dashboard'))  # Перенаправление на панель администратора
            else:
                return redirect(url_for('index'))  # Возврат на главную страницу для обычных пользователей
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('login.html', form=form)


@app.route('/bank_dashboard', methods=['GET'])
@login_required
def bank_dashboard():
    if not current_user.is_admin:
        flash('У вас нет прав для доступа к этой панели!', 'danger')
        return redirect(url_for('index'))

    loans = Loan.query.all()  # Получаем все кредиты
    return render_template('bank_dashboard.html', loans=loans)


@app.route('/approve_loan/<int:loan_id>', methods=['POST'])
@login_required
def approve_loan(loan_id):
    if not current_user.is_admin:
        flash('У вас нет прав для выполнения этого действия!', 'danger')
        return redirect(url_for('index'))

    loan = Loan.query.get(loan_id)
    if loan:
        loan.status = 'Approved'  # Одобрение кредита
        db.session.commit()
        flash('Кредит одобрен!', 'success')
    else:
        flash('Кредит не найден.', 'danger')
    return redirect(url_for('bank_dashboard'))


@app.route('/reject_loan/<int:loan_id>', methods=['POST'])
@login_required
def reject_loan(loan_id):
    if not current_user.is_admin:
        flash('У вас нет прав для выполнения этого действия!', 'danger')
        return redirect(url_for('index'))

    loan = Loan.query.get(loan_id)
    if loan:
        loan.status = 'Rejected'  # Отклонение кредита
        db.session.commit()
        flash('Кредит отклонен!', 'success')
    else:
        flash('Кредит не найден.', 'danger')
    return redirect(url_for('bank_dashboard'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы!', 'success')
    return redirect(url_for('bank_login'))


# Логин сотрудника банка
@app.route('/bank_login', methods=['GET', 'POST'])
def bank_login():
    form = LoginForm()
    if form.validate_on_submit():

        return redirect(url_for('bank_dashboard'))
    return render_template('login.html', form=form)


@app.route('/apply_loan', methods=['GET', 'POST'])
def apply_loan():
    form = LoanApplicationForm()
    if form.validate_on_submit():
        # Проверяем, существует ли клиент с указанным email
        existing_client = Client.query.filter_by(email=form.email.data).first()
        if existing_client is None:
            flash('Клиент с таким email не найден. Сначала зарегистрируйтесь.', 'danger')
            return redirect(url_for('apply_loan'))

        # Если клиент существует, создаем новый кредит
        new_loan = Loan(
            amount=form.amount.data,
            interest_rate=form.interest_rate.data,
            client_id=existing_client.id
        )
        db.session.add(new_loan)
        db.session.commit()

        flash('Заявка на кредит принята!', 'success')
        return redirect(url_for('index'))

    return render_template('client_form.html', form=form)


@app.route('/manage_users', methods=['GET'])
@login_required
def manage_users():
    if not current_user.is_admin:
        flash('У вас нет прав для доступа к этой панели!', 'danger')
        return redirect(url_for('index'))

    users = Client.query.all()
    return render_template('manage_users.html', users=users)


@app.route('/toggle_administrator/<int:user_id>', methods=['GET'])
@login_required
def toggle_administrator(user_id):
    if not current_user.is_admin:
        flash('У вас нет прав для выполнения этого действия!', 'danger')
        return redirect(url_for('index'))

    user = Client.query.get(user_id)
    if user:
        user.is_admin = not user.is_admin  # Переключаем статус
        db.session.commit()
        flash(f'Пользователь {user.name} теперь {"администратор" if user.is_admin else "пользователь"}!', 'success')
    else:
        flash('Пользователь не найден.', 'error')

    return redirect(url_for('manage_users'))


with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
