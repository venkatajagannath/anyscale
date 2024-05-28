import ray


@ray.remote
def f():
    print("Hi!")


ray.get(f.remote())
