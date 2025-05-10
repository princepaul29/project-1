from sqlmodel import SQLModel, create_engine, Session

DATABASE_URL = "sqlite:///data/web_scraper.db" # TODO: Move to PostgreSQL
engine = create_engine(DATABASE_URL, echo=False, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine, expire_on_commit=False) as session:
        yield session
