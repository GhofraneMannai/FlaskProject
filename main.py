from flask import Flask, render_template, request, redirect, url_for, session, flash,jsonify  
from flask_mysqldb import MySQL
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature, SignatureExpired

# Configure Flask-Mail

app = Flask(__name__, template_folder='template', static_url_path='/static', static_folder='static')
# Initialize Flask-Mail
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Replace with your mail server
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'ghofranemn22@gmail.com'  # Replace with your email
app.config['MAIL_PASSWORD'] = 'lexh jter nxjy ioxu'  # Replace with your email password
app.config['MAIL_DEFAULT_SENDER'] = 'your_email@example.com'

mail = Mail(app)

# Set the secret key to enable sessions
app.secret_key = 'your_secret_key_here'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'stage'
app.config['UPLOAD_FOLDER'] = '/static/faces/'

mysql = MySQL(app)

def generate_confirmation_token(email):
    s = Serializer(app.config['SECRET_KEY'])
    return s.dumps({'email': email}, salt='email-confirmation')

def confirm_token(token, expiration=3600):
    s = Serializer(app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt='email-confirmation', max_age=expiration)
    except (BadSignature, SignatureExpired):
        return None
    return data['email']
@app.route('/index')
def index():
    # Check if user is logged in and admin is connected
    if 'username' in session and session.get('admin_connected'):
        # Fetch username and email from session to display on index page
        username = session['username']
        mail = session['mail']  # Safely retrieve 'mail' from session with a default value
        return render_template('index.html', username=username, mail=mail)
    else:
        # If not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Fetch user from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
        user = cur.fetchone()
        cur.close()
        
        if user:
            print(user);
            # Store user info in session
            session['username'] = user[1]
            session['mail'] =user[3] # Storing email in session
            session['admin_connected'] = True  # Indicator that admin is connected
            # Redirect to index page
            return redirect(url_for('index'))
        else:
            # Invalid credentials
            error = "Invalid username or password"
    
    return render_template('pages/samples/login.html', error=error)


#Client
@app.route('/client')
def client():
    # Check if user is logged in and admin is connected
    if 'username' in session and session.get('admin_connected'):
        # Fetch username and email from session to display on index page
        username = session['username']
        mail = session['mail']  # Safely retrieve 'mail' from session with a default value
        
        # Fetch clients from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM clients")
        clients_data = cur.fetchall()
        cur.close()
        
        clients = []
        for client in clients_data:
            # Diviser la description en paragraphes
            paragraphs = client[5].split('\n')
            clients.append((client[0], client[2], client[1], client[3], client[4], paragraphs, client[6], client[7], client[8],client[9],client[10],client[11],client[12]))

        return render_template('client.html', username=username, mail=mail, clients=clients)
    else:
        # If not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    return redirect(url_for('login'))



