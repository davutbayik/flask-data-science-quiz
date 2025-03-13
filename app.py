#Import necessary libraries for the project
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

#Answer key of the test
CORRECT_ANSWERS = ["D", "A", "B", "D", "C", "B", "B", "C", "B", "B", "B", "A", "A", "A", "B", "B", "A", "B", "C", "C"]

def checkAnswers(answer_list):
    
    '''Calculate Score Function
    Checks the user's answers with the answer key and calculates a final score of the test
    '''
    
    score = 0
    for user_answer, correct_answer in zip(answer_list, CORRECT_ANSWERS):
        if user_answer == correct_answer:
            score += (100/len(CORRECT_ANSWERS))
    
    return round(score,2)

#Initialize the flask application
app = Flask(__name__)

#Configure the flaskalcemly sql URI with the sqlite databases
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_scores.db'
db = SQLAlchemy(app)

# Create Users Model for the database
class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(100), unique=False, nullable=False)
    score = db.Column(db.Integer, unique=False, nullable=False)

#Create the database instance
with app.app_context():
    db.create_all()

def fetchAllBest():
    
    '''Global High Score Function
    Fetches the global high score to display on the screen from the database
    '''

    result = db.session.execute(db.select(User.score)).scalars().fetchall()
    if len(result) == 0:
        return "-"
    else:
        return f'{max(result)}%'

def fetchUserBest(username):
    
    '''User Best Function
    Fetches the user's personal high score to display on the screen from the database depending on the name input
    '''
    
    result = db.session.execute(db.select(User.score).where(User.user_name == username)).scalars().fetchall()
    if len(result) == 0:
        return "-"
    else:
        return f'{max(result)}%'


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    '''Index Page
    Route the index page with GET and POST methods. We will use the POST method for the backend operations of this project
    Fetch the global high score and display on the index page
    '''

    return render_template(
        'index.html', 
        all_best=fetchAllBest()
        )

@app.route('/quiz', methods=['GET', 'POST'])
def quiz():
    
    '''Quiz Page
    Fetch the username from the POST request of the index page and global and personal best scores from the databese
    Render the quiz html page and if not clicked the continue button from the previous page, redirect to the index page
    '''

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
    
    '''Results Page
    Fetch the username, user answers from the POST request of the quiz page
    Check the answers and calculate a final score
    Render the results html page and if not clicked the submit answers button from the previous page, redirect to the index page
    '''
    
    if request.method == 'POST':
        
        user_name = request.form["username"]
        
        #Get all the questions' answers from the POST request
        user_answers = [request.form[f"question{i}"] for i in range(1, len(CORRECT_ANSWERS)+1)]
        quiz_score = checkAnswers(user_answers)
        
        #Inserting the test result to the database
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

#Main function to start the Flask project
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)