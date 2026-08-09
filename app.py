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
CREATOR_EMAIL = os.environ.get("CREATOR_EMAIL", "").strip().lower()

# =========================================================
# DATABASE
# =========================================================

def init_db():

    connection = sqlite3.connect(DATABASE)

    # -----------------------------------------------------
    # USERS
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)

    # -----------------------------------------------------
    # REFLECTIONS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # DECISIONS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # FEEDBACK
    # -----------------------------------------------------

    connection.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            reflection_id INTEGER,
            rating INTEGER NOT NULL,
            comment TEXT,
            after_emotion TEXT,
            after_intensity INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # -----------------------------------------------------
    # DATABASE MIGRATION
    # Adds new columns to existing feedback table
    # without deleting old feedback.
    # -----------------------------------------------------

    columns = connection.execute(
        "PRAGMA table_info(feedback)"
    ).fetchall()

    column_names = [column[1] for column in columns]

    # Add reflection_id to existing databases
    if "reflection_id" not in column_names:

        connection.execute(
            "ALTER TABLE feedback ADD COLUMN reflection_id INTEGER"
        )

    # Add after_emotion to existing databases
    if "after_emotion" not in column_names:

        connection.execute(
            "ALTER TABLE feedback ADD COLUMN after_emotion TEXT"
        )

    # Add after_intensity to existing databases
    if "after_intensity" not in column_names:

        connection.execute(
            "ALTER TABLE feedback ADD COLUMN after_intensity INTEGER"
        )

    # -----------------------------------------------------
    # SAVE CHANGES
    # -----------------------------------------------------

    connection.commit()
    connection.close()


# =========================================================
# USER CONTEXT
# =========================================================

@app.context_processor
def inject_user():

    return {
        "logged_in": "user_id" in session,
        "username": session.get("username")
    }


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template("index.html")


# =========================================================
# EMOTIONAL CHECK-IN
# =========================================================

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
            "insights": analyze_reflection(
                emotion,
                thought,
                response
            )
        }

    return render_template(
        "check_in.html",
        reflection=reflection
    )


# =========================================================
# RATIONAL DECISION
# =========================================================

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


# =========================================================
# STRESS RESET
# =========================================================

@app.route("/reset")
def reset():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("reset.html")


# =========================================================
# EXPLORE
# =========================================================

@app.route("/explore")
def explore():

    return render_template(
        "explore.html",
        lessons=lessons
    )


# =========================================================
# DAILY REFLECTION
# =========================================================

@app.route("/reflection", methods=["GET", "POST"])
def reflection():

    if "user_id" not in session:
        return redirect("/login")

    message = None

    connection = get_db()

    if request.method == "POST":

        situation = request.form.get("situation")
        emotion = request.form.get("emotion")
        intensity = request.form.get("intensity")
        thought = request.form.get("thought")

        supporting_evidence = request.form.get("evidence")
        challenging_evidence = request.form.get(
            "challenging_evidence"
        )

        alternative = request.form.get("alternative")
        response = request.form.get("response")
        insights = request.form.get("insights")

        evidence = (
            "Supports: " + (supporting_evidence or "") +
            "\n\nChallenges: " +
            (challenging_evidence or "")
        )

        connection.execute(
            """
            INSERT INTO reflections (
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

        message = "Reflection saved."

    entries = connection.execute(
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

    connection.close()

    return render_template(
        "reflection.html",
        entries=entries,
        message=message
    )


# =========================================================
# DASHBOARD
# =========================================================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    reflection_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM reflections
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

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


# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
        email = request.form.get("email")

        password = hashlib.sha256(
            request.form.get("password").encode()
        ).hexdigest()

        connection = sqlite3.connect(DATABASE)

        try:

            connection.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (?, ?, ?)
                """,
                (
                    username,
                    email,
                    password
                )
            )

            connection.commit()

        except sqlite3.IntegrityError:

            connection.close()

            return render_template(
                "signup.html",
                error="An account with this email already exists."
            )

        connection.close()

        return redirect("/login")

    return render_template("signup.html")


# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form.get("email")

        password = hashlib.sha256(
            request.form.get("password").encode()
        ).hexdigest()

        connection = sqlite3.connect(DATABASE)

        user = connection.execute(
            """
            SELECT id, username
            FROM users
            WHERE email = ?
            AND password = ?
            """,
            (
                email,
                password
            )
        ).fetchone()

        connection.close()

        if user:

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/dashboard")

    return render_template("login.html")


# =========================================================
# LOGOUT
# =========================================================

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")


