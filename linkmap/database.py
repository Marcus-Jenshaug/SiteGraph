from sqlalchemy import create_engine, Column, Integer, String, Text, Float, Boolean
from sqlalchemy.orm import sessionmaker, declarative_base

Base = declarative_base()

class Page(Base):
    """
    Represents a crawled page (a node in the link graph).
    """
    __tablename__ = 'pages'
    id = Column(Integer, primary_key=True)
    url = Column(Text, unique=True, nullable=False)
    status_code = Column(Integer)
    content_type = Column(String(100))
    depth = Column(Integer, nullable=False)

    # --- Fields from KRAVSPEKK.md ---
    # Data collected during crawl
    canonical = Column(Text, nullable=True)
    title = Column(Text, nullable=True)
    h1 = Column(Text, nullable=True)
    language = Column(String(50), nullable=True)
    meta_robots = Column(String(255), nullable=True)
    load_ms = Column(Integer, nullable=True)
    size_bytes = Column(Integer, nullable=True)

    # Data computed during analysis phase
    in_degree = Column(Integer, nullable=True)
    out_degree = Column(Integer, nullable=True)
    pagerank = Column(Float, nullable=True)
    cluster = Column(String(255), nullable=True)
    reciprocity_ratio = Column(Float, nullable=True)
    orphan_status = Column(Boolean, nullable=True)

    def __repr__(self):
        return f"<Page(url='{self.url}', status_code={self.status_code})>"

class Edge(Base):
    """
    Represents a link between two pages (an edge in the link graph).
    """
    __tablename__ = 'edges'
    id = Column(Integer, primary_key=True)
    source_url = Column(Text, nullable=False)
    target_url = Column(Text, nullable=False)

    # --- Fields from KRAVSPEKK.md ---
    anchor_text = Column(Text, nullable=True)
    rel = Column(String(255), nullable=True)
    is_bidirectional = Column(Boolean, default=False, nullable=True)

    def __repr__(self):
        return f"<Edge(source='{self.source_url}', target='{self.target_url}')>"

def get_engine(db_path='crawl.db'):
    """
    Returns a SQLAlchemy engine for the given database path.
    """
    return create_engine(f'sqlite:///{db_path}')

def create_db_and_tables(engine):
    """
    Creates all tables defined in the Base metadata.
    """
    Base.metadata.create_all(engine)

def get_session(engine):
    """
    Creates and returns a new SQLAlchemy session.
    """
    Session = sessionmaker(bind=engine)
    return Session()
