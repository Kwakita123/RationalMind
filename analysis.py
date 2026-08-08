def analyze_reflection(emotion, thought, response):

    insights = []


    # Detect emotional intensity

    if emotion:

        emotion_lower = emotion.lower()

        if "stress" in emotion_lower or "anxiety" in emotion_lower:
            insights.append(
                "Your reflection shows signs of pressure or uncertainty."
            )


        if "angry" in emotion_lower or "frustrated" in emotion_lower:
            insights.append(
                "Consider whether your reaction is focused on the event or your interpretation of it."
            )


        if "sad" in emotion_lower or "disappointed" in emotion_lower:
            insights.append(
                "Try separating one outcome from your overall identity."
            )


    # Detect thinking patterns

    if thought:

        thought_lower = thought.lower()


        if "always" in thought_lower or "never" in thought_lower:
            insights.append(
                "Watch for extreme thinking patterns."
            )


        if "everyone" in thought_lower or "nobody" in thought_lower:
            insights.append(
                "Consider whether your conclusion is based on enough evidence."
            )


    # General insight

    if len(insights) == 0:

        insights.append(
            "Your reflection demonstrates awareness of your thoughts and emotions."
        )


    return insights