from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
import nltk
import random
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = Flask(__name__, static_folder='assets', template_folder='.')

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct full paths to the text files
ghalib_path = os.path.join(script_dir, 'ghalib.txt')
iqbal_path = os.path.join(script_dir, 'iqbal.txt')
password_path = os.path.join(script_dir, 'password.txt')


nltk.download('punkt')


# Read the content of the files
with open(ghalib_path, 'r', encoding='utf-8') as file:
    data2 = file.readlines()
with open(iqbal_path, 'r', encoding='utf-8') as file:
    data3 = file.readlines()

data = data2 + data3
data = [x for x in data if x != '\n']
data = [x for x in data if x != '‘']

# Tokenize
tokenized_sentences = []
for sentence in data:
    tokens = nltk.word_tokenize(sentence)
    tokenized_sentences.extend([token for token in tokens if len(token) > 1])

# Generate n-grams
bigrams = nltk.ngrams(tokenized_sentences, 3)
bigramFD = nltk.FreqDist(bigrams)

# Poetry generation functions (unchanged)
def Misra_e_oola():
    verse_length = random.randint(7, 10)
    generated_verse = ""
    first_word = random.choice(tokenized_sentences)
    generated_verse += first_word + " "

    for _ in range(verse_length - 1):
        max_freq = 0
        next_word = ""

        for token in bigramFD.items():
            if token[0][0] == first_word and token[1] > max_freq:
                next_word = token[0][1]
                max_freq = token[1]

        if next_word == "":
            break

        generated_verse += next_word + " "
        first_word = next_word

    return generated_verse.strip()

def Misra_e_Doom1(last_word, check):
    verse_length = random.randint(7, 10)
    generated_verse = last_word + " "

    for _ in range(verse_length - 1):
        max_freq = 0
        prev_word = ""

        for token in bigramFD.items():
            if token[0][1] == last_word and token[1] > max_freq:
                prev_word = token[0][0]
                max_freq = token[1]

        if prev_word == "":
            break

        generated_verse = prev_word + " " + generated_verse
        last_word = prev_word

    return generated_verse.strip()

def Rhyme(word):
    for token in bigramFD.items():
        a = token[0][1]
        if a[int(len(a) / 3):] == word[int(len(word) / 3):] and a != word:
            return a, False
    return word, True

# Read SMTP credentials from password.txt
def read_smtp_credentials():
    with open(password_path, 'r') as file:
        lines = file.readlines()
        smtp_username = lines[0].strip()
        smtp_password = lines[1].strip()
    return smtp_username, smtp_password

# Get SMTP credentials
smtp_username, smtp_password = read_smtp_credentials()

# Send email function (modified to use directly read credentials)
def send_email(name, email, comment):
    # Create the email message
    msg = MIMEMultipart()
    msg['From'] = smtp_username
    msg['To'] = "iltafabdulahad@gmail.com"  # Receiver's email
    msg['Subject'] = f"New Contact Form Submission from {name}"

    # Compose the body of the email (name, email, message)
    body = f"Name: {name}\nEmail: {email}\n\nMessage:\n{comment}"
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()  # Secure the connection
        server.login(smtp_username, smtp_password)

        # Send the email
        server.sendmail(smtp_username, "iltafabdulahad@gmail.com", msg.as_string())
        print("Email sent successfully!")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        server.quit()  # Close the SMTP connection

# Flask routes (unchanged)
@app.route('/generate_poetry', methods=['GET'])
def generate_poetry():
    first_verse = Misra_e_oola()
    second_verse = Misra_e_Doom1(first_verse.split()[-1], False)

    rhyme_word, check = Rhyme(second_verse.split()[-1])
    third_verse = Misra_e_Doom1(rhyme_word, check)

    rhyme_word, check = Rhyme(third_verse.split()[-1])
    fourth_verse = Misra_e_Doom1(rhyme_word, False)

    return jsonify({"poetry": [first_verse, second_verse, third_verse, fourth_verse]})

@app.route('/send_email', methods=['POST'])
def handle_form_submission():
    name = request.form['name']
    email = request.form['email']
    comment = request.form['comment']

    try:
        send_email(name, email, comment)
        flash('Your message has been sent successfully!', 'success')
    except Exception as e:
        flash(f'An error occurred: {e}', 'danger')

    return redirect(url_for('index'))

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'  # Change this to your preferred secret key
    app.run()
