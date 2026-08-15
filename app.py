from flask import Flask, render_template, request, redirect, session
import sqlite3
import hashlib
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from analysis import analyze_reflection


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "database.db")

# =========================================================
# TIMEZONE
# =========================================================

# Illinois uses America/Chicago.
# This automatically handles CST and CDT.
ILLINOIS_TIMEZONE = ZoneInfo("America/Chicago")


def convert_to_illinois_time(timestamp):

    if not timestamp:
        return timestamp

    try:

        # SQLite CURRENT_TIMESTAMP is stored in UTC.
        utc_time = datetime.strptime(
            timestamp,
            "%Y-%m-%d %H:%M:%S"
        ).replace(
            tzinfo=timezone.utc
        )

        # Convert UTC → Illinois time.
        local_time = utc_time.astimezone(
            ILLINOIS_TIMEZONE
        )

        return local_time.strftime(
            "%B %d, %Y at %I:%M %p"
        )

    except (ValueError, TypeError):

        return timestamp

def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# =========================================================
# LESSONS
# =========================================================

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


# =========================================================
# APP
# =========================================================
app = Flask(__name__)

app.secret_key = "rationalmind_secret_key"

CREATOR_USERNAME = "Koki Wakita".strip().lower()
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
    # -----------------------------------------------------

    columns = connection.execute(
        "PRAGMA table_info(feedback)"
    ).fetchall()

    column_names = [
        column[1]
        for column in columns
    ]

    if "reflection_id" not in column_names:

        connection.execute(
            """
            ALTER TABLE feedback
            ADD COLUMN reflection_id INTEGER
            """
        )

    if "after_emotion" not in column_names:

        connection.execute(
            """
            ALTER TABLE feedback
            ADD COLUMN after_emotion TEXT
            """
        )

    if "after_intensity" not in column_names:

        connection.execute(
            """
            ALTER TABLE feedback
            ADD COLUMN after_intensity INTEGER
            """
        )

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
@app.template_filter("illinois_time")
def illinois_time_filter(timestamp):

    return convert_to_illinois_time(timestamp)


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


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
        counter_evidence = request.form.get(
            "counter_evidence"
        )
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

        benefits_a = request.form.get(
            "benefits_a"
        )

        drawbacks_a = request.form.get(
            "drawbacks_a"
        )

        benefits_b = request.form.get(
            "benefits_b"
        )

        drawbacks_b = request.form.get(
            "drawbacks_b"
        )

        short_term = request.form.get(
            "short_term"
        )

        long_term = request.form.get(
            "long_term"
        )

        decision_choice = request.form.get(
            "decision_choice"
        )

        reasoning = request.form.get(
            "reasoning"
        )

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

    return render_template(
        "reset.html"
    )


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

# =========================================================
# DAILY REFLECTION
# =========================================================

