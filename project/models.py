from . import db, ma
from flask_login import UserMixin

# Many-to-Many relationship tables with named foreign key constraints
competitor_events = db.Table('competitor_events',
    db.Column('Competitor_id', db.Integer, db.ForeignKey('competitor.id', name='fk_competitor_events_competitor_id'), primary_key=True),
    db.Column('Event_id', db.Integer, db.ForeignKey('event.id', name='fk_competitor_events_event_id'), primary_key=True)
)

competition_events = db.Table('competition_events',
    db.Column('Competition_id', db.Integer, db.ForeignKey('competition.id', name='fk_competition_events_competition_id'), primary_key=True),
    db.Column('Event_id', db.Integer, db.ForeignKey('event.id', name='fk_competition_events_event_id'), primary_key=True)
)

# class CompetitionEvent(db.Model):
#     __tablename__ = 'competition_events'
#     competition_id = db.Column(db.Integer, db.ForeignKey('competition.id', name='fk_competition_event_competition_id'), primary_key=True)
#     event_id = db.Column(db.Integer, db.ForeignKey('event.id', name='fk_competition_event_event_id'), primary_key=True)

round_competitors = db.Table('competitor_rounds',
    db.Column('Competitor_id', db.Integer, db.ForeignKey('competitor.id', name='fk_competitor_rounds_competitor_id'), primary_key=True),
    db.Column('Round_id', db.Integer, db.ForeignKey('round.id', name='fk_competitor_rounds_round_id'), primary_key=True)
)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class Competitor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id', name='fk_competitor_competition_id'), nullable=False)

    events = db.relationship('Event', secondary=competitor_events, backref=db.backref('competitors', lazy=True))

