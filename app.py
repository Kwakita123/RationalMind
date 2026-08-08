

from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib
from datetime import datetime
from analysis import analyze_reflection
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection

lessons = [

# Emotional Intelligence

{
"category": "Emotional Intelligence",
"title": "Understanding Emotions",
"description":
"Emotions are signals that provide information about our experiences. They influence decisions, but they do not have to control our actions.",
"question":
"What information is this emotion providing?"
},


{
"category": "Emotional Intelligence",
"title": "Emotional Regulation",
"description":
"Regulation does not mean eliminating emotions. It means creating enough space to respond intentionally.",
"question":
"How can I acknowledge this emotion without immediately reacting?"
},



# Psychology

{
"category": "Psychology",
"title": "Cognitive Biases",
"description":
"The human mind uses shortcuts to make decisions efficiently. These shortcuts can sometimes create inaccurate interpretations.",
"question":
"What assumptions might be influencing my perspective?"
},


{
"category": "Psychology",
"title": "Cognitive Distortions",
"description":
"People sometimes develop inaccurate thinking patterns such as all-or-nothing thinking or overgeneralization.",
"question":
"Am I viewing this situation more negatively than the evidence suggests?"
},



# Philosophy

{
"category": "Philosophy",
"title": "Stoic Control",
"description":
"Stoicism emphasizes separating what we can control from what we cannot control.",
"question":
"What part of this situation is actually within my control?"
},


{
"category": "Philosophy",
"title": "Identity and Growth",
"description":
"Personal development requires seeing yourself as adaptable rather than defined permanently by past experiences.",
"question":
"What type of person am I trying to become?"
},



# Decision Science

{
"category": "Decision Science",
"title": "Opportunity Cost",
"description":
"Every choice involves giving something else up. Understanding tradeoffs improves decision quality.",
"question":
"What am I choosing, and what am I sacrificing?"
},


{
"category": "Decision Science",
"title": "Long-Term Thinking",
"description":
"Good decisions consider consequences beyond immediate rewards or emotions.",
"question":
"How will this decision affect my future self?"
},



# Rational Thinking

{
"category": "Rational Thinking",
"title": "Facts vs Interpretation",
"description":
"Events and our interpretations of events are different. Separating them improves clarity.",
"question":
"What happened, and what story did I create about it?"
}

]

app = Flask(__name__)

app.secret_key = "rationalmind_secret_key"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")



# -----------------------------
# DATABASE
# -----------------------------
def init_db():

    connection = sqlite3.connect(DATABASE)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS reflections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            situation TEXT,
            emotion TEXT,
            intensity TEXT,
            thought TEXT,
            evidence TEXT,
            alternative TEXT,
            response TEXT,
            insights TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    connection.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        situation TEXT,
        goal TEXT,
        facts TEXT,
        assumptions TEXT,
        option_a TEXT,
        benefits_a TEXT,
        drawbacks_a TEXT,
        option_b TEXT,
        benefits_b TEXT,
        drawbacks_b TEXT,
        short_term TEXT,
        long_term TEXT,
        decision_choice TEXT,
        reasoning TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

    connection.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            rating INTEGER NOT NULL,
            comment TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()

@app.context_processor
def inject_user():

    return {
        "logged_in": "user_id" in session,
        "username": session.get("username")
    }
# -----------------------------
# HOME
# -----------------------------

@app.route("/")
def home():

    return render_template("index.html")


# -----------------------------
# EMOTIONAL CHECK-IN
# -----------------------------

@app.route("/check-in", methods=["GET", "POST"])
def check_in():

    if "user_id" not in session:
        return redirect("/login")

    reflection = None

    if request.method == "POST":

        situation = request.form.get("situation")
        emotion = request.form.get("emotion")
        intensity = request.form.get("intensity")
        thought = request.form.get("thought")
        evidence = request.form.get("evidence")
        counter_evidence = request.form.get("counter_evidence")
        alternative = request.form.get("alternative")
        response = request.form.get("response")

        reflection = {
            "situation": situation,
            "emotion": emotion,
            "intensity": intensity,
            "thought": thought,
            "evidence": evidence,
            "counter_evidence": counter_evidence,
            "alternative": alternative,
            "response": response,
            "insights": analyze_reflection(emotion,thought,response)
        }

    return render_template(
        "check_in.html",
        reflection=reflection
    )

