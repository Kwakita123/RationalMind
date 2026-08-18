from flask import Flask, render_template, request, redirect, url_for, session
import psycopg
from datetime import datetime, timezone
import hashlib
import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from analysis import analyze_reflection

DATABASE_URL = os.environ.get("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set.")
# =========================================================
# LANGUAGE / TRANSLATIONS
# =========================================================

# =========================================================
# LANGUAGE / TRANSLATIONS
# =========================================================

TRANSLATIONS = {

    "en": {

        # =================================================
        # NAVIGATION
        # =================================================

        "dashboard": "Dashboard",
        "reflection": "Reflection",
        "decisions": "Decisions",
        "history": "History",
        "explore": "Explore",
        "reset": "Reset",
        "feedback": "Feedback",
        "creator": "Creator",
        "logout": "Logout",
        "login": "Login",
        "signup": "Sign Up",

        # =================================================
        # GENERAL
        # =================================================

        "welcome": "Welcome",
        "continue": "Continue",
        "submit": "Submit",
        "save": "Save",
        "cancel": "Cancel",
        "back": "Back",
        "next": "Next",
        "done": "Done",
        "close": "Close",
        "view": "View",
        "learn_more": "Learn More",
        "no_data": "Not enough data yet.",
        "loading": "Loading...",
        "optional": "Optional",
        "required": "Required",

        # =================================================
        # DASHBOARD
        # =================================================

        "rationalmind": "RATIONALMIND",

        "dashboard_eyebrow":
            "YOUR MENTAL SPACE",

        "dashboard_title":
            "Build awareness.<br>Make intentional choices.",

        "dashboard_description":
            "Your mind is shaped by your thoughts, emotions, and decisions. "
            "RationalMind helps you understand those patterns and respond "
            "with clarity.",

        "what_is_rationalmind":
            "WHAT IS RATIONALMIND?",

        "rationalmind_heading":
            "Think clearly. Understand yourself. Choose intentionally.",

        "rationalmind_description":
            "RationalMind is a personal reflection and decision-making "
            "tool designed to help you examine your thoughts, understand "
            "your emotions, and approach important choices with greater "
            "awareness.",

        "reflect":
            "Reflect",

        "reflect_description":
            "Understand your experiences, emotions, thoughts, and reactions.",

        "reason":
            "Reason",

        "reason_description":
            "Separate facts from assumptions and consider different perspectives.",

        "decide":
            "Decide",

        "decide_description":
            "Compare options, consider tradeoffs, and make choices aligned "
            "with your goals.",

        "rationalmind_principle_short":
            "RationalMind isn't about having perfect answers. "
            "It's about developing a better understanding of how you think.",

        "personal_insight":
            "PERSONAL INSIGHT",

        "awareness_creates_change":
            "Awareness creates change.",

        "reflection_completed":
            "reflection exercises completed.",

        "most_frequent_emotion":
            "Your most frequent emotional state is:",

        "observe_patterns":
            "Continue observing patterns instead of judging them.",

        "your_journey":
            "YOUR JOURNEY",

        "growth_dashboard":
            "Growth Dashboard",

        "growth_description":
            "Track your reflections and build awareness of your thoughts, "
            "emotions, and decisions.",

        "reflections_completed":
            "Reflections Completed",

        "entries_recorded":
            "Entries Recorded",

        "latest_reflection":
            "LATEST REFLECTION",

        "insight":
            "Insight",

        "todays_practice":
            "Today's Practice",

        "todays_practice_description":
            "Choose one activity to strengthen your awareness.",

        "reflect_on_thoughts":
            "Reflect on your thoughts",

        "reset_attention":
            "Reset your attention",

        "analyze_decision":
            "Analyze a decision",

        "recent_reflections":
            "Recent Reflections",

        "complete_first_reflection":
            "Complete your first reflection to begin tracking your growth.",

        "your_privacy":
            "YOUR PRIVACY",

        "privacy_title":
            "Your information stays personal.",

        "privacy_description_1":
            "The personal information you enter into RationalMind, "
            "including your reflections, thoughts, decisions, history, "
            "and other written responses, is not visible to me as "
            "the creator.",

        "privacy_description_2":
            "I can only access limited, anonymous information used "
            "to understand how the app is being used, such as general "
            "emotional patterns and intensity data. Your personal "
            "entries are not available for me to read.",

        "rationalmind_principle":
            "The RationalMind Principle",

        "principle_description":
            "You cannot control every event, but you can improve how "
            "you understand and respond to those events.",

        # =================================================
        # REFLECTION
        # =================================================

        "reflection_title":
            "Reflection",

        "reflection_description":
            "Take a moment to examine your experience before deciding "
            "how to respond.",

        "situation":
            "Situation",

        "situation_prompt":
            "What happened?",

        "emotion":
            "Emotion",

        "emotion_prompt":
            "What emotion are you experiencing?",

        "emotion_direction":
            "Emotion Direction",

        "negative":
            "Negative",

        "positive":
            "Positive",

        "intensity":
            "Emotional Intensity",

        "intensity_prompt":
            "How intense is this emotion?",

        "thought":
            "Thought",

        "thought_prompt":
            "What thoughts are going through your mind?",

        "evidence":
            "Evidence",

        "supporting_evidence":
            "What evidence supports your interpretation?",

        "challenging_evidence":
            "What evidence challenges your interpretation?",

        "alternative":
            "Alternative Perspective",

        "alternative_prompt":
            "What is another way to view this situation?",

        "response":
            "Response",

        "response_prompt":
            "How would you like to respond?",

        "insights":
            "Insights",

        "insights_prompt":
            "What did you learn from this reflection?",

        "complete_reflection":
            "Complete Reflection",

        "feedback_required":
            "Please complete feedback for your previous reflection "
            "before starting another reflection.",

        "select_intensity":
            "Please select an emotion intensity.",

        "select_direction":
            "Please select whether the emotion is negative or positive.",

        "negative_intensity_error":
            "A negative emotion must have an intensity between -5 and -1.",

        "positive_intensity_error":
            "A positive emotion must have an intensity between +1 and +5.",

        # =================================================
        # DECISIONS
        # =================================================

        "decision_title":
            "Rational Decision",

        "decision_description":
            "Slow down, examine the evidence, and make a deliberate choice.",

        "goal":
            "Goal",

        "facts":
            "Facts",

        "assumptions":
            "Assumptions",

        "option_a":
            "Option A",

        "option_b":
            "Option B",

        "benefits":
            "Benefits",

        "drawbacks":
            "Drawbacks",

        "short_term":
            "Short-Term Consequences",

        "long_term":
            "Long-Term Consequences",

        "decision_choice":
            "Decision",

        "reasoning":
            "Reasoning",

        "analyze_decision":
            "Analyze Decision",

        # =================================================
        # HISTORY
        # =================================================

        "reflection_history":
            "Reflection History",

        "decision_history":
            "Decision History",

        "no_reflections":
            "You haven't completed any reflections yet.",

        "no_decisions":
            "You haven't recorded any decisions yet.",

        "date":
            "Date",

        # =================================================
        # FEEDBACK
        # =================================================

        "feedback_title":
            "Feedback",

        "feedback_description":
            "Reflect on how the experience affected you.",

        "feedback_responses":
            "Feedback Responses",

        "rating":
            "Rating",

        "comment":
            "Comment",

        "comment_optional":
            "Comment (Optional)",

        "after_emotion":
            "Emotion After",

        "after_intensity":
            "Intensity After",

        "other":
            "Other",

        "submit_feedback":
            "Submit Feedback",

        "feedback_submitted":
            "Thank you. Your feedback has been submitted.",

        "already_submitted":
            "You have already submitted feedback for your most recent "
            "reflection. Complete another reflection before submitting "
            "new feedback.",

        "feedback_no_reflection":
            "Please complete a reflection before submitting feedback.",

        "select_rating":
            "Please select a rating.",

        "select_emotion":
            "Please select or enter your emotion.",

        "select_emotional_intensity":
            "Please select your emotional intensity.",

        # =================================================
        # RESET
        # =================================================

        "reset_title":
            "Reset",

        "reset_description":
            "Take a moment to step away from the situation and reset "
            "your attention.",

        "reset_purpose":
            "The purpose of Reset is not to record another reflection. "
            "It is a short space to pause, breathe, and regain perspective.",

        "reset_no_submission":
            "There is no submission button because this exercise is "
            "designed for the moment itself rather than for creating "
            "another entry in your history.",

        # =================================================
        # EXPLORE
        # =================================================

        "explore_title":
            "Explore",

        "explore_description":
            "Explore ideas from psychology, philosophy, emotional "
            "intelligence, decision science, and rational thinking.",

        "emotional_intelligence":
            "Emotional Intelligence",

        "psychology":
            "Psychology",

        "philosophy":
            "Philosophy",

        "decision_science":
            "Decision Science",

        "rational_thinking":
            "Rational Thinking",

        "reflection_question":
            "Reflection Question",

        # =================================================
        # AUTHENTICATION
        # =================================================

        "username":
            "Username",

        "password":
            "Password",

        "create_account":
            "Create Account",

        "already_account":
            "Already have an account?",

        "no_account":
            "Don't have an account?",

        "incorrect_login":
            "Incorrect username or password.",

        "username_taken":
            "That username is already taken.",

        # =================================================
        # CREATOR
        # =================================================

        "creator_dashboard":
            "Creator Dashboard",

        "analytics":
            "Analytics",

        "overview":
            "Overview",

        "total_users":
            "Total Users",

        "total_reflections":
            "Total Reflections",

        "total_feedback":
            "Total Feedback",

        "average_rating":
            "Average Rating",

        "feedback_coverage":
            "Feedback Coverage",

        "feedback_rate":
            "Feedback Rate",

        "emotional_impact":
            "Emotional Impact",

        "before":
            "Before",

        "after":
            "After",

        "average_change":
            "Average Change",

        "improvement":
            "Improvement",

        "improvement_rate":
            "Improvement Rate",

        "improved":
            "Improved",

        "unchanged":
            "No Change",

        "worsened":
            "Worsened",

        "emotional_patterns":
            "Emotional Patterns",

        "emotion_transitions":
            "Emotion Transitions",

        "starting_emotion":
            "Most Common Starting Emotion",

        "ending_emotion":
            "Most Common Ending Emotion",

        "top_starting_emotions":
            "Top Starting Emotions",

        "top_ending_emotions":
            "Top Ending Emotions",

        "recent_feedback":
            "Recent Feedback",

        "growth_signal":
            "Growth Signal",

        "early_data":
            "Early Data",

        "encouraging":
            "Encouraging",

        "mixed_positive":
            "Mixed but Positive",

        "mixed":
            "Mixed",

        "privacy_data":
            "Privacy & Data",

        "anonymous_data":
            "Only limited, anonymous information is used for aggregate "
            "analysis. Personal reflections and written responses are "
            "not displayed here.",

        "insufficient_data":
            "Not enough data to calculate this yet.",

        # =================================================
        # SYSTEM
        # =================================================

        "not_found":
            "The requested page could not be found.",

        "error":
            "Something went wrong. Please try again.",

        "language":
            "Language",

    },


    # =====================================================
    # JAPANESE
    # =====================================================

    "ja": {

        # =================================================
        # NAVIGATION
        # =================================================

        "dashboard": "ダッシュボード",
        "reflection": "振り返り",
        "decisions": "意思決定",
        "history": "履歴",
        "explore": "学ぶ",
        "reset": "リセット",
        "feedback": "フィードバック",
        "creator": "クリエイター",
        "logout": "ログアウト",
        "login": "ログイン",
        "signup": "新規登録",

        # =================================================
        # GENERAL
        # =================================================

        "welcome": "ようこそ",
        "continue": "続ける",
        "submit": "送信",
        "save": "保存",
        "cancel": "キャンセル",
        "back": "戻る",
        "next": "次へ",
        "done": "完了",
        "close": "閉じる",
        "view": "見る",
        "learn_more": "詳しく見る",
        "no_data": "まだ十分なデータがありません。",
        "loading": "読み込み中...",
        "optional": "任意",
        "required": "必須",

        # =================================================
        # DASHBOARD
        # =================================================

        "rationalmind": "RATIONALMIND",

        "dashboard_eyebrow":
            "あなたの心のスペース",

        "dashboard_title":
            "気づきを深める。<br>意識的に選択する。",

        "dashboard_description":
            "あなたの心は、考え、感情、そして意思決定によって形作られています。"
            "RationalMindは、そのパターンを理解し、より明確に行動するためのサポートをします。",

        "what_is_rationalmind":
            "RATIONALMINDとは？",

        "rationalmind_heading":
            "明確に考える。自分を理解する。意識的に選択する。",

        "rationalmind_description":
            "RationalMindは、自分の考えや感情を振り返り、重要な選択について、"
            "より深い気づきを持って考えるためのツールです。",

        "reflect":
            "振り返る",

        "reflect_description":
            "自分の経験、感情、考え、反応を理解します。",

        "reason":
            "考える",

        "reason_description":
            "事実と推測を分け、さまざまな視点から考えます。",

        "decide":
            "選択する",

        "decide_description":
            "選択肢やメリット・デメリットを比較し、目標に沿った選択をします。",

        "rationalmind_principle_short":
            "RationalMindは、完璧な答えを見つけるためのものではありません。"
            "自分がどのように考えているのかを、より深く理解するためのものです。",

        "personal_insight":
            "あなたへの気づき",

        "awareness_creates_change":
            "気づきが変化を生み出します。",

        "reflection_completed":
            "回の振り返りを完了しました。",

        "most_frequent_emotion":
            "最も多かった感情は：",

        "observe_patterns":
            "感情を判断するのではなく、パターンを観察し続けてみましょう。",

        "your_journey":
            "あなたの歩み",

        "growth_dashboard":
            "成長ダッシュボード",

        "growth_description":
            "振り返りを記録し、自分の考え、感情、意思決定への理解を深めましょう。",

        "reflections_completed":
            "完了した振り返り",

        "entries_recorded":
            "記録されたエントリー",

        "latest_reflection":
            "最新の振り返り",

        "insight":
            "気づき",

        "todays_practice":
            "今日の実践",

        "todays_practice_description":
            "気づきを深めるための活動を一つ選びましょう。",

        "reflect_on_thoughts":
            "自分の考えを振り返る",

        "reset_attention":
            "注意をリセットする",

        "analyze_decision":
            "意思決定を分析する",

        "recent_reflections":
            "最近の振り返り",

        "complete_first_reflection":
            "最初の振り返りを完了すると、自分の成長を記録できるようになります。",

        "your_privacy":
            "あなたのプライバシー",

        "privacy_title":
            "あなたの情報は個人的なものとして守られます。",

        "privacy_description_1":
            "RationalMindに入力した個人的な情報、振り返り、考え、意思決定、履歴、"
            "その他の文章による回答は、クリエイターである私から見ることはできません。",

        "privacy_description_2":
            "私は、アプリの利用状況を理解するために必要な、感情の傾向や強さなどの"
            "限定された匿名データのみを確認できます。あなたの個人的な記録を読むことはできません。",

        "rationalmind_principle":
            "RationalMindの原則",

        "principle_description":
            "すべての出来事をコントロールすることはできません。"
            "しかし、その出来事をどのように理解し、どう反応するかは改善できます。",

        # =================================================
        # REFLECTION
        # =================================================

        "reflection_title":
            "振り返り",

        "reflection_description":
            "どのように対応するかを決める前に、自分の経験について少し立ち止まって考えてみましょう。",

        "situation":
            "状況",

        "situation_prompt":
            "何が起こりましたか？",

        "emotion":
            "感情",

        "emotion_prompt":
            "今、どのような感情を感じていますか？",

        "emotion_direction":
            "感情の方向",

        "negative":
            "ネガティブ",

        "positive":
            "ポジティブ",

        "intensity":
            "感情の強さ",

        "intensity_prompt":
            "この感情はどのくらい強いですか？",

        "thought":
            "考え",

        "thought_prompt":
            "今、どのようなことを考えていますか？",

        "evidence":
            "根拠",

        "supporting_evidence":
            "あなたの解釈を支持する根拠は何ですか？",

        "challenging_evidence":
            "あなたの解釈に疑問を投げかける根拠は何ですか？",

        "alternative":
            "別の視点",

        "alternative_prompt":
            "この状況を別の方法で見るとしたら、どう考えられますか？",

        "response":
            "対応",

        "response_prompt":
            "あなたはどのように対応したいですか？",

        "insights":
            "気づき",

        "insights_prompt":
            "この振り返りから何を学びましたか？",

        "complete_reflection":
            "振り返りを完了する",

        "feedback_required":
            "新しい振り返りを始める前に、前回の振り返りについてフィードバックを送信してください。",

        "select_intensity":
            "感情の強さを選択してください。",

        "select_direction":
            "感情がネガティブかポジティブかを選択してください。",

        "negative_intensity_error":
            "ネガティブな感情の強さは -5 から -1 の範囲で指定してください。",

        "positive_intensity_error":
            "ポジティブな感情の強さは +1 から +5 の範囲で指定してください。",

        # =================================================
        # DECISIONS
        # =================================================

        "decision_title":
            "合理的な意思決定",

        "decision_description":
            "一度立ち止まり、根拠を確認し、意識的に選択しましょう。",

        "goal":
            "目標",

        "facts":
            "事実",

        "assumptions":
            "前提・推測",

        "option_a":
            "選択肢A",

        "option_b":
            "選択肢B",

        "benefits":
            "メリット",

        "drawbacks":
            "デメリット",

        "short_term":
            "短期的な結果",

        "long_term":
            "長期的な結果",

        "decision_choice":
            "決定",

        "reasoning":
            "理由",

        "analyze_decision":
            "意思決定を分析する",

        # =================================================
        # HISTORY
        # =================================================

        "reflection_history":
            "振り返り履歴",

        "decision_history":
            "意思決定履歴",

        "no_reflections":
            "まだ振り返りを完了していません。",

        "no_decisions":
            "まだ意思決定を記録していません。",

        "date":
            "日付",

        # =================================================
        # FEEDBACK
        # =================================================

        "feedback_title":
            "フィードバック",

        "feedback_description":
            "この体験があなたにどのような影響を与えたか振り返ってみましょう。",

        "feedback_responses":
            "フィードバック回答",

        "rating":
            "評価",

        "comment":
            "コメント",

        "comment_optional":
            "コメント（任意）",

        "after_emotion":
            "振り返り後の感情",

        "after_intensity":
            "振り返り後の感情の強さ",

        "other":
            "その他",

        "submit_feedback":
            "フィードバックを送信",

        "feedback_submitted":
            "ありがとうございます。フィードバックが送信されました。",

        "already_submitted":
            "最新の振り返りについては、すでにフィードバックを送信しています。"
            "新しい振り返りを完了すると、次のフィードバックを送信できます。",

        "feedback_no_reflection":
            "フィードバックを送信する前に、振り返りを完了してください。",

        "select_rating":
            "評価を選択してください。",

        "select_emotion":
            "感情を選択または入力してください。",

        "select_emotional_intensity":
            "感情の強さを選択してください。",

        # =================================================
        # RESET
        # =================================================

        "reset_title":
            "リセット",

        "reset_description":
            "少しの間、状況から離れて注意をリセットしましょう。",

        "reset_purpose":
            "リセットは、新しい振り返りを記録するためのものではありません。"
            "立ち止まり、呼吸し、視点を取り戻すための短い時間です。",

        "reset_no_submission":
            "この機能には送信ボタンがありません。この時間は履歴に新しい記録を残すためではなく、"
            "その瞬間に立ち止まるためのものだからです。",

        # =================================================
        # EXPLORE
        # =================================================

        "explore_title":
            "学ぶ",

        "explore_description":
            "心理学、哲学、感情知能、意思決定科学、合理的思考について学びましょう。",

        "emotional_intelligence":
            "感情知能",

        "psychology":
            "心理学",

        "philosophy":
            "哲学",

        "decision_science":
            "意思決定科学",

        "rational_thinking":
            "合理的思考",

        "reflection_question":
            "振り返りの質問",

        # =================================================
        # AUTHENTICATION
        # =================================================

        "username":
            "ユーザー名",

        "password":
            "パスワード",

        "create_account":
            "アカウントを作成",

        "already_account":
            "すでにアカウントをお持ちですか？",

        "no_account":
            "アカウントをお持ちではありませんか？",

        "incorrect_login":
            "ユーザー名またはパスワードが正しくありません。",

        "username_taken":
            "そのユーザー名はすでに使用されています。",

        # =================================================
        # CREATOR
        # =================================================

        "creator_dashboard":
            "クリエイターダッシュボード",

        "analytics":
            "分析",

        "overview":
            "概要",

        "total_users":
            "総ユーザー数",

        "total_reflections":
            "総振り返り数",

        "total_feedback":
            "総フィードバック数",

        "average_rating":
            "平均評価",

        "feedback_coverage":
            "フィードバック取得率",

        "feedback_rate":
            "フィードバック率",

        "emotional_impact":
            "感情への影響",

        "before":
            "前",

        "after":
            "後",

        "average_change":
            "平均変化",

        "improvement":
            "改善",

        "improvement_rate":
            "改善率",

        "improved":
            "改善",

        "unchanged":
            "変化なし",

        "worsened":
            "悪化",

        "emotional_patterns":
            "感情パターン",

        "emotion_transitions":
            "感情の変化",

        "starting_emotion":
            "最も多かった開始時の感情",

        "ending_emotion":
            "最も多かった終了時の感情",

        "top_starting_emotions":
            "主な開始時の感情",

        "top_ending_emotions":
            "主な終了時の感情",

        "recent_feedback":
            "最近のフィードバック",

        "growth_signal":
            "成長シグナル",

        "early_data":
            "初期データ",

        "encouraging":
            "良好な傾向",

        "mixed_positive":
            "混合的だがポジティブ",

        "mixed":
            "混合的",

        "privacy_data":
            "プライバシーとデータ",

        "anonymous_data":
            "集計分析には限定された匿名データのみが使用されます。"
            "個人的な振り返りや文章による回答はここには表示されません。",

        "insufficient_data":
            "まだ計算に十分なデータがありません。",

        # =================================================
        # SYSTEM
        # =================================================

        "not_found":
            "指定されたページが見つかりません。",

        "error":
            "問題が発生しました。もう一度お試しください。",

        "language":
            "言語",
    }
}
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

