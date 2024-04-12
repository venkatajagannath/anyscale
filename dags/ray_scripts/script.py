# script.py
import ray

@ray.remote
def hello_world():
    return "hello world"

print(ray.get(hello_world.remote()))