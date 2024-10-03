from flask import Flask, render_template, redirect, url_for, flash, session
from flask_bootstrap import Bootstrap5
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
import csv
from flask_sqlalchemy import SQLAlchemy
from flask import send_from_directory
import os  # Para manipular o sistema de arquivos
from werkzeug.utils import secure_filename  # Para garantir a segurança no upload de arquivos
from flask import Flask, render_template, redirect, url_for, flash, session, request
from datetime import datetime



app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///devs.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

Bootstrap5(app)
db = SQLAlchemy(app)

# este caminho corresponde ao diretório onde os currículos são salvos
app.config['UPLOAD_FOLDER'] = 'static/uploads' 


# -------------------------------------------------------------------------------------------------

favorites = db.Table('favorites',
    db.Column('dev_id', db.Integer, db.ForeignKey('dev.id'), primary_key=True),
    db.Column('job_id', db.Integer, db.ForeignKey('job.id'), primary_key=True)
)

# Modelos de Banco de Dados
class Dev(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    cel = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    habilidades = db.Column(db.Text, nullable=False)
    experiencia = db.Column(db.Text)  # Experiência do desenvolvedor
    portfolio = db.Column(db.String(255))  # Link para portfólio
    cv_file = db.Column(db.String(255))  # Arquivo de currículo
    cidade = db.Column(db.String(100))  # Cidade do desenvolvedor
    pais = db.Column(db.String(100))  # País do desenvolvedor
    disponibilidade = db.Column(db.String(50))  # Disponibilidade para trabalho
    idiomas = db.Column(db.Text)  # Idiomas falados
    objetivo_profissional = db.Column(db.Text)  # Objetivo profissional
    profile_picture = db.Column(db.String(255))  # Nome do arquivo da foto de perfil
    
    # Relacionamento de favoritos
    favorites = db.relationship('Job', secondary=favorites, backref='favorited_by')



class Empresa(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    setor = db.Column(db.String(100), nullable=False)

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    empresa_id = db.Column(db.Integer, db.ForeignKey('empresa.id'), nullable=False)
    empresa = db.relationship('Empresa', backref=db.backref('jobs', lazy=True))
    applications = db.relationship('Application', cascade="all, delete-orphan", backref="job")


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    dev_id = db.Column(db.Integer, db.ForeignKey('dev.id'), nullable=False)
    dev = db.relationship('Dev', backref=db.backref('applications', lazy=True))
    
    # Nova coluna para registrar o match
    matched = db.Column(db.Boolean, default=False)
    
class FavoriteJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dev_id = db.Column(db.Integer, db.ForeignKey('dev.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    


class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    dev_id = db.Column(db.Integer, db.ForeignKey('dev.id'), nullable=False)
    scheduled_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Pendente")
    job = db.relationship('Job', backref=db.backref('interviews', lazy=True))
    dev = db.relationship('Dev', backref=db.backref('interviews', lazy=True))

# -------------------------------------------------------------------------------------------------
# Formulários
class EmpresaForm(FlaskForm):
    name = StringField('Nome da Empresa', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    password = StringField('Senha', validators=[DataRequired()])
    setor = StringField('Setor de Atuação', validators=[DataRequired()])
    submit = SubmitField('Cadastrar Empresa')

class LoginForm(FlaskForm):
    email = StringField('E-mail', validators=[DataRequired()])
    password = StringField('Senha', validators=[DataRequired()])
    submit = SubmitField('Login')

class DevForm(FlaskForm):
    name = StringField('Nome', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired()])
    cel = StringField('Celular', validators=[DataRequired()])
    password = StringField('Senha', validators=[DataRequired()])
    habilidades = TextAreaField('Habilidades', validators=[DataRequired()])
    submit = SubmitField('Cadastrar')

class JobForm(FlaskForm):
    title = StringField('Título da Vaga', validators=[DataRequired()])
    description = TextAreaField('Descrição', validators=[DataRequired()])
    requirements = TextAreaField('Requisitos', validators=[DataRequired()])
    submit = SubmitField('Publicar Vaga')

# -------------------------------------------------------------------------------------------------
# Rotas
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dev/register", methods=["GET", "POST"])
def dev_register():
    form = DevForm()
    if form.validate_on_submit():
        new_dev = Dev(
            name=form.name.data,
            email=form.email.data,
            cel=form.cel.data,
            password=form.password.data,
            habilidades=form.habilidades.data
        )
        db.session.add(new_dev)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template("dev_register.html", form=form)

@app.route("/dev/login", methods=["GET", "POST"])
def dev_login():
    form = LoginForm()
    if form.validate_on_submit():
        dev = Dev.query.filter_by(email=form.email.data).first()
        if dev and dev.password == form.password.data:
            # Armazena o e-mail do usuário na sessão
            session['user_email'] = dev.email
            flash('Login realizado com sucesso!', 'success')

            # Adiciona um print para verificar se o e-mail está na sessão
            print(f"Usuário logado: {session['user_email']}")

            return redirect(url_for('dev_dashboard'))
        else:
            flash('Login falhou. Verifique seu e-mail e senha.', 'danger')
    return render_template("dev_login.html", form=form)

@app.route("/empresa/register", methods=["GET", "POST"])
def empresa_register():
    form = EmpresaForm()
    if form.validate_on_submit():
        new_empresa = Empresa(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            setor=form.setor.data
        )
        db.session.add(new_empresa)
        db.session.commit()
        flash('Cadastro de empresa realizado com sucesso!', 'success')
        return redirect(url_for('home'))
    return render_template("empresa_register.html", form=form)

@app.route("/empresa/login", methods=["GET", "POST"])
def empresa_login():
    form = LoginForm()
    if form.validate_on_submit():
        empresa = Empresa.query.filter_by(email=form.email.data).first()
        if empresa and empresa.password == form.password.data:
            session['empresa_email'] = empresa.email
            flash('Login de empresa realizado com sucesso!', 'success')
            return redirect(url_for('empresa_dashboard'))
        else:
            flash('Login falhou. Verifique seu e-mail e senha.', 'danger')
    return render_template("empresa_login.html", form=form)

@app.route('/empresa/dashboard', methods=["GET", "POST"])
def empresa_dashboard():
    if 'empresa_email' not in session:
        flash('Faça login para acessar o dashboard.', 'danger')
        return redirect(url_for('empresa_login'))

    form = JobForm()
    empresa = Empresa.query.filter_by(email=session['empresa_email']).first()

    # Lógica para adicionar vaga
    if form.validate_on_submit():
        new_job = Job(
            title=form.title.data,
            description=form.description.data,
            requirements=form.requirements.data,
            empresa_id=empresa.id
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Vaga publicada com sucesso!', 'success')
        return redirect(url_for('empresa_dashboard'))

    # Buscar vagas criadas pela empresa
    jobs = Job.query.filter_by(empresa_id=empresa.id).all()

    # Para cada vaga, buscar os desenvolvedores que se candidataram
    candidaturas = {}
    for job in jobs:
        applications = Application.query.filter_by(job_id=job.id).all()
        devs = [Dev.query.get(application.dev_id) for application in applications]
        candidaturas[job.id] = devs  # Associa os desenvolvedores à vaga pelo ID da vaga

    return render_template('empresa_dashboard.html', form=form, jobs=jobs, candidaturas=candidaturas, empresa=empresa)




@app.route('/dev/dashboard')
def dev_dashboard():
    if 'user_email' not in session:
        flash('Faça login para acessar o dashboard.', 'danger')
        return redirect(url_for('dev_login'))

    dev = Dev.query.filter_by(email=session['user_email']).first()  # Obtenha o dev logado
    search_query = request.args.get('search', '')

    if search_query:
        jobs = Job.query.filter(Job.title.contains(search_query) | Job.requirements.contains(search_query)).all()
    else:
        jobs = Job.query.all()

    return render_template('dashboard.html', jobs=jobs, dev=dev)  # Passe o dev para o template




# Rota para se candidatar a uma vaga
@app.route('/apply/<int:job_id>', methods=["POST"])
def apply_job(job_id):
    # Verifica se o usuário está logado
    if 'user_email' not in session:
        flash("Você precisa estar logado como desenvolvedor para se candidatar.", "danger")
        return redirect(url_for('dev_login'))

    # Obter o desenvolvedor logado a partir do e-mail salvo na sessão
    dev = Dev.query.filter_by(email=session['user_email']).first()
    
    # Verificar se o desenvolvedor já se candidatou a essa vaga
    existing_application = Application.query.filter_by(job_id=job_id, dev_id=dev.id).first()
    if existing_application:
        flash(f'Você já se candidatou a esta vaga.', 'warning')
        return redirect(url_for('dev_dashboard'))

    # Criar uma nova aplicação para a vaga
    new_application = Application(job_id=job_id, dev_id=dev.id)
    db.session.add(new_application)
    db.session.commit()
    flash(f'Você se candidatou à vaga com sucesso!', 'success')
    return redirect(url_for('dev_dashboard'))

  
# Rota para excluir vaga
@app.route('/empresa/delete_job/<int:job_id>', methods=['POST'])
def delete_job(job_id):
    job = Job.query.get_or_404(job_id)
    db.session.delete(job)
    db.session.commit()
    flash('A vaga foi excluída com sucesso!', 'success')
    return redirect(url_for('empresa_dashboard'))

@app.route('/empresa/edit_job/<int:job_id>', methods=["GET", "POST"])
def edit_job(job_id):
    job = Job.query.get_or_404(job_id)
    form = JobForm(obj=job)  # Preenche o formulário com os dados da vaga
    if form.validate_on_submit():
        job.title = form.title.data
        job.description = form.description.data
        job.requirements = form.requirements.data
        db.session.commit()
        flash('Vaga atualizada com sucesso!', 'success')
        return redirect(url_for('empresa_dashboard'))
    return render_template('edit_job.html', form=form, job=job)

@app.route('/dev/applications', methods=["GET"])
def dev_applications():
    if 'user_email' not in session:
        flash("Você precisa estar logado para ver suas candidaturas.", "danger")
        return redirect(url_for('dev_login'))
    
    # Obter o desenvolvedor logado
    dev = Dev.query.filter_by(email=session['user_email']).first()
    
    # Buscar todas as candidaturas do desenvolvedor logado
    applications = Application.query.filter_by(dev_id=dev.id).all()
    
    # Obter as vagas relacionadas às candidaturas
    jobs = [application.job for application in applications]
    
    return render_template('dev_applications.html', jobs=jobs)

@app.route('/empresa/candidaturas', methods=["GET"])
def empresa_candidaturas():
    if 'empresa_email' not in session:
        flash("Você precisa estar logado como empresa para ver as candidaturas.", "danger")
        return redirect(url_for('empresa_login'))
    
    # Obter a empresa logada
    empresa = Empresa.query.filter_by(email=session['empresa_email']).first()

    # Buscar todas as vagas criadas pela empresa
    jobs = Job.query.filter_by(empresa_id=empresa.id).all()

    # Buscando todas as candidaturas associadas às vagas da empresa
    candidaturas = []
    for job in jobs:
        applications = Application.query.filter_by(job_id=job.id).all()
        for application in applications:
            dev = Dev.query.get(application.dev_id)
            interview = Interview.query.filter_by(job_id=job.id, dev_id=dev.id).first()  # Buscar entrevista associada (se houver)
            candidaturas.append({
                'job': job,
                'dev': dev,
                'application': application,
                'interview': interview  # Pode ser None se ainda não tiver sido agendada
            })

    return render_template('empresa_candidaturas.html', candidaturas=candidaturas)



    return render_template('empresa_candidaturas.html', candidaturas=candidaturas)

@app.route('/empresa/match/<int:candidatura_id>', methods=['POST'])
def match_candidate(candidatura_id):
    candidatura = Application.query.get_or_404(candidatura_id)
    candidatura.matched = True
    db.session.commit()
    flash('Você deu match com o desenvolvedor!', 'success')
    return redirect(url_for('empresa_candidaturas'))


@app.route('/dev/matches', methods=["GET"])
def dev_matches():
    dev = Dev.query.filter_by(email=session['user_email']).first()
    matches = Application.query.filter_by(dev_id=dev.id, matched=True).all()
    return render_template('dev_matches.html', matches=matches)

@app.route('/empresa/add_job', methods=['GET', 'POST'])
def add_job():
    form = JobForm()
    empresa = Empresa.query.filter_by(email=session['empresa_email']).first()
    
    if form.validate_on_submit():
        new_job = Job(
            title=form.title.data,
            description=form.description.data,
            requirements=form.requirements.data,
            empresa_id=empresa.id
        )
        db.session.add(new_job)
        db.session.commit()
        flash('Vaga publicada com sucesso!', 'success')
        return redirect(url_for('empresa_dashboard'))
    
    return render_template('add_job.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_email', None)  # Remove a sessão do desenvolvedor
    session.pop('empresa_email', None)  # Remove a sessão da empresa
    flash('Você saiu da sua conta.', 'success')
    return redirect(url_for('home'))

@app.route('/empresa/job/<int:job_id>/candidaturas', methods=["GET"])
def view_candidaturas(job_id):
    job = Job.query.get_or_404(job_id)
    applications = Application.query.filter_by(job_id=job_id).all()
    
    candidaturas = []
    for application in applications:
        dev = Dev.query.get(application.dev_id)
        candidaturas.append({
            'job': job,
            'dev': dev,
            'application': application  # Inclui o objeto application, que tem o id
        })
    
    return render_template('empresa_candidaturas.html', candidaturas=candidaturas)

# Rota para exibir o perfil do desenvolvedor
@app.route('/dev/profile')
def dev_profile():
    dev = Dev.query.filter_by(email=session['user_email']).first()
    return render_template('dev_profile.html', dev=dev)

# Rota para exibir o formulário de edição do perfil
@app.route('/dev/profile/edit', methods=['GET', 'POST'])
def edit_profile():
    dev = Dev.query.filter_by(email=session['user_email']).first()
    if request.method == 'POST':
        dev.name = request.form['name']
        dev.email = request.form['email']
        dev.cel = request.form['cel']
        dev.habilidades = request.form['habilidades']
        dev.cidade = request.form['cidade']
        dev.pais = request.form['pais']
        dev.disponibilidade = request.form['disponibilidade']
        dev.idiomas = request.form['idiomas']
        dev.objetivo_profissional = request.form['objetivo_profissional']
        
        # Se o dev fizer upload de um novo currículo (opcional)
        if 'cv_file' in request.files:
            cv_file = request.files['cv_file']
            if cv_file and cv_file.filename != '':
                cv_filename = secure_filename(cv_file.filename)
                cv_file.save(os.path.join(app.config['UPLOAD_FOLDER'], cv_filename))
                dev.cv_file = cv_filename
        

        # Salvar a foto de perfil
        if 'profile_picture' in request.files:
            profile_picture = request.files['profile_picture']
            if profile_picture and profile_picture.filename != '':
                picture_filename = secure_filename(profile_picture.filename)
                # Verificar o diretório
                picture_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_filename)
                print(f"Salvando imagem em: {picture_path}")  # Debug para verificar o caminho
                profile_picture.save(picture_path)
                dev.profile_picture = picture_filename



        db.session.commit()
        flash('Perfil atualizado com sucesso!', 'success')
        return redirect(url_for('dev_profile'))
    
    return render_template('edit_dev_profile.html', dev=dev)


@app.route('/download/<cv_file>')
def download_cv(cv_file):
    try:
        return send_from_directory(app.config['UPLOAD_FOLDER'], cv_file)
    except FileNotFoundError:
        flash('Arquivo não encontrado.', 'danger')
        return redirect(url_for('dev_profile'))
    
@app.route('/dev/favorite/<int:job_id>', methods=['POST'])
def favorite_job(job_id):
    if 'user_email' not in session:
        flash("Você precisa estar logado para favoritar vagas.", "danger")
        return redirect(url_for('dev_login'))

    dev = Dev.query.filter_by(email=session['user_email']).first()
    job = Job.query.get_or_404(job_id)

    # Verificar se o trabalho já está favoritado
    if job in dev.favorites:
        flash('Você já favoritou esta vaga.', 'warning')
    else:
        dev.favorites.append(job)
        db.session.commit()
        flash('Vaga favoritada com sucesso!', 'success')

    return redirect(url_for('dev_dashboard'))



@app.route('/dev/favorites')
def dev_favorites():
    if 'user_email' not in session:
        flash("Você precisa estar logado para ver suas vagas favoritas.", "danger")
        return redirect(url_for('dev_login'))

    dev = Dev.query.filter_by(email=session['user_email']).first()
    favorite_jobs = dev.favorites  # Obtém as vagas favoritedas pelo dev

    return render_template('dev_favorites.html', jobs=favorite_jobs)


@app.route('/dev/unfavorite/<int:job_id>', methods=['POST'])
def unfavorite_job(job_id):
    if 'user_email' not in session:
        flash("Você precisa estar logado para desfavoritar vagas.", "danger")
        return redirect(url_for('dev_login'))

    dev = Dev.query.filter_by(email=session['user_email']).first()
    job = Job.query.get_or_404(job_id)

    # Verificar se o trabalho está na lista de favoritos
    if job in dev.favorites:
        dev.favorites.remove(job)
        db.session.commit()
        flash('Vaga removida dos favoritos com sucesso!', 'success')
    else:
        flash('Você não favoritou esta vaga.', 'warning')

    return redirect(url_for('dev_dashboard'))



@app.route('/schedule_interview/<int:job_id>/<int:dev_id>', methods=["POST"])
def schedule_interview(job_id, dev_id):
    if 'empresa_email' not in session:
        flash("Você precisa estar logado como empresa para agendar entrevistas.", "danger")
        return redirect(url_for('empresa_login'))

    scheduled_time = request.form.get('scheduled_time')
    new_interview = Interview(
        job_id=job_id,
        dev_id=dev_id,
        scheduled_time=datetime.strptime(scheduled_time, '%Y-%m-%dT%H:%M')
    )
    db.session.add(new_interview)
    db.session.commit()
    flash("Entrevista agendada com sucesso!", "success")
    return redirect(url_for('empresa_candidaturas'))

@app.route('/dev/interviews', methods=["GET"])
def dev_interviews():
    if 'user_email' not in session:
        flash("Você precisa estar logado para ver suas entrevistas.", "danger")
        return redirect(url_for('dev_login'))

    dev = Dev.query.filter_by(email=session['user_email']).first()
    interviews = Interview.query.filter_by(dev_id=dev.id).all()
    
    return render_template('dev_interviews.html', interviews=interviews)

@app.route('/update_interview_status/<int:interview_id>', methods=["POST"])
def update_interview_status(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    interview.status = request.form.get('status')
    db.session.commit()
    flash('Status da entrevista atualizado!', 'success')
    return redirect(url_for('empresa_candidaturas'))

@app.route('/toggle_theme')
def toggle_theme():
    theme = request.args.get('theme', 'light')
    session['theme'] = theme
    return '', 204  # Retorna um código de sucesso sem conteúdo


#-----------------------------------------------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=6001)
