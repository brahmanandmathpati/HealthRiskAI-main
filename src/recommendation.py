def give_recommendation(glucose, bmi):

    suggestions = []

    if glucose > 140:
        suggestions.append("Reduce sugar intake 🍭")
        suggestions.append("Avoid sweets & soft drinks")

    if bmi > 25:
        suggestions.append("Start daily exercise 🏃")
        suggestions.append("Eat healthy food 🥗")

    if not suggestions:
        suggestions.append("You are healthy! Maintain lifestyle 👍")

    return suggestions
def heart_recommendation(chol, bp, maxhr):
    recs = []

    if chol > 240:
        recs.append("Reduce cholesterol intake (avoid oily food)")

    if bp > 140:
        recs.append("Control blood pressure with diet & exercise")

    if maxhr < 120:
        recs.append("Improve cardiovascular fitness (walking, jogging)")

    if not recs:
        recs.append("Maintain healthy lifestyle 👍")

    return recs