class HybridRow(dict):
    """A PostgreSQL row that supports both row["column"] and row[0]."""

    def __getitem__(self, key):
        if isinstance(key, int):
            return list(self.values())[key]
        return super().__getitem__(key)


def hybrid_row(cursor):

    if cursor.description is None:
        return lambda values: HybridRow()

    columns = [column.name for column in cursor.description]

    def make_row(values):

        data = dict(zip(columns, values))

        for key, value in data.items():

            if key == "created_at" and isinstance(value, datetime):

                data[key] = value.strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

        return HybridRow(data)

    return make_row


def get_db():
    connection = psycopg.connect(
        DATABASE_URL,
        row_factory=hybrid_row
    )
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
        "What information is this emotion providing%s"
    },

    {
        "category": "Emotional Intelligence",
        "title": "Emotional Regulation",
        "description":
        "Regulation does not mean eliminating emotions. It means creating enough space to respond intentionally.",
        "question":
        "How can I acknowledge this emotion without immediately reacting%s"
    },

    # Psychology

    {
        "category": "Psychology",
        "title": "Cognitive Biases",
        "description":
        "The human mind uses shortcuts to make decisions efficiently. These shortcuts can sometimes create inaccurate interpretations.",
        "question":
        "What assumptions might be influencing my perspective%s"
    },

    {
        "category": "Psychology",
        "title": "Cognitive Distortions",
        "description":
        "People sometimes develop inaccurate thinking patterns such as all-or-nothing thinking or overgeneralization.",
        "question":
        "Am I viewing this situation more negatively than the evidence suggests%s"
    },

    # Philosophy

    {
        "category": "Philosophy",
        "title": "Stoic Control",
        "description":
        "Stoicism emphasizes separating what we can control from what we cannot control.",
        "question":
        "What part of this situation is actually within my control%s"
    },

    {
        "category": "Philosophy",
        "title": "Identity and Growth",
        "description":
        "Personal development requires seeing yourself as adaptable rather than defined permanently by past experiences.",
        "question":
        "What type of person am I trying to become%s"
    },

    # Decision Science

    {
        "category": "Decision Science",
        "title": "Opportunity Cost",
        "description":
        "Every choice involves giving something else up. Understanding tradeoffs improves decision quality.",
        "question":
        "What am I choosing, and what am I sacrificing%s"
    },

    {
        "category": "Decision Science",
        "title": "Long-Term Thinking",
        "description":
        "Good decisions consider consequences beyond immediate rewards or emotions.",
        "question":
        "How will this decision affect my future self%s"
    },

    # Rational Thinking

    {
        "category": "Rational Thinking",
        "title": "Facts vs Interpretation",
        "description":
        "Events and our interpretations of events are different. Separating them improves clarity.",
        "question":
        "What happened, and what story did I create about it%s"
    }

]