@app.route('/add', methods=['POST'])
def add():
    if request.method == 'POST':
        errors = []

        # Get form data
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        company = request.form.get('company')
        address = request.form.get('address')
        phone = request.form.get('phone')
        dob = request.form.get('dob')
        deadline = request.form.get('deadline')
        poste = request.form.get('poste')
        title_project = request.form.get('title_project')
        description = request.form.get('description')
        decisionMail="Not Confirmed"
        badgeMail="warning"
        badgeValidate="warning"
        decisionvalidate="Not Validated"
        # Validation checks
        if not name:
            errors.append('Name is required.')
        if not surname:
            errors.append('Surname is required.')
        if not company:
            errors.append('Company is required.')
        if not dob:
            errors.append('Date of Birth is required.')
        if not deadline:
            errors.append('Deadline is required.')
        if not poste:
            errors.append('Post is required.')
        if not address:
            errors.append('Address is required.')
        if not email:
            errors.append('Email is required.')
        if not title_project:
            errors.append('The title of the project is required.')
        if not description:
            errors.append('Description is required.')
        if not phone:
            errors.append('Phone number is required.')
        elif len(phone) < 9:
            errors.append('Phone number must be at least 9 digits.')

        # Parse and validate dates
        try:
            dob_date = datetime.strptime(dob, '%Y-%m-%d')
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
            current_date = datetime.now()

            if dob_date >= current_date:
                errors.append('Date of birth must be in the past.')
            if deadline_date <= current_date:
                errors.append('Deadline must be in the future.')

        except ValueError:
            errors.append('Invalid date format. Use YYYY-MM-DD.')

        # Return errors if any
        if errors:
            return jsonify({'status': 'error', 'errors': errors})

        # Handle image upload
        image = request.files.get('image')
        if image:
            image_name = image.filename
            image_path = os.path.join('static', 'faces', image_name)

            # Ensure directory exists and save the image
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        else:
            image_name = None  # Set image_name to None if no image is provided

        # Insert data into MySQL database
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                INSERT INTO clients (
                    nom, prenom, nomEntreprise, email, adress, phone, dateBirth, deadline, poste, titleprojet, description, image,decisionMail,badgeMail,decisionValidate,badgeValidate
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s , %s , %s , %s , %s)
                """, 
                (name, surname, company, email, address, phone, dob, deadline, poste, title_project, description, image_name,decisionMail,badgeMail,decisionvalidate,badgeValidate))
            mysql.connection.commit()
            cur.close()

            token = generate_confirmation_token(email)
            confirmation_url = url_for('confirm_email', token=token, _external=True)

        # Send confirmation email
            msg = Message('Client Added Successfully',sender=app.config['MAIL_DEFAULT_SENDER'],recipients=[email])
            msg.html = render_template('confirmation_email.html', name=name, confirmation_url=confirmation_url)
            mail.send(msg)


            return jsonify({'status': 'success', 'redirect_url': url_for('client')})

        except Exception as e:
            return jsonify({'status': 'error', 'errors': [str(e)]})

    return redirect(url_for('index'))



@app.route('/confirm/<token>')
def confirm_email(token):
    email = confirm_token(token)
    if email:
        try:
            # Update the database to confirm the email
            cur = mysql.connection.cursor()
            cur.execute("""UPDATE clients SET decisionMail = %s, badgeMail = %s WHERE email = %s""", ('Confirmed', 'success', email))
            mysql.connection.commit()
            cur.close()

            # Render a confirmation page
            return render_template('confirmation_success.html', name=email)
        except Exception as e:
            return render_template('confirmation_error.html', message=str(e))
    else:
        return render_template('confirmation_error.html', message="The confirmation link is invalid or has expired.")

@app.route('/submit_details', methods=['POST'])
def submitClient():
    if request.method == 'POST':
        errors = []
        # Get form data
        reunionDate = request.form.get('reunionDate')
        client_id = request.form.get('clientId')

        # Validation checks
        if not reunionDate:
            errors.append('Date of reunion is required.')

        try:
            reunionDate_date = datetime.strptime(reunionDate, '%Y-%m-%d')
            current_date = datetime.now()
            if reunionDate_date <= current_date:
                errors.append('Date of the reunion must be in the future.')
        except ValueError:
            errors.append('Invalid date format. Use YYYY-MM-DD.')

        # Return errors if any
        if errors:
            return jsonify({'status': 'error', 'errors': errors})

        # Handle image upload
        devis = request.files.get('devisImage')
        if devis:
            devis_name = secure_filename(devis.filename)
            devis_path = os.path.join('static', 'uploads', devis_name)

            # Ensure directory exists and save the devis
            os.makedirs(os.path.dirname(devis_path), exist_ok=True)
            devis.save(devis_path)
        else:
            devis_name = None

        # Insert data into MySQL database
        try:
            cur = mysql.connection.cursor()
            cur.execute("""
                UPDATE clients
                SET reunionDate = %s, devis_name = %s, decisionValidate = %s
                WHERE id = %s
                """, (reunionDate, devis_name, "Validate", client_id))
            mysql.connection.commit()
            cur.close()

            # Retrieve email to send confirmation
            cursor = mysql.connection.cursor()
            query = "SELECT email FROM clients WHERE id = %s"
            cursor.execute(query, (client_id,))
            result = cursor.fetchone()
            cursor.close()

            # Check if result is not None and send email
            if result and result[0]:
                email = result[0]
                msg = Message('Client Details Updated', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
                msg.html = render_template('devis.html', reunionDate=reunionDate, devis_name=devis_name)
                mail.send(msg)

            flash('Details submitted successfully!', 'success')
            return jsonify({'status': 'success', 'redirect_url': url_for('index')})
        except Exception as e:
            flash(f'Error: {str(e)}', 'danger')
            return jsonify({'status': 'error', 'errors': [str(e)]})

    return redirect(url_for('index'))

@app.route('/update', methods=['POST'])
def update():
    client_id = request.form['client_id']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    company = request.form['company']
    address = request.form['address']
    phone = request.form['phone']
    dob = request.form['dob']
    deadline = request.form['deadline']
    poste = request.form['poste']
    title_project = request.form['title_project']
    description = request.form['description']

    # Charger et sauvegarder l'image si elle est présente
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_name = image.filename
            image_path = os.path.join('static', 'faces', image_name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        else:
            image_name = None
    else:
        image_name = None

    # Effectuer la mise à jour dans la base de données
    cur = mysql.connection.cursor()
    update_query = """
        UPDATE clients
        SET nom = %s, prenom = %s, nomEntreprise = %s, email = %s, adress = %s,
            phone = %s, dateBirth = %s, deadline = %s, poste = %s,
            titleprojet = %s, description = %s, image = %s
        WHERE id = %s
    """
    cur.execute(update_query, (name, surname, company, email, address, phone, dob,
                               deadline, poste, title_project, description, image_name, client_id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('client'))



@app.route('/delete/<int:client_id>', methods=['DELETE'])
def delete_client(client_id):
        try:
            # Connect to MySQL and delete the client record
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM clients WHERE id = %s", (client_id,))
            mysql.connection.commit()
            cur.close()

            return jsonify({'status': 'success', 'message': 'Client deleted successfully'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})


#Candidate
@app.route('/candidat')
def candidat():
    # Check if user is logged in and admin is connected
    if 'username' in session and session.get('admin_connected'):
        # Fetch username and email from session to display on index page
        username = session['username']
        mail = session['mail']  # Safely retrieve 'mail' from session with a default value
        
        # Fetch clients from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM candidats")
        candidat_data = cur.fetchall()
        cur.close()
        
        candidats = []
        for candidat in candidat_data:
            # Diviser la description en paragraphes
            commentaires = candidat[7].split('\n')
            candidats.append((candidat[0], candidat[1], candidat[2], candidat[3], candidat[4], candidat[5], candidat[6], commentaires))

        return render_template('candidat.html', username=username, mail=mail, candidats=candidats)
    else:
        # If not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/addCandidat', methods=['POST'])
def addCandidat():
    if request.method == 'POST':
        errors = []

        name = request.form['name']
        surname = request.form['surname']
        email = request.form['email']
        phone = request.form['phone']
        commentaire = request.form['commentaire']

        if not name:
            errors.append('Name is required.')
        if not surname:
            errors.append('Surname is required.')
        if not email:
            errors.append('Email is required.')
        if not commentaire:
            errors.append('Commentaire is required.')
        if not phone:
            errors.append('Phone number is required.')
        elif len(phone) < 9:
            errors.append('Phone number must be at least 9 digits.')

        if errors:
            return jsonify({'status': 'error', 'errors': errors})

        image = request.files['image']
        # Define the path where the image will be saved
        image_name = image.filename
        image_path = os.path.join('static', 'faces', image_name)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Save the image
        image.save(image_path)
        print(errors);


        cv = request.files['cv']
        
        cv_name = cv.filename
        cv_path = os.path.join('static', 'CV', cv_name)

      
        os.makedirs(os.path.dirname(cv_path), exist_ok=True)

       
        cv.save(cv_path)
        print(errors);

        # Insert into MySQL database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO candidats (
                nom, prenom,image,email, telephone, CV, Commentaire
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (name, surname, image_name, email , phone,  cv_name ,commentaire))
        mysql.connection.commit()
        cur.close()

        return jsonify({'status': 'success'})

    return redirect(url_for('index'))


@app.route('/updateCandidat', methods=['POST'])
def updateCandidat():
    candidat_id = request.form['candidat_id']
    name = request.form['name']
    surname = request.form['surname']
    email = request.form['email']
    phone = request.form['phone']
    commentaire = request.form['commentaire']

    # Handle image upload if present
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_name = image.filename
            image_path = os.path.join('static', 'faces', image_name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        else:
            image_name = None
    else:
        image_name = None

    # Handle CV upload if present
    if 'cv' in request.files:
        cv = request.files['cv']
        if cv.filename != '':
            cv_name = cv.filename
            cv_path = os.path.join('static', 'CV', cv_name)
            os.makedirs(os.path.dirname(cv_path), exist_ok=True)
            cv.save(cv_path)
        else:
            cv_name = None
    else:
        cv_name = None

    # Execute the database update
    cur = mysql.connection.cursor()
    update_query = """
        UPDATE candidats
        SET nom = %s, prenom = %s, email = %s, telephone = %s, commentaire = %s, image = %s, cv = %s
        WHERE id = %s
    """
    cur.execute(update_query, (name, surname, email, phone, commentaire, image_name, cv_name, candidat_id))
    mysql.connection.commit()
    cur.close()

    return redirect(url_for('candidat'))



@app.route('/deleteCandidat/<int:candidat_id>', methods=['DELETE'])
def delete_candidat(candidat_id):
        print(candidat_id)
        try:
            # Connect to MySQL and delete the client record
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM candidats WHERE id = %s", (candidat_id,))
            mysql.connection.commit()
            cur.close()

            return jsonify({'status': 'success', 'message': 'Candidat deleted successfully'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})


#Department
@app.route('/departement')
def department():
    # Check if user is logged in and admin is connected
    if 'username' in session and session.get('admin_connected'):
        # Fetch username and email from session to display on index page
        username = session['username']
        mail = session['mail']  # Safely retrieve 'mail' from session with a default value
        
        # Fetch departements from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM departements")
        departement_data = cur.fetchall()
        cur.close()
        
        departements = []
        for departement in departement_data:
            departements.append((departement[0], departement[1], departement[2], departement[3]))

        return render_template('departement.html', username=username, mail=mail, departements=departements)
    else:
        # If not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/addDepartement', methods=['POST'])
def addDepartement():
    if request.method == 'POST':
        errors = []

        name = request.form['name']
        head = request.form['head']

        if not name:
            errors.append('Name of department is required.')
        if not head:
            errors.append('Head Of Department is required.')
        if errors:
            return jsonify({'status': 'error', 'errors': errors})

        image = request.files['image']
        # Define the path where the image will be saved
        image_name = image.filename
        image_path = os.path.join('static', 'faces', image_name)

        # Ensure the directory exists
        os.makedirs(os.path.dirname(image_path), exist_ok=True)

        # Save the image
        image.save(image_path)
        print(errors)

    try:
        # Insert into MySQL database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO departements (
                name, dirigeant,image
            ) VALUES (%s, %s, %s)
            """,
            (name, head, image_name))
        mysql.connection.commit()
        cur.close()
        return jsonify({'status': 'success'})

    except Exception as e:
        return jsonify({'status': 'error', 'errors': [str(e)]})

    return redirect(url_for('departement'))

