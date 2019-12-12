import os
import tempfile

temp_ddbb = tempfile.mkstemp()[1]

os.environ['PYDO_DATABASE_URL'] = 'sqlite:///{}'.format(temp_ddbb)