# =========================================================
# APP
# =========================================================
app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "rationalmind_secret_key")

CREATOR_USERNAME = "Koki Wakita".strip().lower()

@app.context_processor
def inject_creator_status():
    username = session.get("username", "").strip().lower()

    return {
        "is_creator": username == CREATOR_USERNAME
    }
@app.context_processor
def inject_language():

    language = session.get(
        "language",
        "en"
    )

    if language not in TRANSLATIONS:
        language = "en"

    return {
        "language": language,
        "t": TRANSLATIONS[language]
    }
# =========================================================
# DATABASE
# =========================================================

def init_db():

    connection = get_db()

    try:

        # -----------------------------------------------------
        # USERS
        # -----------------------------------------------------

        connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
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
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
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
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
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
                id INTEGER GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
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
        # POSTGRESQL MIGRATION
        # -----------------------------------------------------

        connection.execute("""
            ALTER TABLE feedback
            ADD COLUMN IF NOT EXISTS reflection_id INTEGER
        """)

        connection.execute("""
            ALTER TABLE feedback
            ADD COLUMN IF NOT EXISTS after_emotion TEXT
        """)

        connection.execute("""
            ALTER TABLE feedback
            ADD COLUMN IF NOT EXISTS after_intensity INTEGER
        """)

        connection.commit()

    except Exception:
        connection.rollback()
        raise

    finally:
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

        connection = get_db()

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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        WHERE user_id = %s
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
            WHERE reflection_id = %s
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
            WHERE user_id = %s
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
                WHERE reflection_id = %s
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
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
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
        WHERE user_id = %s
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

    connection = get_db()

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
        WHERE user_id = %s
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
        WHERE user_id = %s
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
        WHERE user_id = %s
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
        WHERE user_id = %s
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

        connection = get_db()

        try:

            connection.execute(
                """
                INSERT INTO users
                (username, email, password)
                VALUES (%s, %s, %s)
                """,
                (
                    username,
                    username + "@rationalmind.local",
                    password
                )
            )

            connection.commit()

        except psycopg.IntegrityError:

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

        connection = get_db()

        user = connection.execute(
            """
            SELECT id, username
            FROM users
            WHERE username = %s
            AND password = %s
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
        WHERE user_id = %s
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
        WHERE user_id = %s
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
        WHERE user_id = %s
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
            WHERE reflection_id = %s
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
            VALUES (%s, %s, %s, %s, %s, %s)
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
        WHERE id = %s
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

    try:

        # =====================================================
        # CREATOR-ONLY ACCESS
        # =====================================================

        user = connection.execute(
            """
            SELECT username
            FROM users
            WHERE id = %s
            """,
            (session["user_id"],)
        ).fetchone()

        if not user:
            return redirect("/dashboard")

        if user["username"].strip().lower() != CREATOR_USERNAME:
            return redirect("/dashboard")


        # =====================================================
        # OVERVIEW
        # =====================================================

        total_users = connection.execute(
            """
            SELECT COUNT(*)
            FROM users
            """
        ).fetchone()[0]

        total_reflections = connection.execute(
            """
            SELECT COUNT(*)
            FROM reflections
            """
        ).fetchone()[0]

        total_feedback = connection.execute(
            """
            SELECT COUNT(*)
            FROM feedback
            """
        ).fetchone()[0]

        average_rating = connection.execute(
            """
            SELECT AVG(rating)
            FROM feedback
            """
        ).fetchone()[0]

        if average_rating is not None:
            average_rating = round(float(average_rating), 1)


        # =====================================================
        # FEEDBACK COVERAGE
        # =====================================================
        # Counts reflections that actually have feedback.
        # This prevents the percentage from becoming misleading
        # if old/duplicate data exists.

        feedback_reflections = connection.execute(
            """
            SELECT COUNT(DISTINCT reflection_id)
            FROM feedback
            WHERE reflection_id IS NOT NULL
            """
        ).fetchone()[0]

        feedback_rate = None

        if total_reflections > 0:

            feedback_rate = round(
                (
                    feedback_reflections
                    / total_reflections
                ) * 100
            )


        # =====================================================
        # VALID BEFORE / AFTER COMPARISONS
        # =====================================================

        comparison_rows = connection.execute(
            """
            SELECT
                f.id,
                r.emotion AS before_emotion,
                r.intensity AS before_intensity,
                f.after_emotion,
                f.after_intensity,
                f.rating,
                f.comment,
                f.created_at
            FROM feedback f
            JOIN reflections r
                ON r.id = f.reflection_id
            WHERE
                r.intensity IS NOT NULL
                AND f.after_intensity IS NOT NULL
            ORDER BY f.id DESC
            """
        ).fetchall()


        # =====================================================
        # OUTCOME COUNTS
        # =====================================================

        improved = 0
        unchanged = 0
        worsened = 0

        negative_before_values = []
        negative_after_values = []

        positive_before_values = []
        positive_after_values = []

        comparisons = []


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


            # -------------------------------------------------
            # NEGATIVE EMOTION
            # -------------------------------------------------

            if before < 0:

                negative_before_values.append(
                    abs(before)
                )

                negative_after_values.append(
                    abs(after)
                )

                change = (
                    abs(before)
                    - abs(after)
                )


            # -------------------------------------------------
            # POSITIVE EMOTION
            # -------------------------------------------------

            elif before > 0:

                positive_before_values.append(
                    before
                )

                positive_after_values.append(
                    after
                )

                change = (
                    after
                    - before
                )

            else:

                continue


            # -------------------------------------------------
            # CLASSIFY OUTCOME
            # -------------------------------------------------

            if change > 0:

                outcome = "Improved"
                improved += 1

            elif change == 0:

                outcome = "No change"
                unchanged += 1

            else:

                outcome = "Worsened"
                worsened += 1


            comparisons.append({

                "before_emotion":
                    row["before_emotion"],

                "after_emotion":
                    row["after_emotion"],

                "before":
                    before,

                "after":
                    after,

                "change":
                    change,

                "outcome":
                    outcome

            })


        # =====================================================
        # COMPARISON TOTAL
        # =====================================================

        total_comparisons = len(
            comparisons
        )


        # =====================================================
        # IMPROVEMENT RATE
        # =====================================================

        improvement_percentage = None

        if total_comparisons > 0:

            improvement_percentage = round(
                (
                    improved
                    / total_comparisons
                ) * 100
            )


        # =====================================================
        # NEGATIVE EMOTIONAL INTENSITY
        # =====================================================

        average_negative_before = None
        average_negative_after = None
        negative_change = None

        if negative_before_values:

            average_negative_before = round(
                sum(
                    negative_before_values
                )
                / len(
                    negative_before_values
                ),
                1
            )

            average_negative_after = round(
                sum(
                    negative_after_values
                )
                / len(
                    negative_after_values
                ),
                1
            )

            negative_change = round(
                average_negative_before
                - average_negative_after,
                1
            )


        # =====================================================
        # POSITIVE EMOTIONAL INTENSITY
        # =====================================================

        average_positive_before = None
        average_positive_after = None
        positive_change = None

        if positive_before_values:

            average_positive_before = round(
                sum(
                    positive_before_values
                )
                / len(
                    positive_before_values
                ),
                1
            )

            average_positive_after = round(
                sum(
                    positive_after_values
                )
                / len(
                    positive_after_values
                ),
                1
            )

            positive_change = round(
                average_positive_after
                - average_positive_before,
                1
            )


        # =====================================================
        # EMOTION TRANSITIONS
        # =====================================================

        transition_rows = connection.execute(
            """
            SELECT
                TRIM(r.emotion) AS before_emotion,
                TRIM(f.after_emotion) AS after_emotion,
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
                TRIM(r.emotion),
                TRIM(f.after_emotion)
            ORDER BY
                amount DESC
            LIMIT 10
            """
        ).fetchall()

        transitions = []

        for row in transition_rows:

            transitions.append({

                "before":
                    row["before_emotion"],

                "after":
                    row["after_emotion"],

                "amount":
                    row["amount"]

            })


        # =====================================================
        # MOST COMMON STARTING EMOTION
        # =====================================================

        starting_emotion = connection.execute(
            """
            SELECT
                TRIM(emotion) AS emotion,
                COUNT(*) AS amount
            FROM reflections
            WHERE
                emotion IS NOT NULL
                AND TRIM(emotion) != ''
            GROUP BY TRIM(emotion)
            ORDER BY amount DESC
            LIMIT 1
            """
        ).fetchone()


        # =====================================================
        # MOST COMMON ENDING EMOTION
        # =====================================================

        ending_emotion = connection.execute(
            """
            SELECT
                TRIM(after_emotion) AS emotion,
                COUNT(*) AS amount
            FROM feedback
            WHERE
                after_emotion IS NOT NULL
                AND TRIM(after_emotion) != ''
            GROUP BY TRIM(after_emotion)
            ORDER BY amount DESC
            LIMIT 1
            """
        ).fetchone()


        # =====================================================
        # TOP STARTING EMOTIONS
        # =====================================================

        starting_emotions = connection.execute(
            """
            SELECT
                TRIM(emotion) AS emotion,
                COUNT(*) AS amount
            FROM reflections
            WHERE
                emotion IS NOT NULL
                AND TRIM(emotion) != ''
            GROUP BY TRIM(emotion)
            ORDER BY amount DESC
            LIMIT 5
            """
        ).fetchall()


        # =====================================================
        # TOP ENDING EMOTIONS
        # =====================================================

        ending_emotions = connection.execute(
            """
            SELECT
                TRIM(after_emotion) AS emotion,
                COUNT(*) AS amount
            FROM feedback
            WHERE
                after_emotion IS NOT NULL
                AND TRIM(after_emotion) != ''
            GROUP BY TRIM(after_emotion)
            ORDER BY amount DESC
            LIMIT 5
            """
        ).fetchall()


        # =====================================================
        # RECENT FEEDBACK
        # =====================================================

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
            LIMIT 10
            """
        ).fetchall()


        # =====================================================
        # FORMAT TIMESTAMPS
        # =====================================================

        recent_feedback = []

        for item in recent_feedback_rows:

            feedback_data = dict(item)

            timestamp = feedback_data.get(
                "created_at"
            )

            if timestamp:

                try:

                    if isinstance(
                        timestamp,
                        datetime
                    ):

                        if timestamp.tzinfo is None:

                            timestamp = timestamp.replace(
                                tzinfo=timezone.utc
                            )

                    else:

                        timestamp = datetime.strptime(
                            str(timestamp),
                            "%Y-%m-%d %H:%M:%S"
                        ).replace(
                            tzinfo=timezone.utc
                        )

                    timestamp = timestamp.astimezone(
                        ZoneInfo("America/Chicago")
                    )

                    feedback_data["created_at"] = (
                        timestamp.strftime(
                            "%B %d, %Y at %I:%M %p"
                        )
                    )

                except (
                    ValueError,
                    TypeError
                ):

                    pass

            recent_feedback.append(
                feedback_data
            )


        # =====================================================
        # GROWTH SIGNAL
        # =====================================================

        if total_comparisons < 5:

            growth_signal = (
                "The dataset is still developing. "
                "Continue collecting reflections and feedback "
                "before drawing strong conclusions."
            )

            growth_level = "Early data"

        elif improvement_percentage >= 70:

            growth_signal = (
                "Most reported comparisons currently move "
                "in the intended direction. This is an "
                "encouraging descriptive pattern, although "
                "the data does not establish causation."
            )

            growth_level = "Encouraging"

        elif improvement_percentage >= 50:

            growth_signal = (
                "More reported comparisons currently improve "
                "than worsen. Continued data collection will "
                "help determine whether this pattern remains "
                "consistent."
            )

            growth_level = "Mixed but positive"

        else:

            growth_signal = (
                "Reported outcomes are currently mixed. "
                "More data is needed to determine whether "
                "a stable pattern exists."
            )

            growth_level = "Mixed"


        # =====================================================
        # RETURN DASHBOARD
        # =====================================================

        return render_template(

            "creator.html",

            # Overview
            total_users=total_users,
            total_reflections=total_reflections,
            total_feedback=total_feedback,
            average_rating=average_rating,

            # Coverage
            feedback_reflections=
                feedback_reflections,

            feedback_rate=
                feedback_rate,

            total_comparisons=
                total_comparisons,

            # Impact
            average_negative_before=
                average_negative_before,

            average_negative_after=
                average_negative_after,

            negative_change=
                negative_change,

            average_positive_before=
                average_positive_before,

            average_positive_after=
                average_positive_after,

            positive_change=
                positive_change,

            # Outcomes
            improved=improved,
            unchanged=unchanged,
            worsened=worsened,

            improvement_percentage=
                improvement_percentage,

            # Patterns
            transitions=transitions,

            starting_emotion=
                starting_emotion,

            ending_emotion=
                ending_emotion,

            starting_emotions=
                starting_emotions,

            ending_emotions=
                ending_emotions,

            # Feedback
            recent_feedback=
                recent_feedback,

            # Growth
            growth_signal=
                growth_signal,

            growth_level=
                growth_level

        )

    finally:

        connection.close()


# =========================================================
# LANGUAGE
# =========================================================

@app.route("/set-language/<language>")
def set_language(language):

    if language not in TRANSLATIONS:
        language = "en"

    session["language"] = language

    return redirect(
        request.referrer or "/"
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