@app.route('/updateDepartement', methods=['POST'])
def updateDepartement():
    depart_id = request.form['depart_id']
    name = request.form['name']
    head = request.form['head']

    # Charger et sauvegarder l'image si elle est présente
    if 'image' in request.files:
        image = request.files['image']
        if image.filename != '':
            image_name = image.filename
            image_path = os.path.join('static', 'faces', image_name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        else:
            image_name = None
    else:
        image_name = None

    # Effectuer la mise à jour dans la base de données
    cur = mysql.connection.cursor()
    update_query = """
        UPDATE departements
        SET name = %s, dirigeant = %s, image = %s
        WHERE id = %s
    """
    cur.execute(update_query, (name, head, image_name, depart_id))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('department'))


@app.route('/deleteDepartement/<int:depart_id>', methods=['DELETE'])
def delete_departement(depart_id):
        print(depart_id)
        try:
            # Connect to MySQL and delete the client record
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM departements WHERE id = %s", (depart_id,))
            mysql.connection.commit()
            cur.close()

            return jsonify({'status': 'success', 'message': 'Department deleted successfully'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})



#Member
@app.route('/member')
def member():
    # Check if user is logged in and admin is connected
    if 'username' in session and session.get('admin_connected'):
        # Fetch username and email from session to display on index page
        username = session['username']
        mail = session['mail']  # Safely retrieve 'mail' from session with a default value
        
        # Fetch members from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM members")
        members_data = cur.fetchall()
        cur.close()
        # Fetch departments from database
        cur = mysql.connection.cursor()
        cur.execute("SELECT id, name FROM departements")
        departement_data = cur.fetchall()
        cur.close()
        
        members = []
        for member in members_data:
            # Diviser la description en paragraphes
            description = member[5].split('\n')
            members.append((member[0], member[1], member[2], member[3], member[4], description, member[6], member[7], member[8],member[9],member[10],member[11],member[12]))

        return render_template('member.html', username=username, mail=mail, members=members,departments=departement_data)
    else:
        # If not logged in, redirect to login page
        return redirect(url_for('login'))

