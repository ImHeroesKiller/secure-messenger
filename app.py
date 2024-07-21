from flask import Flask, render_template, request, redirect, url_for
from cryptography.fernet import Fernet
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)

# Generate a key for encryption
key = Fernet.generate_key()
cipher_suite = Fernet(key)

engine = create_engine('sqlite:///messages.db')
Base = declarative_base()
Session = sessionmaker(bind=engine)
session = Session()

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True)
    content = Column(String)

Base.metadata.create_all(engine)

@app.route('/')
def index():
    messages = session.query(Message).all()
    decrypted_messages = [(msg.id, cipher_suite.decrypt(msg.content.encode('utf-8')).decode('utf-8')) for msg in messages]
    return render_template('index.html', messages=decrypted_messages)

@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    encrypted_message = cipher_suite.encrypt(message.encode('utf-8')).decode('utf-8')
    new_message = Message(content=encrypted_message)
    session.add(new_message)
    session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

