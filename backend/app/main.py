import threading
from . import create_app
from .extensions import socketio
from .tasks import audio_processing_thread

from . import sockets 

if __name__ == '__main__':
    app = create_app()

    t = threading.Thread(target=audio_processing_thread, args=(app,), daemon=True)
    t.start()

    print("Server starting on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)