@app.route("/reflection", methods=["GET", "POST"])
def reflection():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    # =====================================================
    # CHECK MOST RECENT REFLECTION
    # =====================================================

    latest_reflection = connection.execute(
        """
        SELECT
            id
        FROM reflections
        WHERE user_id = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (session["user_id"],)
    ).fetchone()


    # =====================================================
    # DETERMINE WHETHER FEEDBACK IS REQUIRED
    # =====================================================

    feedback_required = False

    if latest_reflection:

        existing_feedback = connection.execute(
            """
            SELECT
                id
            FROM feedback
            WHERE reflection_id = ?
            LIMIT 1
            """,
            (latest_reflection["id"],)
        ).fetchone()

        if not existing_feedback:

            feedback_required = True


    # =====================================================
    # PREVENT ANOTHER REFLECTION
    # UNTIL FEEDBACK IS SUBMITTED
    # =====================================================

    if request.method == "GET" and feedback_required:

        connection.close()

        return render_template(
            "reflection.html",
            entries=[],
            message=None,
            feedback_required=True
        )


    # =====================================================
    # POST — SAVE NEW REFLECTION
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # EXTRA SECURITY CHECK
        # -------------------------------------------------
        # Check again in case the user tries to bypass
        # the page restriction.
        # -------------------------------------------------

        latest_reflection = connection.execute(
            """
            SELECT
                id
            FROM reflections
            WHERE user_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (session["user_id"],)
        ).fetchone()


        if latest_reflection:

            existing_feedback = connection.execute(
                """
                SELECT
                    id
                FROM feedback
                WHERE reflection_id = ?
                LIMIT 1
                """,
                (latest_reflection["id"],)
            ).fetchone()


            if not existing_feedback:

                connection.close()

                return render_template(
                    "reflection.html",
                    entries=[],
                    message=None,
                    feedback_required=True
                )


        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        situation = request.form.get(
            "situation"
        )

        emotion = request.form.get(
            "emotion"
        )

        emotion_direction = request.form.get(
            "emotion_direction"
        )

        intensity = request.form.get(
            "intensity"
        )

        thought = request.form.get(
            "thought"
        )

        supporting_evidence = request.form.get(
            "evidence"
        )

        challenging_evidence = request.form.get(
            "challenging_evidence"
        )

        alternative = request.form.get(
            "alternative"
        )

        response = request.form.get(
            "response"
        )

        insights = request.form.get(
            "insights"
        )


        # =================================================
        # VALIDATE INTENSITY
        # =================================================

        try:

            intensity = int(intensity)

        except (TypeError, ValueError):

            connection.close()

            return render_template(
                "reflection.html",
                entries=[],
                message=(
                    "Please select an emotion intensity."
                ),
                feedback_required=False
            )


        # =================================================
        # VALIDATE EMOTION DIRECTION
        # =================================================

        if emotion_direction not in [
            "negative",
            "positive"
        ]:

            connection.close()

            return render_template(
                "reflection.html",
                entries=[],
                message=(
                    "Please select whether the emotion "
                    "is negative or positive."
                ),
                feedback_required=False
            )


        # =================================================
        # VALIDATE INTENSITY SIGN
        # =================================================

        if emotion_direction == "negative":

            if intensity < -5 or intensity > -1:

                connection.close()

                return render_template(
                    "reflection.html",
                    entries=[],
                    message=(
                        "A negative emotion must have "
                        "an intensity between -5 and -1."
                    ),
                    feedback_required=False
                )


        elif emotion_direction == "positive":

            if intensity < 1 or intensity > 5:

                connection.close()

                return render_template(
                    "reflection.html",
                    entries=[],
                    message=(
                        "A positive emotion must have "
                        "an intensity between +1 and +5."
                    ),
                    feedback_required=False
                )


        # =================================================
        # COMBINE EVIDENCE
        # =================================================

        evidence = (
            "Supports: "
            + (supporting_evidence or "")
            + "\n\nChallenges: "
            + (challenging_evidence or "")
        )


        # =================================================
        # SAVE REFLECTION
        # =================================================

        cursor = connection.execute(
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

        connection.close()


        # =================================================
        # SEND USER DIRECTLY TO FEEDBACK
        # =================================================

        return redirect("/feedback")


    # =====================================================
    # LOAD REFLECTION HISTORY
    # =====================================================

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


    # =====================================================
    # DISPLAY REFLECTION PAGE
    # =====================================================

    return render_template(
        "reflection.html",
        entries=entries,
        message=None,
        feedback_required=False
    )
# =========================================================
# DASHBOARD
# =========================================================

# =========================================================
# DASHBOARD
# =========================================================

from datetime import datetime
from zoneinfo import ZoneInfo


@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect("/login")

    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row

    # -----------------------------------------------------
    # ILLINOIS TIMEZONE
    # -----------------------------------------------------

    illinois_timezone = ZoneInfo("America/Chicago")

    # -----------------------------------------------------
    # TOTAL REFLECTIONS
    # -----------------------------------------------------

    reflection_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM reflections
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()[0]

    # -----------------------------------------------------
    # RECENT REFLECTIONS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CONVERT REFLECTION TIMES TO ILLINOIS TIME
    # -----------------------------------------------------

    converted_reflections = []

    for reflection in recent_reflections:

        reflection_data = dict(reflection)

        if reflection_data["created_at"]:

            try:

                utc_time = datetime.strptime(
                    reflection_data["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=ZoneInfo("UTC")
                )

                illinois_time = utc_time.astimezone(
                    illinois_timezone
                )

                reflection_data["created_at"] = (
                    illinois_time.strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                )

            except (ValueError, TypeError):

                pass

        converted_reflections.append(
            reflection_data
        )

    # -----------------------------------------------------
    # MOST COMMON EMOTION
    # -----------------------------------------------------

    emotion_result = connection.execute(
        """
        SELECT
            emotion,
            COUNT(*) AS amount
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

    # -----------------------------------------------------
    # LATEST REFLECTION
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CONVERT LATEST REFLECTION TIME
    # -----------------------------------------------------

    if latest_reflection:

        latest_reflection = dict(
            latest_reflection
        )

        if latest_reflection["created_at"]:

            try:

                utc_time = datetime.strptime(
                    latest_reflection["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=ZoneInfo("UTC")
                )

                illinois_time = utc_time.astimezone(
                    illinois_timezone
                )

                latest_reflection["created_at"] = (
                    illinois_time.strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                )

            except (ValueError, TypeError):

                pass

    # -----------------------------------------------------
    # CLOSE DATABASE
    # -----------------------------------------------------

    connection.close()

    # -----------------------------------------------------
    # SEND DATA TO DASHBOARD
    # -----------------------------------------------------

    return render_template(
        "dashboard.html",
        reflection_count=reflection_count,
        recent_reflections=converted_reflections,
        common_emotion=common_emotion,
        latest_reflection=latest_reflection
    )


# =========================================================
# SIGNUP
# =========================================================

# =========================================================
# SIGNUP
# =========================================================

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        username = request.form.get("username")
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
                    username + "@rationalmind.local",
                    password
                )
            )

            connection.commit()

        except sqlite3.IntegrityError:

            connection.close()

            return render_template(
                "signup.html",
                error="That username is already taken."
            )

        connection.close()

        return redirect("/login")

    return render_template("signup.html")

# =========================================================
# LOGIN
# =========================================================

# =========================================================
# LOGIN
# =========================================================

# =========================================================
# LOGIN
# =========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username", "").strip()

        password_input = request.form.get("password", "")

        password = hashlib.sha256(
            password_input.encode()
        ).hexdigest()

        connection = sqlite3.connect(DATABASE)

        user = connection.execute(
            """
            SELECT id, username
            FROM users
            WHERE username = ?
            AND password = ?
            """,
            (
                username,
                password
            )
        ).fetchone()

        connection.close()

        if user:

            session["user_id"] = user[0]
            session["username"] = user[1]

            return redirect("/dashboard")

        return render_template(
            "login.html",
            error="Incorrect username or password."
        )

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

# =========================================================
# HISTORY
# =========================================================

@app.route("/history")
def history():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    illinois_timezone = ZoneInfo("America/Chicago")

    # -----------------------------------------------------
    # REFLECTIONS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CONVERT REFLECTION TIMES
    # -----------------------------------------------------

    converted_reflections = []

    for reflection in reflections:

        reflection_data = dict(reflection)

        if reflection_data["created_at"]:

            try:

                utc_time = datetime.strptime(
                    reflection_data["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=ZoneInfo("UTC")
                )

                illinois_time = utc_time.astimezone(
                    illinois_timezone
                )

                reflection_data["created_at"] = (
                    illinois_time.strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                )

            except (ValueError, TypeError):

                pass

        converted_reflections.append(
            reflection_data
        )

    # -----------------------------------------------------
    # DECISIONS
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CONVERT DECISION TIMES
    # -----------------------------------------------------

    converted_decisions = []

    for decision in decisions:

        decision_data = dict(decision)

        if decision_data["created_at"]:

            try:

                utc_time = datetime.strptime(
                    decision_data["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=ZoneInfo("UTC")
                )

                illinois_time = utc_time.astimezone(
                    illinois_timezone
                )

                decision_data["created_at"] = (
                    illinois_time.strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                )

            except (ValueError, TypeError):

                pass

        converted_decisions.append(
            decision_data
        )

    # -----------------------------------------------------
    # CLOSE DATABASE
    # -----------------------------------------------------

    connection.close()

    # -----------------------------------------------------
    # SEND DATA TO HISTORY PAGE
    # -----------------------------------------------------

    return render_template(
        "history.html",
        reflections=converted_reflections,
        decisions=converted_decisions
    )

# =========================================================
# FEEDBACK
# =========================================================

# =========================================================
# FEEDBACK
# =========================================================

@app.route("/feedback", methods=["GET", "POST"])
def feedback():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    # -----------------------------------------------------
    # FIND MOST RECENT REFLECTION
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # CHECK WHETHER REFLECTION ALREADY HAS FEEDBACK
    # -----------------------------------------------------

    has_feedback = False

    if latest_reflection:

        existing_feedback = connection.execute(
            """
            SELECT id
            FROM feedback
            WHERE reflection_id = ?
            LIMIT 1
            """,
            (latest_reflection["id"],)
        ).fetchone()

        if existing_feedback:

            has_feedback = True

    # =====================================================
    # POST
    # =====================================================

    if request.method == "POST":

        # -------------------------------------------------
        # NO REFLECTION
        # -------------------------------------------------

        if not latest_reflection:

            connection.close()

            return render_template(
                "feedback.html",
                can_submit=False,
                error=(
                    "Please complete a reflection "
                    "before submitting feedback."
                )
            )

        # -------------------------------------------------
        # FEEDBACK ALREADY SUBMITTED
        # -------------------------------------------------

        if has_feedback:

            connection.close()

            return render_template(
                "feedback.html",
                can_submit=False,
                error=(
                    "You have already submitted feedback "
                    "for your most recent reflection. "
                    "Complete another reflection before "
                    "submitting new feedback."
                )
            )

        # -------------------------------------------------
        # GET FORM DATA
        # -------------------------------------------------

        rating = request.form.get(
            "rating"
        )

        comment = request.form.get(
            "comment",
            ""
        ).strip()

        after_emotion = request.form.get(
            "after_emotion"
        )

        after_intensity = request.form.get(
            "after_intensity"
        )

        # -------------------------------------------------
        # OTHER EMOTION
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

            connection.close()

            return render_template(
                "feedback.html",
                can_submit=True,
                error="Please select a rating."
            )

        if not after_emotion:

            connection.close()

            return render_template(
                "feedback.html",
                can_submit=True,
                error=(
                    "Please select or enter your emotion."
                )
            )

        if not after_intensity:

            connection.close()

            return render_template(
                "feedback.html",
                can_submit=True,
                error=(
                    "Please select your emotional intensity."
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

        return render_template(
            "feedback.html",
            submitted=True,
            can_submit=False
        )

    # =====================================================
    # GET
    # =====================================================

    connection.close()

    # -----------------------------------------------------
    # NO REFLECTION YET
    # -----------------------------------------------------

    if not latest_reflection:

        return render_template(
            "feedback.html",
            can_submit=False
        )

    # -----------------------------------------------------
    # REFLECTION ALREADY HAS FEEDBACK
    # -----------------------------------------------------

    if has_feedback:

        return render_template(
            "feedback.html",
            can_submit=False,
            already_submitted=True
        )

    # -----------------------------------------------------
    # REFLECTION EXISTS AND NEEDS FEEDBACK
    # -----------------------------------------------------

    return render_template(
        "feedback.html",
        can_submit=True
    )
# =========================================================
# FEEDBACK RESULTS
# =========================================================

# =========================================================
# FEEDBACK RESULTS
# =========================================================

@app.route("/feedback-results")
def feedback_results():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    # -----------------------------------------------------
    # ILLINOIS TIMEZONE
    # -----------------------------------------------------

    illinois_timezone = ZoneInfo("America/Chicago")

    # -----------------------------------------------------
    # CREATOR-ONLY ACCESS
    # -----------------------------------------------------

    user = connection.execute(
        """
        SELECT username
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if (
        not user
        or user["username"].strip().lower()
        != CREATOR_USERNAME.strip().lower()
    ):

        connection.close()

        return redirect("/dashboard")

    # -----------------------------------------------------
    # ALL FEEDBACK
    # -----------------------------------------------------

    feedback_rows = connection.execute(
        """
        SELECT *
        FROM feedback
        ORDER BY id DESC
        """
    ).fetchall()

    # -----------------------------------------------------
    # CONVERT FEEDBACK TIMES
    # -----------------------------------------------------

    feedback = []

    for item in feedback_rows:

        feedback_data = dict(item)

        if feedback_data["created_at"]:

            try:

                utc_time = datetime.strptime(
                    feedback_data["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=ZoneInfo("UTC")
                )

                illinois_time = utc_time.astimezone(
                    illinois_timezone
                )

                feedback_data["created_at"] = (
                    illinois_time.strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                )

            except (ValueError, TypeError):

                pass

        feedback.append(
            feedback_data
        )

    # -----------------------------------------------------
    # AVERAGE RATING
    # -----------------------------------------------------

    average = connection.execute(
        """
        SELECT AVG(rating)
        FROM feedback
        """
    ).fetchone()[0]

    if average is not None:

        average = round(
            average,
            1
        )

    # -----------------------------------------------------
    # BEFORE / AFTER
    # -----------------------------------------------------

    comparison_data = connection.execute(
        """
        SELECT
            f.id,
            f.after_emotion,
            f.after_intensity,
            r.emotion AS before_emotion,
            r.intensity AS before_intensity
        FROM feedback f
        LEFT JOIN reflections r
            ON r.id = f.reflection_id
        WHERE
            f.after_intensity IS NOT NULL
        """
    ).fetchall()

    # -----------------------------------------------------
    # BUILD COMPARISONS
    # -----------------------------------------------------

    comparisons = []

    for item in comparison_data:

        try:

            before_intensity = int(
                item["before_intensity"]
            )

            after_intensity = int(
                item["after_intensity"]
            )

        except (TypeError, ValueError):

            continue

        before_emotion = (
            item["before_emotion"]
            or ""
        ).strip().lower()

        after_emotion = (
            item["after_emotion"]
            or ""
        ).strip().lower()

        # -------------------------------------------------
        # CALCULATE CHANGE
        # -------------------------------------------------

        if before_intensity < 0:

            change = (
                abs(before_intensity)
                - abs(after_intensity)
            )

        else:

            change = (
                after_intensity
                - before_intensity
            )

        comparisons.append({

            "before_emotion":
                item["before_emotion"],

            "before_intensity":
                before_intensity,

            "after_emotion":
                item["after_emotion"],

            "after_intensity":
                after_intensity,

            "change":
                change

        })

    # -----------------------------------------------------
    # SUMMARY STATISTICS
    # -----------------------------------------------------

    if comparisons:

        average_before = round(
            sum(
                abs(
                    item["before_intensity"]
                )
                for item in comparisons
            )
            / len(comparisons),
            1
        )

        average_after = round(
            sum(
                abs(
                    item["after_intensity"]
                )
                for item in comparisons
            )
            / len(comparisons),
            1
        )

        average_change = round(
            average_before
            - average_after,
            1
        )

        improved_count = sum(
            1
            for item in comparisons
            if item["change"] > 0
        )

        improvement_percentage = round(
            (
                improved_count
                / len(comparisons)
            ) * 100
        )

    else:

        average_before = None
        average_after = None
        average_change = None
        improvement_percentage = None

    # -----------------------------------------------------
    # CLOSE DATABASE
    # -----------------------------------------------------

    connection.close()

    # -----------------------------------------------------
    # SEND DATA TO TEMPLATE
    # -----------------------------------------------------

    return render_template(
        "feedback_results.html",

        feedback=feedback,

        average=average,

        comparisons=comparisons,

        average_before=average_before,

        average_after=average_after,

        average_change=average_change,

        improvement_percentage=(
            improvement_percentage
        )
    )

# =========================================================
# CREATOR DASHBOARD
# =========================================================

@app.route("/creator")
def creator():

    if "user_id" not in session:
        return redirect("/login")

    connection = get_db()

    illinois_timezone = ZoneInfo("America/Chicago")

    # -----------------------------------------------------
    # CREATOR-ONLY ACCESS
    # -----------------------------------------------------

    user = connection.execute(
        """
        SELECT username
        FROM users
        WHERE id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    if not user:

        connection.close()

        return redirect("/dashboard")

    creator_username = CREATOR_USERNAME.strip().lower()

    if user["username"].strip().lower() != creator_username:

        connection.close()

        return redirect("/dashboard")

    # -----------------------------------------------------
    # TOTAL USERS
    # -----------------------------------------------------

    total_users = connection.execute(
        """
        SELECT COUNT(*)
        FROM users
        """
    ).fetchone()[0]

    # -----------------------------------------------------
    # TOTAL REFLECTIONS
    # -----------------------------------------------------

    total_reflections = connection.execute(
        """
        SELECT COUNT(*)
        FROM reflections
        """
    ).fetchone()[0]

    # -----------------------------------------------------
    # TOTAL FEEDBACK
    # -----------------------------------------------------

    total_feedback = connection.execute(
        """
        SELECT COUNT(*)
        FROM feedback
        """
    ).fetchone()[0]

    # -----------------------------------------------------
    # AVERAGE RATING
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # INTENSITY COMPARISONS
    # -----------------------------------------------------

    comparison_rows = connection.execute(
        """
        SELECT
            f.id,
            f.after_emotion,
            f.after_intensity,
            r.emotion AS before_emotion,
            r.intensity AS before_intensity
        FROM feedback f
        JOIN reflections r
            ON r.id = f.reflection_id
        WHERE
            f.after_intensity IS NOT NULL
            AND r.intensity IS NOT NULL
        """
    ).fetchall()

    # -----------------------------------------------------
    # CALCULATE INTENSITY OUTCOMES
    # -----------------------------------------------------

    lower_intensity = 0
    same_intensity = 0
    higher_intensity = 0

    comparison_data = []

    for row in comparison_rows:

        try:

            before = int(
                row["before_intensity"]
            )

            after = int(
                row["after_intensity"]
            )

        except (TypeError, ValueError):

            continue

        # Negative emotions:
        # closer to zero = improvement

        if before < 0:

            change = (
                abs(before)
                - abs(after)
            )

        # Positive emotions:
        # higher positive value = improvement

        else:

            change = (
                after
                - before
            )

        if change > 0:

            lower_intensity += 1

        elif change == 0:

            same_intensity += 1

        else:

            higher_intensity += 1

        comparison_data.append({

            "before":
                before,

            "after":
                after,

            "change":
                change,

            "before_emotion":
                row["before_emotion"],

            "after_emotion":
                row["after_emotion"]

        })

    # -----------------------------------------------------
    # AVERAGE BEFORE / AFTER
    # -----------------------------------------------------

    if comparison_data:

        average_before = round(
            sum(
                abs(item["before"])
                for item in comparison_data
            )
            / len(comparison_data),
            1
        )

        average_after = round(
            sum(
                abs(item["after"])
                for item in comparison_data
            )
            / len(comparison_data),
            1
        )

        average_change = round(
            average_before
            - average_after,
            1
        )

    else:

        average_before = None
        average_after = None
        average_change = None

    # -----------------------------------------------------
    # EMOTIONAL TRANSITIONS
    # -----------------------------------------------------

    transition_rows = connection.execute(
        """
        SELECT
            r.emotion AS before_emotion,
            f.after_emotion AS after_emotion,
            COUNT(*) AS amount
        FROM feedback f
        JOIN reflections r
            ON r.id = f.reflection_id
        WHERE
            r.emotion IS NOT NULL
            AND f.after_emotion IS NOT NULL
            AND TRIM(r.emotion) != ''
            AND TRIM(f.after_emotion) != ''
        GROUP BY
            r.emotion,
            f.after_emotion
        ORDER BY
            amount DESC
        """
    ).fetchall()

    transitions = transition_rows

    # -----------------------------------------------------
    # MOST COMMON STARTING EMOTION
    # -----------------------------------------------------

    starting_emotion = connection.execute(
        """
        SELECT
            emotion,
            COUNT(*) AS amount
        FROM reflections
        WHERE
            emotion IS NOT NULL
            AND TRIM(emotion) != ''
        GROUP BY emotion
        ORDER BY amount DESC
        LIMIT 1
        """
    ).fetchone()

    # -----------------------------------------------------
    # MOST COMMON ENDING EMOTION
    # -----------------------------------------------------

    ending_emotion = connection.execute(
        """
        SELECT
            after_emotion,
            COUNT(*) AS amount
        FROM feedback
        WHERE
            after_emotion IS NOT NULL
            AND TRIM(after_emotion) != ''
        GROUP BY after_emotion
        ORDER BY amount DESC
        LIMIT 1
        """
    ).fetchone()

    # -----------------------------------------------------
    # RECENT FEEDBACK
    # -----------------------------------------------------

    recent_feedback_rows = connection.execute(
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
            ON r.id = f.reflection_id
        ORDER BY f.id DESC
        LIMIT 20
        """
    ).fetchall()

    # -----------------------------------------------------
    # CONVERT FEEDBACK TIMES TO ILLINOIS TIME
    # -----------------------------------------------------

    recent_feedback = []

    for feedback in recent_feedback_rows:

        feedback_data = dict(feedback)

        if feedback_data["created_at"]:

            try:

                utc_time = datetime.strptime(
                    feedback_data["created_at"],
                    "%Y-%m-%d %H:%M:%S"
                ).replace(
                    tzinfo=ZoneInfo("UTC")
                )

                illinois_time = utc_time.astimezone(
                    illinois_timezone
                )

                feedback_data["created_at"] = (
                    illinois_time.strftime(
                        "%B %d, %Y at %I:%M %p"
                    )
                )

            except (ValueError, TypeError):

                pass

        recent_feedback.append(
            feedback_data
        )

    # -----------------------------------------------------
    # CLOSE DATABASE
    # -----------------------------------------------------

    connection.close()

    # -----------------------------------------------------
    # SEND DATA TO CREATOR PAGE
    # -----------------------------------------------------

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