class Competition(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    events = db.relationship('Event', secondary=competition_events, backref=db.backref('competitions', lazy=True))

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    comp_format = db.Column(db.String(3))  # ao5/mo3

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    time_string = db.Column(db.String)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitor.id', name='fk_result_competitor_id'), nullable=False)
    round_id = db.Column(db.Integer, db.ForeignKey('round.id', name='fk_result_round_id'), nullable=False)

    competitor = db.relationship('Competitor', foreign_keys=[competitor_id], backref='result_competitor')

    def __init__(self, competitor_id, round_id, time_string):
        self.competitor_id = competitor_id
        self.round_id = round_id
        self.time_string = time_string
        self.time = self._parse_time_string(time_string)

    @staticmethod
    def _parse_time_string(time_string):
        # Implement the logic to parse the time_string into an integer time (milliseconds, seconds, etc.)
        # Example assuming time_string is in "mm:ss.SSS" format
        if time_string == "DNF":
            return 999999
        if time_string.find(':') != -1:
            minutes, seconds = map(str, time_string.split(':'))
            seconds, millis = map(int, seconds.split('.'))
            return (int(minutes) * 60000 + int(seconds) * 1000 + int(millis)*10)
        else:
            seconds, millis = map(int, time_string.split('.'))
            return (seconds * 1000 + millis*10)


class Average(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    avg = db.Column(db.Integer)
    avg_string = db.Column(db.String)
    best = db.Column(db.Integer)
    best_string = db.Column(db.String)
    first_id = db.Column(db.Integer, db.ForeignKey('result.id', name='fk_average_first_id'))
    second_id = db.Column(db.Integer, db.ForeignKey('result.id', name='fk_average_second_id'))
    third_id = db.Column(db.Integer, db.ForeignKey('result.id', name='fk_average_third_id'))
    fourth_id = db.Column(db.Integer, db.ForeignKey('result.id', name='fk_average_fourth_id'))
    fifth_id = db.Column(db.Integer, db.ForeignKey('result.id', name='fk_average_fifth_id'))
    round_id = db.Column(db.Integer, db.ForeignKey('round.id', name='fk_average_round_id'), nullable=False)
    competitor_id = db.Column(db.Integer, db.ForeignKey('competitor.id', name='fk_average_competitor_id'), nullable=False)

    competitor = db.relationship('Competitor', foreign_keys=[competitor_id], backref='average_competitor')
    first = db.relationship('Result', foreign_keys=[first_id], backref='average_first')
    second = db.relationship('Result', foreign_keys=[second_id], backref='average_second')
    third = db.relationship('Result', foreign_keys=[third_id], backref='average_third')
    fourth = db.relationship('Result', foreign_keys=[fourth_id], backref='average_fourth')
    fifth = db.relationship('Result', foreign_keys=[fifth_id], backref='average_fifth')

    def __init__(self, competitor_id, round_id):
        self.competitor_id = competitor_id
        self.round_id = round_id
        

    def append_results(self, result_ids):
        self.first_id, self.second_id, self.third_id, self.fourth_id, self.fifth_id = result_ids
        self._calculate_avg_and_best()

    def _calculate_avg_and_best(self):
        results = [Result.query.get(result_id) for result_id in 
                   [self.first_id, self.second_id, self.third_id, self.fourth_id, self.fifth_id]]
        times = [result.time for result in results if result]
        dnf_count = times.count(999999)
        print("caculating, dnf count:")
        print(dnf_count)
        if dnf_count > 1:
            self.best = min(times)
            self.best_string = self.time_to_string(self.best)
            self.avg = 999999
            self.avg_string = "DNF"

        elif times:
            self.best = min(times)
            self.best_string = self.time_to_string(self.best)
            worst = max(times)
            self.avg = (sum(times) - self.best - worst)/3
            self.avg_string = self.time_to_string(self.avg)
        else:
            self.best = None
            self.avg = None

    def time_to_string(self, time):
        minutes = int(time/60000)
        seconds = int((time - minutes*60000)/1000)
        millis = int(time%1000/10)
        print("in time to str:")
        print(minutes)
        print(seconds)
        print(millis)
        if minutes:
            return(f'{minutes}:{seconds}.{millis}')
        return(f'{seconds}.{millis}')


class Round(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer, nullable=False)
    advances = db.Column(db.String)
    event_id = db.Column(db.Integer, db.ForeignKey('event.id', name='fk_round_event_id'), nullable=False)
    competition_id = db.Column(db.Integer, db.ForeignKey('competition.id', name='fk_round_competition_id'), nullable=False)
    competitors = db.relationship('Competitor', secondary=round_competitors, backref=db.backref('rounds', lazy=True))

class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_relationships = True
        load_instance = True

event_schema = EventSchema()
events_schema = EventSchema(many=True)


class CompetitorSchema(ma.SQLAlchemyAutoSchema):
    events = ma.Nested(EventSchema, many=True)

    class Meta:
        model = Competitor
        include_relationships = True
        load_instance = True

competitor_schema = CompetitorSchema()
competitors_schema = CompetitorSchema(many=True)

class ResultSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Result
        include_relationships = True
        load_instance = True

result_schema = ResultSchema()
results_schema = ResultSchema(many=True)

class AverageSchema(ma.SQLAlchemyAutoSchema):
    competitor = ma.Nested(CompetitorSchema)
    first = ma.Nested(ResultSchema)
    second = ma.Nested(ResultSchema)
    third = ma.Nested(ResultSchema)
    fourth = ma.Nested(ResultSchema)
    fifth = ma.Nested(ResultSchema)
    class Meta:
        model = Average
        include_relationships = True
        load_instance = True

average_schema = AverageSchema()
averages_schema = AverageSchema(many=True)

class RoundSchema(ma.SQLAlchemyAutoSchema):
    competitors = ma.Nested(CompetitorSchema, many=True)

    class Meta:
        model = Round
        include_relationships = True
        load_instance = True

round_schema = RoundSchema()
rounds_schema = RoundSchema(many=True)

class CompetitionSchema(ma.SQLAlchemyAutoSchema):
    events = ma.Nested(EventSchema, many=True)

    class Meta:
        model = Competition
        include_relationships = True
        load_instance = True

competition_schema = CompetitionSchema()
competitions_schema = CompetitionSchema(many=True)
