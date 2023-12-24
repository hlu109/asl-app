from .setup import create_app
from .db import db

import logging

logging.basicConfig(level=logging.DEBUG)

app = create_app()
# db.create_all(app=app)

# TODO: add custom deconstructor
db.session.commit()



if __name__ == "__main__":
    # TODO where can we put this in the file? bottom? 
    
    app.run(debug=True)
