from pathlib import Path


class FileReceiver(object):
    def __init__(self, script, cwd):
        self.script = script
        self.session = None
        self.cwd = Path(cwd).resolve()
        self.fp = None
        self.size = 0

    def connect(self):
        self.script.on('message', self.on_message)

    def on_message(self, msg, data):
        if msg.get('type') != 'send':
            print('unknown message:', msg)
            return

        payload = msg.get('payload', {})
        subject = payload.get('subject')
        if subject == 'download':
            method_mapping = {
                'start': self.on_download_start,
                'data': self.on_download_data,
                'end': self.on_download_finish,
                'error': self.on_download_error,
                'mkdir': self.on_mkdir,
            }
            method = method_mapping[payload.get('event')]
            method(data=data, **payload)
        elif subject == 'finish':
            print('bye')
            # self.session.detach()
            # self.device.kill(self.app.pid)
            # sys.exit(0)
        else:
            print('unknown message')
            print(msg)

    def secure_path(self, relative) -> Path:
        abspath: Path = self.cwd / relative
        # try:
        abspath.resolve().relative_to(self.cwd)
        # except ValueError:
        #     print('[WARNING] possible path traversal: %s', relative)
        # else:
        return abspath

    def on_mkdir(self, relative, **kwargs):
        self.secure_path(relative).mkdir(parents=True)

    def on_download_start(self, session, relative, size, **kwargs):
        # print('start, session= %s', session)
        self.session = session
        self.fp = open(self.secure_path(relative), 'wb')
        self.size = size
        self.script.post({'type': 'ack'})

    def on_download_data(self, session, data, **kwargs):
        # print('data, session= %s', session)
        assert(self.session == session)
        self.fp.write(data)
        self.script.post({'type': 'flush'})

    def on_download_finish(self, session, **kwargs):
        self.close_session(session)

    def on_download_error(self, session, **kwargs):
        self.close_session(session)

    def close_session(self, session):
        self.fp.close()
        self.session = None
