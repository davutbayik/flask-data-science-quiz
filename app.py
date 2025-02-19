from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

CORRECT_ANSWERS = ["B", "A", "B", "D", "C"]

def checkAnswers(answer_list):
    
    score = 0
    for user_answer, correct_answer in zip(answer_list, CORRECT_ANSWERS):
        if user_answer == correct_answer:
            score += (100/len(CORRECT_ANSWERS))
    
    return score

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_scores.db'
db = SQLAlchemy(app)

# Create Users Model
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=False, nullable=False)
    score = db.Column(db.Integer, unique=False, nullable=False)

with app.app_context():
    db.create_all()

def fetchAllBest():
    result = db.session.execute(db.select(User.score)).scalars().fetchall()
    if len(result) == 0:
        return "-"
    else:
        return f'{max(result)}%'

def fetchUserBest(username):
    result = db.session.execute(db.select(User.score).where(User.user_name == username)).scalars().fetchall()
    if len(result) == 0:
        return "-"
    else:
        return f'{max(result)}%'

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template(
        'index.html', 
        all_best=fetchAllBest()
        )

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    
    if request.method == 'POST':
        user_name = request.form["username"]
    else:
        user_name = None
    
    try:
        request.form["index_submit"]
        return render_template(
            'quiz.html', 
            name=user_name,
            user_best=fetchUserBest(user_name),
            all_best=fetchAllBest()
            )
    
    except:
        return redirect('/')
    
@app.route('/result', methods=['GET', 'POST'])
def result():
    
    if request.method == 'POST':
        
        user_name = request.form["username"]
        
        user_answers = [request.form[f"question{i}"] for i in range(1, len(CORRECT_ANSWERS)+1)]
        quiz_score = checkAnswers(user_answers)
                
        user_score = User(
            user_name = request.form["username"],
            score = quiz_score,
        )

        db.session.add(user_score)
        db.session.commit()
    
    try:
        request.form["quiz_submit"]
        return render_template(
            'result.html',
            name=user_name,
            quiz_result=f'{int(quiz_score)}%',
            user_best=fetchUserBest(user_name),
            all_best=fetchAllBest()
            )
    except:
        return redirect('/')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)