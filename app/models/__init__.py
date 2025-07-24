from app.models.user import User
from app.models.animal import Animal
# __init__.py로 인해 models 외부에서 from models.animal.animalModel import Animal 가 아닌 from models import Animal와 같이 접근 가능