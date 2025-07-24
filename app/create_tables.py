from core.database import Base, engine
import models  # models/__init__.py에서 모든 모델 import됨

Base.metadata.create_all(bind=engine)
