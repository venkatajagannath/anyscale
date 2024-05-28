from ray import serve


@serve.deployment
class Hi:
    def __call__(self, *args) -> str:
        return "hi"
