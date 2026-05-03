# Adapte l'import selon l'endroit où se trouve ton 'engine'
from app.database import engine
from app.models import Base

print("Création des tables manquantes...")
# Cette ligne va créer User et UserBet sans toucher au reste
Base.metadata.create_all(bind=engine)
print("Terminé !")