# app.py

from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class DirectorSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class GenreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()


class MovieSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    director_id = fields.Int()
    genre_id = fields.Int()

movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = DirectorSchema()
genres_schema = DirectorSchema(many=True)

api = Api(app)
movies_ns = api.namespace('movies')
director_ns = api.namespace('directors')
genre_ns = api.namespace('genre')

@movies_ns.route("/")
class MoviesView(Resource):

    def get(self):
        director = request.args.get("director_id")
        genre = request.args.get("genre_id")

        if director and genre is not None:
            movies = Movie.query.filter(Movie.director_id == director).filter(Movie.genre_id == genre)
        elif genre is not None:
            movies = Movie.query.filter(Movie.genre_id == genre)
        elif director is not None:
            movies = Movie.query.filter(Movie.director_id == director)
        else:
            movies = db.session.query(Movie).all()
        return movies_schema.dump(movies), 200

    def post(self):
        movie_data = request.json
        new_movie = Movie(**movie_data)

        with db.session.begin():
            db.session.add(new_movie)
        return "ADD", 201


@movies_ns.route("/<int:uid>")
class MovieView(Resource):

    def get(self, uid: int):
        movie = Movie.query.get(uid)
        return movie_schema.dump(movie), 200

    def put(self, uid: int):
        update_rows = db.session.query(Movie).filter(Movie.id == uid).update(request.json)

        if update_rows != 1:
            return "Not found", 400
        db.session.commit()
        return "Updated", 204

    def delete(self, uid: int):
        movie = Movie.query.get(uid)
        db.session.delete(movie)
        db.session.commit()
        return "Delete", 204


@director_ns.route("/")
class DirectorView(Resource):

    def get(self):
        movie = Director.query.all()
        return directors_schema.dump(movie), 200

    def post(self):
        director_data = request.json
        new_director = Director(**director_data)
        with db.session.begin():
            db.session.add(new_director)
        return "ADD", 201


@director_ns.route("/<int:uid>")
class DirectorView(Resource):

    def get(self, uid: int):
        director = Director.query.get(uid)
        return director_schema.dump(director), 200

    def put(self, uid: int):
        director = Director.query.get(uid)
        director_data = request.json
        director.name = director_data.get("name")
        db.session.add(director)
        db.session.commit()
        return "Update", 204

    def delete(self, uid: int):
        director = Director.query.get(uid)
        db.session.delete(director)
        db.session.commit()
        return "Delete", 204


@genre_ns.route("/")
class GenreView(Resource):


    def get(self):
        genres_all = Genre.query.all()
        return genres_schema.dump(genres_all), 200

    def post(self):
        genre_data = request.json
        new_genre = Genre(**genre_data)
        with db.session.begin():
            db.session.add(new_genre)
        return "ADD", 201


@genre_ns.route("/<int:uid>")
class GenreView(Resource):


    def get(self, uid: int):
        movie = Genre.query.get(uid)
        return genre_schema.dump(movie), 200

    def put(self, uid: int):
        genre = Genre.query.get(uid)
        genre_data = request.json
        genre.name = genre_data.get("name")
        db.session.add(genre)
        db.session.commit()
        return "Update", 204

    def delete(self, uid: int):
        genre = Genre.query.get(uid)
        db.session.delete(genre)
        db.session.commit()
        return "Delete", 204

if __name__ == '__main__':
    app.run(debug=True)