# =========================================================
# WELCOME
# =========================================================

@app.route("/welcome")
def welcome():

    return render_template(
        "welcome.html"
    )


# =========================================================
# FRAMEWORK
# =========================================================

@app.route("/framework")
def framework():

    return render_template(
        "framework.html"
    )


# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

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


# =========================================================
# FEEDBACK
# =========================================================

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":

        # -------------------------------------------------
        # GET FEEDBACK INFORMATION
        # -------------------------------------------------

        rating = request.form.get("rating")
        comment = request.form.get("comment", "").strip()

        after_emotion = request.form.get("after_emotion")

        after_intensity = request.form.get(
            "after_intensity"
        )

        # -------------------------------------------------
        # HANDLE "OTHER" EMOTION
        # -------------------------------------------------

        if after_emotion == "Other":

            after_emotion = request.form.get(
                "other_emotion",
                ""
            ).strip()

        # -------------------------------------------------
        # VALIDATION
        # -------------------------------------------------

        if not rating:

            return render_template(
                "feedback.html",
                error="Please select a rating."
            )

        if not after_emotion:

            return render_template(
                "feedback.html",
                error="Please select or enter your emotion."
            )

        if not after_intensity:

            return render_template(
                "feedback.html",
                error="Please select your emotional intensity."
            )

        # -------------------------------------------------
        # FIND MOST RECENT REFLECTION
        # -------------------------------------------------

        connection = get_db()

        latest_reflection = connection.execute(
            """
            SELECT
                id,
                emotion,
                intensity
            FROM reflections
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()

        # -------------------------------------------------
        # MAKE SURE A REFLECTION EXISTS
        # -------------------------------------------------

        if not latest_reflection:

            connection.close()

            return render_template(
                "feedback.html",
                error=(
                    "Please complete a reflection "
                    "before submitting feedback."
                )
            )

        # -------------------------------------------------
        # SAVE FEEDBACK
        # -------------------------------------------------

        connection.execute(
            """
            INSERT INTO feedback (
                user_id,
                reflection_id,
                rating,
                comment,
                after_emotion,
                after_intensity
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session["user_id"],
                latest_reflection["id"],
                rating,
                comment,
                after_emotion,
                after_intensity
            )
        )

        connection.commit()
        connection.close()

        # -------------------------------------------------
        # SHOW SUCCESS PAGE
        # -------------------------------------------------

        return render_template(
            "feedback.html",
            submitted=True
        )

    # -----------------------------------------------------
    # GET REQUEST
    # -----------------------------------------------------

    return render_template(
        "feedback.html"
    )


# =========================================================
# FEEDBACK RESULTS
# =========================================================