@app.route('/addMember', methods=['POST'])
def addMember():
    if request.method == 'POST':
        errors = []

        # Collect form data
        name = request.form.get('name')
        surname = request.form.get('surname')
        email = request.form.get('email')
        phone = request.form.get('phone')
        description = request.form.get('description')
        job = request.form.get('job')
        dobstr = request.form.get('dob')
        department_id = request.form.get('department')
        address = request.form.get('address')
        dateJoin = datetime.now().strftime('%Y-%m-%d')
        sex = request.form.get('sex')
        salary = request.form.get('salary')

        # Validate required fields
        if not name:
            errors.append('Name is required.')
        if not surname:
            errors.append('Surname is required.')
        if not email:
            errors.append('Email is required.')
        if not department_id:
            errors.append('Department is required.')
        if not description:
            errors.append('Description is required.')
        if not sex:
            errors.append('Sex is required.')
        if not job:
            errors.append('Job is required.')
        if not phone:
            errors.append('Phone number is required.')
        else:
            try:
                phone = int(phone)
                if len(str(phone)) < 9:
                    errors.append('Phone number must be at least 9 digits.')
            except ValueError:
                errors.append('Phone number must be a valid integer.')

        if salary:
            try:
                salary = float(salary)
            except ValueError:
                errors.append('Salary must be a valid float number.')

        # Validate date of birth
        try:
            dob = datetime.strptime(dobstr, '%Y-%m-%d')
            today = datetime.now()
            if dob >= today:
                errors.append('Date of birth must be less than today\'s date.')
        except ValueError:
            errors.append('Date of birth must be in the format YYYY-MM-DD.')

        if errors:
            return jsonify({'status': 'error', 'errors': errors})

        # Handle image upload
        image = request.files.get('image')
        if image:
            image_name = image.filename
            image_path = os.path.join('static', 'faces', image_name)
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image.save(image_path)
        else:
            errors.append('Image is required.')
            return jsonify({'status': 'error', 'errors': errors})

        # Insert into MySQL database
        cur = mysql.connection.cursor()
        cur.execute("""
            INSERT INTO members (
                nom, prenom, image, email, description, poste, telephone, dateNaissance, adresse, dateJoin, sex, salaire, department_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (name, surname, image_name, email, description, job, phone, dob, address, dateJoin, sex, salary, department_id))
        mysql.connection.commit()
        cur.close()

        # Redirect to the /member page after successful insertion
        return jsonify({'status': 'success', 'redirect_url': url_for('member')})

    return redirect(url_for('index'))

@app.route('/deleteMember/<int:memb_id>', methods=['DELETE'])
def delete_member(memb_id):
        print(memb_id)
        try:
            # Connect to MySQL and delete the client record
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM members WHERE id = %s", (memb_id,))
            mysql.connection.commit()
            cur.close()

            return jsonify({'status': 'success', 'message': 'Member deleted successfully'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})


@app.route('/dashboard')
def dashboard():
    # Check if user is logged in and admin is connected
    if 'username' in session and session.get('admin_connected'):
        # Fetch username and email from session
        username = session['username']
        mail = session.get('mail', '')  # Safely retrieve 'mail' from session with a default value
        
        try:
            # Fetch clients and contacts from database
            cur = mysql.connection.cursor()
            
            # Fetch clients
            cur.execute("SELECT * FROM clients")
            clients_data = cur.fetchall()
            
            # Fetch contacts
            cur.execute("SELECT * FROM contact")
            contacts_data = cur.fetchall()
            
            cur.close()
            
            # Process clients
            clients = []
            for client in clients_data:
                paragraphs = client[5].split('\n')
                clients.append((client[0], client[2], client[1], client[3], client[4], paragraphs, client[6], client[7], client[8], client[9], client[10], client[11], client[12], client[13], client[14], client[15], client[16], client[17], client[18]))
            
            # Process contacts
            contacts = []
            for contact in contacts_data:
                messages = contact[4].split('\n')
                contacts.append((contact[0], contact[1], contact[2], contact[3], messages, contact[5], contact[6]))
            
        except Exception as e:
            # Handle database error (log it and/or notify admin)
            print(f"An error occurred: {e}")
            return redirect(url_for('error_page'))
        
        # Render dashboard template with clients and contacts
        return render_template('dashboard.html', username=username, mail=mail, clients=clients, contacts=contacts)
    
    else:
        # If not logged in, redirect to login page
        return redirect(url_for('login'))


@app.route('/reply', methods=['POST'])
def reply():
    errors = []

    # Get form data
    answer = request.form.get('answer')
    contact_id = request.form.get('contactId')

    # Validation checks
    if not answer:
        errors.append('Answer is required.')
    if not contact_id or not contact_id.isdigit():
        errors.append('Valid contact ID is required.')

    # Return errors if any
    if errors:
        return jsonify({'status': 'error', 'errors': errors})

    try:
        # Retrieve email before trying to save the response
        with mysql.connection.cursor() as cursor:
            cursor.execute("SELECT email FROM contact WHERE id = %s", (contact_id,))
            result = cursor.fetchone()

        # Check if email is retrieved successfully
        if not result or not result[0]:
            return jsonify({'status': 'error', 'errors': ['Email not found for this contact.']})

        email = result[0]

        # Attempt to send the email
        msg = Message('Answer', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
        msg.html = render_template('answer.html', answer=answer)
        mail.send(msg)

        # If the email is sent successfully, insert the response and update the status
        with mysql.connection.cursor() as cur:
            # Insert the response into the reponse table
            cur.execute("""
            INSERT INTO reponse (message, clientId) 
            VALUES (%s, %s)
            """, (answer, contact_id))

            # Update the status of the contact to 'done'
            cur.execute("""
            UPDATE contact SET status = 'done' WHERE id = %s
            """, (contact_id,))

            # Commit the changes to the database
            mysql.connection.commit()

        flash('Details submitted successfully!', 'success')
        return jsonify({'status': 'success', 'redirect_url': url_for('index')})

    except Exception as e:
        # Log error details for debugging
        flash(f'Error: {str(e)}', 'danger')
        return jsonify({'status': 'error', 'errors': [str(e)]})

    return redirect(url_for('index'))

@app.route('/deleteContact/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
        try:
            # Connect to MySQL and delete the client record
            cur = mysql.connection.cursor()
            cur.execute("DELETE FROM contact WHERE id = %s", (contact_id,))
            mysql.connection.commit()
            cur.close()

            return jsonify({'status': 'success', 'message': 'contact deleted successfully'})

        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})



if __name__ == '__main__':
    app.run(debug=True)