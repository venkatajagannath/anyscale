import argparse
import ray

def main(param1, param2, result):
    # Initialize Ray
    ray.init()

    # Simple Ray task
    @ray.remote
    def hello_world_task(param1, param2, result):
        return f"Hello, World! Param1: {param1}, Param2: {param2}, Result: {result}"

    # Run the Ray task
    hello_world = hello_world_task.remote(param1, param2, result)
    print(ray.get(hello_world))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simple Ray job example.")
    parser.add_argument("--param1", type=int, required=True, help="The first parameter.")
    parser.add_argument("--param2", type=int, required=True, help="The second parameter.")
    parser.add_argument("--result", type=int, required=True, help="The result parameter.")

    args = parser.parse_args()
    main(args.param1, args.param2, args.result)