# -----------------------------
# RATIONAL DECISION
# -----------------------------

@app.route("/decision", methods=["GET", "POST"])
def decision():

    if "user_id" not in session:
        return redirect("/login")

    result = None

    if request.method == "POST":

        situation = request.form.get("situation")
        goal = request.form.get("goal")
        facts = request.form.get("facts")
        assumptions = request.form.get("assumptions")

        option_a = request.form.get("option_a")
        option_b = request.form.get("option_b")

        benefits_a = request.form.get("benefits_a")
        drawbacks_a = request.form.get("drawbacks_a")

        benefits_b = request.form.get("benefits_b")
        drawbacks_b = request.form.get("drawbacks_b")

        short_term = request.form.get("short_term")
        long_term = request.form.get("long_term")

        decision_choice = request.form.get("decision_choice")
        reasoning = request.form.get("reasoning")

        connection = sqlite3.connect(DATABASE)

        connection.execute(
            """
            INSERT INTO decisions (
                user_id,
                situation,
                goal,
                facts,
                assumptions,
                option_a,
                benefits_a,
                drawbacks_a,
                option_b,
                benefits_b,
                drawbacks_b,
                short_term,
                long_term,
                decision_choice,
                reasoning
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                situation,
                goal,
                facts,
                assumptions,
                option_a,
                benefits_a,
                drawbacks_a,
                option_b,
                benefits_b,
                drawbacks_b,
                short_term,
                long_term,
                decision_choice,
                reasoning
            )
        )

        connection.commit()
        connection.close()

        result = {
            "situation": situation,
            "goal": goal,
            "facts": facts,
            "assumptions": assumptions,
            "option_a": option_a,
            "option_b": option_b,
            "benefits_a": benefits_a,
            "drawbacks_a": drawbacks_a,
            "benefits_b": benefits_b,
            "drawbacks_b": drawbacks_b,
            "short_term": short_term,
            "long_term": long_term,
            "decision_choice": decision_choice,
            "reasoning": reasoning
        }

    return render_template(
        "decision.html",
        result=result
    )
# -----------------------------
# STRESS RESET
# -----------------------------

@app.route("/reset")
def reset():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("reset.html")

@app.route("/explore")
def explore():

    return render_template(
        "explore.html",
        lessons=lessons
    )

# -----------------------------
# DAILY REFLECTION
# -----------------------------

@app.route("/reflection", methods=["GET", "POST"])
def reflection():

    if "user_id" not in session:
        return redirect("/login")

    message = None

    if request.method == "POST":

        situation = request.form.get("situation")
        emotion = request.form.get("emotion")
        intensity = request.form.get("intensity")
        thought = request.form.get("thought")

        supporting_evidence = request.form.get("evidence")
        challenging_evidence = request.form.get("challenging_evidence")

        alternative = request.form.get("alternative")
        response = request.form.get("response")
        insights = request.form.get("insights")

        # Store both types of evidence together
        evidence = (
            "Supports: " + (supporting_evidence or "") +
            "\n\nChallenges: " + (challenging_evidence or "")
        )

        connection = sqlite3.connect(DATABASE)

        connection.execute(
            """
            INSERT INTO reflections
            (
                user_id,
                situation,
                emotion,
                intensity,
                thought,
                evidence,
                alternative,
                response,
                insights
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                situation,
                emotion,
                intensity,
                thought,
                evidence,
                alternative,
                response,
                insights
            )
        )

        connection.commit()
        connection.close()

        message = "Reflection saved."

    # Get previous reflections

    connection = sqlite3.connect(DATABASE)

    connection.row_factory = sqlite3.Row

    entries = connection.execute(
        """
        SELECT
            created_at,
            situation,
            emotion,
            intensity,
            thought,
            evidence,
            alternative,
            response,
            insights
        FROM reflections
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "reflection.html",
        entries=entries,
        message=message
    )

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    # Total reflections
    reflection_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM reflections
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    # Recent reflections
    recent_reflections = connection.execute(
        """
        SELECT
            id,
            created_at,
            situation,
            emotion,
            intensity,
            thought,
            alternative,
            response,
            insights
        FROM reflections
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 5
        """,
        (session["user_id"],)
    ).fetchall()

    # Most common emotion
    emotion_result = connection.execute(
        """
        SELECT emotion, COUNT(*) AS amount
        FROM reflections
        WHERE user_id = ?
        GROUP BY emotion
        ORDER BY amount DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    if emotion_result:
        common_emotion = emotion_result["emotion"]
    else:
        common_emotion = "Not enough data"

    # Most recent reflection
    latest_reflection = connection.execute(
        """
        SELECT
            created_at,
            situation,
            emotion,
            insights
        FROM reflections
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()

    connection.close()

    return render_template(
        "dashboard.html",
        reflection_count=reflection_count,
        recent_reflections=recent_reflections,
        common_emotion=common_emotion,
        latest_reflection=latest_reflection
    )

@app.route("/signup", methods=["GET","POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")

        email = request.form.get("email")

        password = hashlib.sha256(
            request.form.get("password").encode()
        ).hexdigest()


        connection = sqlite3.connect(DATABASE)


        connection.execute("""
            INSERT INTO users
            (username,email,password)

            VALUES (?,?,?)

        """,
        (
            username,
            email,
            password
        ))


        connection.commit()

        connection.close()


        return redirect("/login")


    return render_template("signup.html")

@app.route("/login", methods=["GET","POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = hashlib.sha256(
            request.form.get("password").encode()
        ).hexdigest()


        connection = sqlite3.connect(DATABASE)


        user = connection.execute("""
            SELECT id,username
            FROM users

            WHERE email=?
            AND password=?

        """,
        (
            email,
            password
        )).fetchone()


        connection.close()


        if user:

            session["user_id"] = user[0]

            session["username"] = user[1]


            return redirect("/dashboard")


    return render_template("login.html")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/welcome")
def welcome():

    return render_template(
        "welcome.html"
    )

@app.route("/framework")
def framework():

    return render_template(
        "framework.html"
    )
@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    # Get reflections
    reflections = connection.execute(
        """
        SELECT
            id,
            created_at,
            situation,
            emotion,
            intensity,
            thought,
            evidence,
            alternative,
            response,
            insights
        FROM reflections
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    # Get decisions
    decisions = connection.execute(
        """
        SELECT
            id,
            created_at,
            situation,
            goal,
            facts,
            assumptions,
            option_a,
            benefits_a,
            drawbacks_a,
            option_b,
            benefits_b,
            drawbacks_b,
            short_term,
            long_term,
            decision_choice,
            reasoning
        FROM decisions
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (session["user_id"],)
    ).fetchall()

    connection.close()

    return render_template(
        "history.html",
        reflections=reflections,
        decisions=decisions
    )
@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        rating = request.form.get("rating")
        comment = request.form.get("comment", "").strip()

        if not rating:
            return render_template(
                "feedback.html",
                error="Please select a rating."
            )

        connection = get_db()

        connection.execute(
            """
            INSERT INTO feedback
            (user_id, rating, comment)
            VALUES (?, ?, ?)
            """,
            (
                session["user_id"],
                rating,
                comment
            )
        )

        connection.commit()
        connection.close()

        return render_template(
            "feedback.html",
            submitted=True
        )

    return render_template("feedback.html")

@app.route("/feedback-results")
def feedback_results():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    feedback = connection.execute(
        """
        SELECT *
        FROM feedback
        ORDER BY id DESC
        """
    ).fetchall()

    average = connection.execute(
        """
        SELECT AVG(rating)
        FROM feedback
        """
    ).fetchone()[0]

    connection.close()

    if average is not None:
        average = round(average, 1)

    return render_template(
        "feedback_results.html",
        feedback=feedback,
        average=average
    )
# -----------------------------
# INITIALIZE DATABASE
# -----------------------------

init_db()

# -----------------------------
# RUN APPLICATION
# -----------------------------
if __name__ == "__main__":

    init_db()

    app.run(debug=True)