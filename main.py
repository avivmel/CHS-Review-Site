from flask import Flask
from flask import request


from flask_sqlalchemy import SQLAlchemy

from flask import render_template


class_dict = {0: "AP chem", 1: "AP CS", 2: "CP English", 3: "AP English", 4: "Applied Computer Science"}

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/database.db'
db = SQLAlchemy(app)


class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    class_id = db.Column(db.Integer, unique=False, nullable=False)
    rating = db.Column(db.Integer, unique=False, nullable=False)
    comment_text = db.Column(db.Text, unique=False, nullable=True)

    def __repr__(self):
        return f'{self.id} class_id:{self.class_id} rating:{self.rating} comment:"{self.comment_text}"'

@app.route('/review/add/<int:class_id>/<int:review>',  methods=["POST"])
def add_review(class_id, review):

    if class_id not in class_dict or (review < 1 or review > 5):
        return "Error"

    if request.method == 'POST':
        data = request.get_json()
        comment_text = data['comment_text']

    review = Review(class_id=class_id, rating=review, comment_text=comment_text)
    db.session.add(review)
    db.session.commit()

    return f'Post {class_id} {review}'


@app.route('/count/<int:class_id>/')
def count_reviews_ept(class_id):
    return_dict, average, total_reviews_count, comments = count_reviews(class_id)
    return return_dict


def count_reviews(class_id):

    if class_id not in class_dict:
        return "Error"

    return_dict = {"count":{}, "percent":{}}
    all_class_reviews = Review.query.filter(Review.class_id == class_id)

    comments = [x for x in all_class_reviews.all() if x.comment_text != ""]
    comments.reverse()

    total_reviews_count = len(all_class_reviews.all())

    if total_reviews_count == 0:
        for i in range(1, 6):
            return_dict["count"][i] = 0
            return_dict["percent"][i] = 0
        return return_dict, 0, 0, []


    total = 0
    for i in range(1,6):
        q = all_class_reviews.filter(Review.rating == i).all()
        return_dict["count"][i] = len(q)
        return_dict["percent"][i] = (len(q)/total_reviews_count)*100

        total += len(q)*i

    average_rating = round(total/total_reviews_count, 1)



    return return_dict, average_rating, total_reviews_count, comments

@app.route('/review/<int:class_id>')
def review(class_id):
    if class_id not in class_dict:
        return "404 Not Found"
    return_dict, average, total_reviews_count, comments = count_reviews(class_id)
    return render_template('review.html', class_id=class_id, class_name=class_dict[class_id], return_dict=return_dict, average=average, total_reviews_count=total_reviews_count, comments=comments)

@app.route('/')
def main():
    classes = []

    for key in class_dict:
        individual_class = {}
        individual_class['id'] = key
        individual_class['name'] = class_dict[key]

        return_dict, average, total_reviews_count, comments = count_reviews(key)
        individual_class['rating'] = average
        individual_class['total reviews'] = total_reviews_count


        classes.append(individual_class)


    return render_template('index.html', classes=classes)


if __name__ == "__main__":
    app.run(debug=True)