@app.route("/feedback-results")
def feedback_results():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    user = connection.execute(
        """
        SELECT email
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # Only the creator can view all feedback
    if not user or user["email"] != CREATOR_EMAIL:

        connection.close()

        return redirect("/dashboard")

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

    comparison_data = connection.execute(
        """
        SELECT
            feedback.id,
            feedback.after_emotion,
            feedback.after_intensity,
            reflections.emotion AS before_emotion,
            reflections.intensity AS before_intensity
        FROM feedback

        LEFT JOIN reflections
        ON reflections.user_id = feedback.user_id

        AND reflections.id = (
            SELECT MAX(r.id)
            FROM reflections r
            WHERE r.user_id = feedback.user_id
            AND r.id <= feedback.id
        )

        WHERE feedback.after_intensity IS NOT NULL
        """
    ).fetchall()

    connection.close()

    if average is not None:
        average = round(average, 1)

    comparisons = []

    for item in comparison_data:

        try:
            before_intensity = int(item["before_intensity"])
            after_intensity = int(item["after_intensity"])
        except (TypeError, ValueError):
            continue

        change = before_intensity - after_intensity

        comparisons.append({
            "before_emotion": item["before_emotion"],
            "before_intensity": before_intensity,
            "after_emotion": item["after_emotion"],
            "after_intensity": after_intensity,
            "change": change
        })

    if comparisons:

        average_before = round(
            sum(
                item["before_intensity"]
                for item in comparisons
            ) / len(comparisons),
            1
        )

        average_after = round(
            sum(
                item["after_intensity"]
                for item in comparisons
            ) / len(comparisons),
            1
        )

        average_change = round(
            average_before - average_after,
            1
        )

        improved_count = sum(
            1
            for item in comparisons
            if item["change"] > 0
        )

        improvement_percentage = round(
            (improved_count / len(comparisons)) * 100
        )

    else:

        average_before = None
        average_after = None
        average_change = None
        improvement_percentage = None

    return render_template(
        "feedback_results.html",
        feedback=feedback,
        average=average,
        comparisons=comparisons,
        average_before=average_before,
        average_after=average_after,
        average_change=average_change,
        improvement_percentage=improvement_percentage
    )
    # -----------------------------------------------------
    # Emotional improvement statistics
    # -----------------------------------------------------

    comparison_data = connection.execute(
        """
        SELECT
            feedback.id,
            feedback.after_emotion,
            feedback.after_intensity,
            reflections.emotion AS before_emotion,
            reflections.intensity AS before_intensity
        FROM feedback

        LEFT JOIN reflections
        ON reflections.user_id = feedback.user_id

        AND reflections.id = (
            SELECT MAX(r.id)
            FROM reflections r
            WHERE r.user_id = feedback.user_id
            AND r.id <= feedback.id
        )

        WHERE feedback.after_intensity IS NOT NULL
        """
    ).fetchall()

    connection.close()

    if average is not None:
        average = round(average, 1)

    comparisons = []

    for item in comparison_data:

        before_intensity = item["before_intensity"]
        after_intensity = item["after_intensity"]

        try:
            before_intensity = int(before_intensity)
            after_intensity = int(after_intensity)
        except (TypeError, ValueError):
            continue

        change = before_intensity - after_intensity

        comparisons.append({
            "before_emotion": item["before_emotion"],
            "before_intensity": before_intensity,
            "after_emotion": item["after_emotion"],
            "after_intensity": after_intensity,
            "change": change
        })

    if comparisons:

        average_before = round(
            sum(item["before_intensity"] for item in comparisons)
            / len(comparisons),
            1
        )

        average_after = round(
            sum(item["after_intensity"] for item in comparisons)
            / len(comparisons),
            1
        )

        average_change = round(
            average_before - average_after,
            1
        )

        improved_count = sum(
            1
            for item in comparisons
            if item["change"] > 0
        )

        improvement_percentage = round(
            (improved_count / len(comparisons)) * 100
        )

    else:

        average_before = None
        average_after = None
        average_change = None
        improvement_percentage = None

    return render_template(
        "feedback_results.html",
        feedback=feedback,
        average=average,
        comparisons=comparisons,
        average_before=average_before,
        average_after=average_after,
        average_change=average_change,
        improvement_percentage=improvement_percentage
    )

@app.route("/creator")
def creator():

    if "user_id" not in session:
        return redirect("/login")

    # -------------------------------------------------
    # CREATOR-ONLY ACCESS
    # -------------------------------------------------

    connection = get_db()

    user = connection.execute(
        """
        SELECT email
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if not user or user["email"].strip().lower() != CREATOR_EMAIL:
        connection.close()
        return redirect("/dashboard")

    # -------------------------------------------------
    # TOTAL USERS
    # -------------------------------------------------

    total_users = connection.execute(
        """
        SELECT COUNT(*)
        FROM users
        """
    ).fetchone()[0]

    # -------------------------------------------------
    # TOTAL REFLECTIONS
    # -------------------------------------------------

    total_reflections = connection.execute(
        """
        SELECT COUNT(*)
        FROM reflections
        """
    ).fetchone()[0]

    # -------------------------------------------------
    # TOTAL FEEDBACK
    # -------------------------------------------------

    total_feedback = connection.execute(
        """
        SELECT COUNT(*)
        FROM feedback
        """
    ).fetchone()[0]

    # -------------------------------------------------
    # AVERAGE RATING
    # -------------------------------------------------

    average_rating = connection.execute(
        """
        SELECT AVG(rating)
        FROM feedback
        """
    ).fetchone()[0]

    if average_rating is not None:
        average_rating = round(
            average_rating,
            1
        )

    # -------------------------------------------------
    # AVERAGE BEFORE INTENSITY
    # -------------------------------------------------

    average_before = connection.execute(
        """
        SELECT AVG(CAST(r.intensity AS REAL))
        FROM feedback f
        JOIN reflections r
            ON f.reflection_id = r.id
        WHERE r.intensity IS NOT NULL
        """
    ).fetchone()[0]

    if average_before is not None:
        average_before = round(
            average_before,
            1
        )

    # -------------------------------------------------
    # AVERAGE AFTER INTENSITY
    # -------------------------------------------------

    average_after = connection.execute(
        """
        SELECT AVG(CAST(after_intensity AS REAL))
        FROM feedback
        WHERE after_intensity IS NOT NULL
        """
    ).fetchone()[0]

    if average_after is not None:
        average_after = round(
            average_after,
            1
        )

    # -------------------------------------------------
    # AVERAGE INTENSITY CHANGE
    # -------------------------------------------------

    average_change = None

    if (
        average_before is not None
        and average_after is not None
    ):

        average_change = round(
            average_after - average_before,
            1
        )

    # -------------------------------------------------
    # NUMBER OF REFLECTIONS WITH LOWER INTENSITY
    # -------------------------------------------------

    lower_intensity = connection.execute(
        """
        SELECT COUNT(*)
        FROM feedback f
        JOIN reflections r
            ON f.reflection_id = r.id
        WHERE CAST(r.intensity AS REAL)
              > CAST(f.after_intensity AS REAL)
        """
    ).fetchone()[0]

    # -------------------------------------------------
    # NUMBER OF REFLECTIONS WITH SAME INTENSITY
    # -------------------------------------------------

    same_intensity = connection.execute(
        """
        SELECT COUNT(*)
        FROM feedback f
        JOIN reflections r
            ON f.reflection_id = r.id
        WHERE CAST(r.intensity AS REAL)
              = CAST(f.after_intensity AS REAL)
        """
    ).fetchone()[0]

    # -------------------------------------------------
    # NUMBER OF REFLECTIONS WITH HIGHER INTENSITY
    # -------------------------------------------------

    higher_intensity = connection.execute(
        """
        SELECT COUNT(*)
        FROM feedback f
        JOIN reflections r
            ON f.reflection_id = r.id
        WHERE CAST(r.intensity AS REAL)
              < CAST(f.after_intensity AS REAL)
        """
    ).fetchone()[0]

    # -------------------------------------------------
    # EMOTIONAL TRANSITIONS
    # -------------------------------------------------

    transitions = connection.execute(
        """
        SELECT
            r.emotion AS before_emotion,
            f.after_emotion AS after_emotion,
            COUNT(*) AS amount
        FROM feedback f
        JOIN reflections r
            ON f.reflection_id = r.id
        WHERE
            r.emotion IS NOT NULL
            AND f.after_emotion IS NOT NULL
        GROUP BY
            r.emotion,
            f.after_emotion
        ORDER BY amount DESC
        """
    ).fetchall()

    # -------------------------------------------------
    # MOST COMMON STARTING EMOTION
    # -------------------------------------------------

    starting_emotion = connection.execute(
        """
        SELECT
            r.emotion,
            COUNT(*) AS amount
        FROM feedback f
        JOIN reflections r
            ON f.reflection_id = r.id
        WHERE r.emotion IS NOT NULL
        GROUP BY r.emotion
        ORDER BY amount DESC
        LIMIT 1
        """
    ).fetchone()

    # -------------------------------------------------
    # MOST COMMON ENDING EMOTION
    # -------------------------------------------------

    ending_emotion = connection.execute(
        """
        SELECT
            after_emotion,
            COUNT(*) AS amount
        FROM feedback
        WHERE after_emotion IS NOT NULL
        GROUP BY after_emotion
        ORDER BY amount DESC
        LIMIT 1
        """
    ).fetchone()

    # -------------------------------------------------
    # RECENT FEEDBACK
    # -------------------------------------------------

    recent_feedback = connection.execute(
        """
        SELECT
            f.rating,
            f.comment,
            f.after_emotion,
            f.after_intensity,
            f.created_at,
            r.emotion AS before_emotion,
            r.intensity AS before_intensity
        FROM feedback f
        LEFT JOIN reflections r
            ON f.reflection_id = r.id
        ORDER BY f.id DESC
        LIMIT 20
        """
    ).fetchall()

    connection.close()

    # -------------------------------------------------
    # SEND DATA TO CREATOR PAGE
    # -------------------------------------------------

    return render_template(
        "creator.html",

        total_users=total_users,

        total_reflections=total_reflections,

        total_feedback=total_feedback,

        average_rating=average_rating,

        average_before=average_before,

        average_after=average_after,

        average_change=average_change,

        lower_intensity=lower_intensity,

        same_intensity=same_intensity,

        higher_intensity=higher_intensity,

        transitions=transitions,

        starting_emotion=starting_emotion,

        ending_emotion=ending_emotion,

        recent_feedback=recent_feedback
    )



# =========================================================
# INITIALIZE DATABASE
# =========================================================

init_db()


# =========================================================
# RUN APPLICATION
# =========================================================

if __name__ == "__main__":

    init_db()

    app.run(debug=True)
