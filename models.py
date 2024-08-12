class ContactMessage(db.Model):
    __tablename__ = 'ContactMessages'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    school = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    roles = db.Column(db.String(50), nullable=False)
    other_role = db.Column(db.String(100))
    age = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ContactMessage {self.id}>'
