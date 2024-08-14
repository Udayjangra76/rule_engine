from flask_sqlalchemy import SQLAlchemy 


db = SQLAlchemy()
class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_string = db.Column(db.String, nullable=False)
    description = db.Column(db.String)

    def __repr__(self):
        return f"<Rule id={self.id} rule_string={self.rule_string}>"

class Evaluation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('rule.id'), nullable=False)
    data = db.Column(db.Text, nullable=False)
    result = db.Column(db.Boolean, nullable=False)

    rule = db.relationship('Rule', backref=db.backref('evaluations', lazy=True))
    
    def __repr__(self):
        return f"<Evaluation id={self.id} rule_id={self.rule_id} result={self.result}>"
