from flask import Blueprint, request, jsonify
from models import db, Comment
from utlis import fetch_youtube_comments, analyze_sentiment

bp = Blueprint("api", __name__)

@bp.route("/fetch-comments", methods=["POST"])
def fetch_comments():
    data = request.json
    video_id = data.get("video_id")
    
    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400
    
    comments = fetch_youtube_comments(video_id)
    for comment in comments:
        sentiment = analyze_sentiment(comment["comment_text"])
        masked_username = comment["username"][0] + "*" * (len(comment["username"]) - 1)

        new_comment = Comment(
            video_id=video_id,
            username=comment["username"],
            masked_username=masked_username,
            comment_text=comment["comment_text"],
            sentiment=sentiment
        )
        db.session.add(new_comment)
    
    db.session.commit()
    return jsonify({"message": "Comments fetched and analyzed"}), 200

@bp.route("/get-insights", methods=["GET"])
def get_insights():
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"error": "Missing video_id"}), 400

    comments = Comment.query.filter_by(video_id=video_id).all()
    total = len(comments)
    print(total)
    agreement = sum(1 for c in comments if c.sentiment == "Agree")
    disagreement = sum(1 for c in comments if c.sentiment == "Disagree")
    
    insights = {
        "total_comments": total,
        "agreement_percentage": (agreement / total) * 100 if total!=0 else 0,
        "disagreement_percentage": (disagreement / total) * 100 if total!=0 else 0,
    }
    print(insights)
    return jsonify(insights), 200


# @main_routes.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'POST':
#         text = request.form.get('text')
#         if not text:
#             flash('Please enter some text!', 'error')
#         else:
#             results = analyze_sentiment(text)
#             return render_template('results.html', results=results)
#     return render_template('index.html')

# @main_routes.route('/analyze', methods=['POST'])
# def analyze():
#     text = request.form.get('text')
#     results = analyze_sentiment(text)
#     return render_template('results.html', results=results)
