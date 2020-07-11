class BaseClient:
    def send_message(self, text=None, urls=None):
        pass

    @staticmethod
    def get_client_name():
        pass

    def is_threadable(self) -> bool:
        pass

    def run_client(self, *args):
        pass

    def get_run_args(self):
        pass

